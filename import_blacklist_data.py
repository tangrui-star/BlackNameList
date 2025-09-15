#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导入补充黑名单数据到数据库
"""

import sys
import os
import pandas as pd
import re
from datetime import datetime
from decimal import Decimal

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'blacklist-backend'))

from app.core.database import get_db
from app.models.blacklist import Blacklist
from app.models.user import RiskLevel
from sqlalchemy.orm import Session
from app.core.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def extract_phone_numbers(text):
    """从文本中提取电话号码"""
    if pd.isna(text) or not text:
        return []
    
    # 电话号码正则表达式
    phone_pattern = r'1[3-9]\d{9}'
    phones = re.findall(phone_pattern, str(text))
    return phones

def determine_risk_level(reason):
    """根据入黑名单原因确定风险等级"""
    if pd.isna(reason) or not reason:
        return RiskLevel.MEDIUM
    
    reason_lower = str(reason).lower()
    
    # 高风险关键词
    high_risk_keywords = ['制造异物', '事精', '反手举报', '恶意', '诈骗', '欺诈']
    if any(keyword in reason_lower for keyword in high_risk_keywords):
        return RiskLevel.HIGH
    
    # 低风险关键词
    low_risk_keywords = ['退款', '补发', '收货', '待观察']
    if any(keyword in reason_lower for keyword in low_risk_keywords):
        return RiskLevel.LOW
    
    # 默认中等风险
    return RiskLevel.MEDIUM

def generate_new_id(db: Session):
    """生成新的10位唯一ID"""
    # 获取当前最大的ID
    max_blacklist = db.query(Blacklist).order_by(Blacklist.id.desc()).first()
    if max_blacklist and max_blacklist.new_id:
        try:
            current_max = int(max_blacklist.new_id)
            return str(current_max + 1).zfill(10)
        except ValueError:
            pass
    
    # 如果没有现有ID，从1开始
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
                existing = db.query(Blacklist).filter(
                    Blacklist.ktt_name == ktt_name,
                    Blacklist.order_name_phone == order_name_phone
                ).first()
                
                if existing:
                    print(f"  ⚠️  跳过：记录已存在 (ID: {existing.id})")
                    skipped_count += 1
                    continue
                
                # 确定风险等级
                risk_level = determine_risk_level(blacklist_reason)
                print(f"  🎯 风险等级: {risk_level.value}")
                
                # 生成新ID
                new_id = generate_new_id(db)
                print(f"  🆔 新ID: {new_id}")
                
                # 创建黑名单记录
                blacklist_record = Blacklist(
                    sequence_number=index + 1,
                    new_id=new_id,
                    ktt_name=ktt_name,
                    wechat_name=wechat_name,
                    wechat_id=wechat_id,
                    order_name_phone=order_name_phone,
                    phone_numbers=phone_numbers,
                    order_address1=order_address1,
                    order_address2=order_address2,
                    blacklist_reason=blacklist_reason,
                    risk_level=risk_level,
                    created_by=1,  # 假设管理员用户ID为1
                    is_active=True
                )
                
                db.add(blacklist_record)
                db.flush()  # 获取ID
                
                print(f"  ✅ 成功创建黑名单记录 (ID: {blacklist_record.id})")
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
        total_blacklist = db.query(Blacklist).filter(Blacklist.is_active == True).count()
        print(f"\n📊 数据库黑名单总数: {total_blacklist}")
        
        # 按风险等级统计
        risk_stats = db.query(Blacklist.risk_level, db.func.count(Blacklist.id)).filter(
            Blacklist.is_active == True
        ).group_by(Blacklist.risk_level).all()
        
        print(f"\n📈 风险等级统计:")
        for risk_level, count in risk_stats:
            print(f"  {risk_level.value}: {count} 条")
        
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    import_blacklist_data()
