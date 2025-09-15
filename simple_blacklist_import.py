#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版黑名单数据导入脚本
"""

import sys
import os
import pandas as pd
import re
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'blacklist-backend'))

from app.core.config import settings
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def extract_phone_numbers(text):
    """从文本中提取电话号码"""
    if pd.isna(text) or not text:
        return "[]"
    
    # 电话号码正则表达式
    phone_pattern = r'1[3-9]\d{9}'
    phones = re.findall(phone_pattern, str(text))
    import json
    return json.dumps(phones, ensure_ascii=False)

def determine_risk_level(reason):
    """根据入黑名单原因确定风险等级"""
    if pd.isna(reason) or not reason:
        return "medium"
    
    reason_lower = str(reason).lower()
    
    # 高风险关键词
    high_risk_keywords = ['制造异物', '事精', '反手举报', '恶意', '诈骗', '欺诈']
    if any(keyword in reason_lower for keyword in high_risk_keywords):
        return "high"
    
    # 低风险关键词
    low_risk_keywords = ['退款', '补发', '收货', '待观察']
    if any(keyword in reason_lower for keyword in low_risk_keywords):
        return "low"
    
    # 默认中等风险
    return "medium"

def get_next_sequence_number(db):
    """获取下一个序号"""
    result = db.execute(text("SELECT MAX(sequence_number) FROM blacklist")).fetchone()
    if result and result[0]:
        return result[0] + 1
    return 1

def generate_new_id(db):
    """生成新的10位唯一ID"""
    result = db.execute(text("SELECT MAX(CAST(new_id AS UNSIGNED)) FROM blacklist WHERE new_id REGEXP '^[0-9]+$'")).fetchone()
    if result and result[0]:
        return str(result[0] + 1).zfill(10)
    return "0000000001"

def import_blacklist_data():
    """导入黑名单数据"""
    excel_file = "补充黑名单.xlsx"
    
    if not os.path.exists(excel_file):
        print(f"❌ 文件不存在: {excel_file}")
        return
    
    try:
        # 读取Excel文件
        print(f"📊 开始导入黑名单数据...")
        print("=" * 60)
        
        df = pd.read_excel(excel_file, sheet_name='Sheet1')
        print(f"📋 读取到 {len(df)} 条记录")
        
        # 创建数据库连接
        engine = create_engine(settings.database_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        imported_count = 0
        skipped_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                print(f"\n🔍 处理第 {index + 1} 条记录...")
                
                # 提取数据
                ktt_name = str(row['ktt名字']).strip() if pd.notna(row['ktt名字']) else ""
                wechat_name = str(row['微信名字']).strip() if pd.notna(row['微信名字']) else None
                wechat_id = str(row['微信号']).strip() if pd.notna(row['微信号']) else None
                order_name_phone = str(row['下单名字和电话']).strip() if pd.notna(row['下单名字和电话']) else ""
                order_address1 = str(row['下单地址1']).strip() if pd.notna(row['下单地址1']) else ""
                order_address2 = str(row['下单地址2']).strip() if pd.notna(row['下单地址2']) else None
                blacklist_reason = str(row['入黑名单原因']).strip() if pd.notna(row['入黑名单原因']) else None
                
                # 验证必填字段
                if not ktt_name or not order_name_phone or not order_address1:
                    print(f"  ⚠️  跳过：缺少必填字段")
                    skipped_count += 1
                    continue
                
                # 提取电话号码
                phone_numbers = extract_phone_numbers(order_name_phone)
                print(f"  📞 提取到电话号码: {phone_numbers}")
                
                # 检查是否已存在相同的记录
                existing = db.execute(text("""
                    SELECT id FROM blacklist 
                    WHERE ktt_name = :ktt_name AND order_name_phone = :order_name_phone
                """), {
                    'ktt_name': ktt_name,
                    'order_name_phone': order_name_phone
                }).fetchone()
                
                if existing:
                    print(f"  ⚠️  跳过：记录已存在 (ID: {existing[0]})")
                    skipped_count += 1
                    continue
                
                # 确定风险等级
                risk_level = determine_risk_level(blacklist_reason)
                print(f"  🎯 风险等级: {risk_level}")
                
                # 生成新ID和序号
                new_id = generate_new_id(db)
                sequence_number = get_next_sequence_number(db)
                print(f"  🆔 新ID: {new_id}, 序号: {sequence_number}")
                
                # 插入黑名单记录
                insert_sql = text("""
                    INSERT INTO blacklist (
                        sequence_number, new_id, ktt_name, wechat_name, wechat_id,
                        order_name_phone, phone_numbers, order_address1, order_address2,
                        blacklist_reason, risk_level, created_by, is_active, created_at, updated_at
                    ) VALUES (
                        :sequence_number, :new_id, :ktt_name, :wechat_name, :wechat_id,
                        :order_name_phone, :phone_numbers, :order_address1, :order_address2,
                        :blacklist_reason, :risk_level, :created_by, :is_active, :created_at, :updated_at
                    )
                """)
                
                now = datetime.now()
                db.execute(insert_sql, {
                    'sequence_number': sequence_number,
                    'new_id': new_id,
                    'ktt_name': ktt_name,
                    'wechat_name': wechat_name,
                    'wechat_id': wechat_id,
                    'order_name_phone': order_name_phone,
                    'phone_numbers': phone_numbers,
                    'order_address1': order_address1,
                    'order_address2': order_address2,
                    'blacklist_reason': blacklist_reason,
                    'risk_level': risk_level,
                    'created_by': 4,  # 使用admin用户ID
                    'is_active': True,
                    'created_at': now,
                    'updated_at': now
                })
                
                print(f"  ✅ 成功创建黑名单记录")
                imported_count += 1
                
            except Exception as e:
                error_msg = f"第 {index + 1} 条记录处理失败: {str(e)}"
                print(f"  ❌ {error_msg}")
                errors.append(error_msg)
                continue
        
        # 提交事务
        db.commit()
        
        print(f"\n🎉 导入完成！")
        print(f"✅ 成功导入: {imported_count} 条")
        print(f"⚠️  跳过: {skipped_count} 条")
        print(f"❌ 错误: {len(errors)} 条")
        
        if errors:
            print(f"\n❌ 错误详情:")
            for error in errors:
                print(f"  - {error}")
        
        # 显示导入后的统计信息
        total_result = db.execute(text("SELECT COUNT(*) FROM blacklist WHERE is_active = 1")).fetchone()
        total_blacklist = total_result[0] if total_result else 0
        print(f"\n📊 数据库黑名单总数: {total_blacklist}")
        
        # 按风险等级统计
        risk_stats = db.execute(text("""
            SELECT risk_level, COUNT(*) 
            FROM blacklist 
            WHERE is_active = 1 
            GROUP BY risk_level
        """)).fetchall()
        
        print(f"\n📈 风险等级统计:")
        for risk_level, count in risk_stats:
            print(f"  {risk_level}: {count} 条")
        
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    import_blacklist_data()
