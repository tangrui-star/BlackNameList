#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清洗和整理Excel黑名单数据
基于分析结果对数据进行清洗、去重和标准化处理
"""

import pandas as pd
import re
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import numpy as np

def clean_text(text: Any) -> Optional[str]:
    """清理文本数据"""
    if pd.isna(text) or text is None:
        return None
    
    text = str(text).strip()
    return text if text else None

def extract_phone_numbers(text: str) -> List[str]:
    """从文本中提取所有电话号码"""
    if not text or pd.isna(text):
        return []
    
    text = str(text).strip()
    
    # 提取11位手机号
    phone_pattern = r'1[3-9]\d{9}'
    phones = re.findall(phone_pattern, text)
    
    # 去重并保持顺序
    seen = set()
    unique_phones = []
    for phone in phones:
        if phone not in seen:
            seen.add(phone)
            unique_phones.append(phone)
    
    return unique_phones

def extract_name_from_phone_text(text: str) -> Optional[str]:
    """从包含电话号码的文本中提取姓名"""
    if not text or pd.isna(text):
        return None
    
    text = str(text).strip()
    
    # 移除电话号码
    text_without_phone = re.sub(r'1[3-9]\d{9}', '', text)
    # 移除其他数字和特殊字符，但保留中文
    name_text = re.sub(r'[0-9\s\-\+\(\)\/]+', '', text_without_phone).strip()
    
    return name_text if name_text else None

def clean_ktt_name(name: str) -> Optional[str]:
    """清理KTT名字"""
    if not name or pd.isna(name):
        return None
    
    name = str(name).strip()
    
    # 移除换行符和多余空格
    name = re.sub(r'\s+', ' ', name)
    
    # 如果是表头，返回None
    if name in ['ktt名字', 'KTT名字']:
        return None
    
    return name if name else None

def clean_wechat_name(name: str) -> Optional[str]:
    """清理微信名字"""
    if not name or pd.isna(name):
        return None
    
    name = str(name).strip()
    
    # 移除换行符和多余空格
    name = re.sub(r'\s+', ' ', name)
    
    # 如果是表头，返回None
    if name in ['微信名字', '微信名']:
        return None
    
    return name if name else None

def clean_wechat_id(wechat_id: str) -> Optional[str]:
    """清理微信号"""
    if not wechat_id or pd.isna(wechat_id):
        return None
    
    wechat_id = str(wechat_id).strip()
    
    # 移除换行符和多余空格
    wechat_id = re.sub(r'\s+', ' ', wechat_id)
    
    # 如果是表头，返回None
    if wechat_id in ['微信号', '微信ID']:
        return None
    
    return wechat_id if wechat_id else None

def clean_address(address: str) -> Optional[str]:
    """清理地址信息"""
    if not address or pd.isna(address):
        return None
    
    address = str(address).strip()
    
    # 移除换行符和多余空格
    address = re.sub(r'\s+', ' ', address)
    
    # 如果是表头，返回None
    if address in ['下单地址1', '下单地址2', '地址1', '地址2']:
        return None
    
    return address if address else None

def clean_blacklist_reason(reason: str) -> Optional[str]:
    """清理黑名单原因"""
    if not reason or pd.isna(reason):
        return None
    
    reason = str(reason).strip()
    
    # 移除换行符和多余空格
    reason = re.sub(r'\s+', ' ', reason)
    
    # 如果是表头，返回None
    if reason in ['入黑名单原因', '黑名单原因', '原因']:
        return None
    
    return reason if reason else None

def determine_risk_level(reason: str) -> str:
    """根据黑名单原因确定风险等级"""
    if not reason:
        return 'medium'
    
    reason_lower = reason.lower()
    
    # 高风险关键词
    high_risk_keywords = [
        '惯犯', '重点', '专业', '骗子', '诈骗', '恶意', '强制', '霸王餐',
        '死罪', '锤死', '不下十家', '不下五家', '不下三家', '四家', '三家'
    ]
    
    # 低风险关键词
    low_risk_keywords = [
        '轻微', '提醒', '事精', '事妈', '挑刺', '找茬', '少发', '漏发'
    ]
    
    # 检查高风险关键词
    for keyword in high_risk_keywords:
        if keyword in reason_lower:
            return 'high'
    
    # 检查低风险关键词
    for keyword in low_risk_keywords:
        if keyword in reason_lower:
            return 'low'
    
    return 'medium'

def clean_and_organize_data(file_path: str) -> pd.DataFrame:
    """清洗和整理数据"""
    print("="*80)
    print("黑名单数据清洗和整理")
    print("="*80)
    
    try:
        # 读取Excel文件
        print(f"正在读取文件: {file_path}")
        df = pd.read_excel(file_path)
        
        # 跳过第一行说明文字
        df = df.iloc[1:].reset_index(drop=True)
        print(f"跳过第一行后，剩余行数: {len(df)}")
        
        # 设置正确的列名
        expected_columns = ['ktt名字', '微信名字', '微信号', '下单名字和电话', '下单地址1', '下单地址2', '入黑名单原因']
        df.columns = expected_columns + list(df.columns[len(expected_columns):])
        
        print(f"设置列名为: {expected_columns}")
        
        # 删除完全空行
        initial_rows = len(df)
        df = df.dropna(how='all').reset_index(drop=True)
        empty_rows_removed = initial_rows - len(df)
        print(f"删除了 {empty_rows_removed} 个完全空行")
        
        # 数据清洗
        print("\n开始数据清洗...")
        
        # 清洗KTT名字
        df['ktt名字_清洗'] = df['ktt名字'].apply(clean_ktt_name)
        
        # 清洗微信名字
        df['微信名字_清洗'] = df['微信名字'].apply(clean_wechat_name)
        
        # 清洗微信号
        df['微信号_清洗'] = df['微信号'].apply(clean_wechat_id)
        
        # 处理下单名字和电话
        df['下单名字和电话_原始'] = df['下单名字和电话'].apply(clean_text)
        df['提取的姓名'] = df['下单名字和电话_原始'].apply(extract_name_from_phone_text)
        df['提取的电话号码'] = df['下单名字和电话_原始'].apply(extract_phone_numbers)
        df['主要电话号码'] = df['提取的电话号码'].apply(lambda x: x[0] if x else None)
        
        # 清洗地址
        df['下单地址1_清洗'] = df['下单地址1'].apply(clean_address)
        df['下单地址2_清洗'] = df['下单地址2'].apply(clean_address)
        
        # 清洗黑名单原因
        df['入黑名单原因_清洗'] = df['入黑名单原因'].apply(clean_blacklist_reason)
        df['风险等级'] = df['入黑名单原因_清洗'].apply(determine_risk_level)
        
        # 过滤有效记录（必须有KTT名字或电话号码）
        valid_mask = (
            df['ktt名字_清洗'].notna() | 
            df['主要电话号码'].notna()
        )
        df_valid = df[valid_mask].copy().reset_index(drop=True)
        
        print(f"有效记录数: {len(df_valid)} (原始: {len(df)})")
        
        # 去重处理（基于电话号码）
        print("\n处理重复数据...")
        phone_counts = df_valid['主要电话号码'].value_counts()
        duplicate_phones = phone_counts[phone_counts > 1].index.tolist()
        print(f"发现 {len(duplicate_phones)} 个重复电话号码")
        
        # 对于重复的电话号码，保留第一个记录
        df_deduplicated = df_valid.drop_duplicates(subset=['主要电话号码'], keep='first').reset_index(drop=True)
        duplicates_removed = len(df_valid) - len(df_deduplicated)
        print(f"去重后记录数: {len(df_deduplicated)} (删除了 {duplicates_removed} 个重复记录)")
        
        # 生成统计信息
        stats = {
            'total_original': len(df),
            'empty_rows_removed': empty_rows_removed,
            'valid_records': len(df_valid),
            'duplicates_removed': duplicates_removed,
            'final_records': len(df_deduplicated),
            'with_ktt_name': df_deduplicated['ktt名字_清洗'].notna().sum(),
            'with_phone': df_deduplicated['主要电话号码'].notna().sum(),
            'with_wechat_name': df_deduplicated['微信名字_清洗'].notna().sum(),
            'with_wechat_id': df_deduplicated['微信号_清洗'].notna().sum(),
            'with_address1': df_deduplicated['下单地址1_清洗'].notna().sum(),
            'with_address2': df_deduplicated['下单地址2_清洗'].notna().sum(),
            'with_reason': df_deduplicated['入黑名单原因_清洗'].notna().sum(),
            'risk_levels': df_deduplicated['风险等级'].value_counts().to_dict()
        }
        
        print(f"\n📊 清洗后数据统计:")
        print(f"  原始记录数: {stats['total_original']}")
        print(f"  删除空行: {stats['empty_rows_removed']}")
        print(f"  有效记录: {stats['valid_records']}")
        print(f"  删除重复: {stats['duplicates_removed']}")
        print(f"  最终记录: {stats['final_records']}")
        print(f"  有KTT名字: {stats['with_ktt_name']}")
        print(f"  有电话号码: {stats['with_phone']}")
        print(f"  有微信名字: {stats['with_wechat_name']}")
        print(f"  有微信号: {stats['with_wechat_id']}")
        print(f"  有地址1: {stats['with_address1']}")
        print(f"  有地址2: {stats['with_address2']}")
        print(f"  有黑名单原因: {stats['with_reason']}")
        print(f"  风险等级分布: {stats['risk_levels']}")
        
        # 显示样本数据
        print(f"\n📋 清洗后样本数据 (前5条):")
        sample_columns = [
            'ktt名字_清洗', '微信名字_清洗', '微信号_清洗', 
            '提取的姓名', '主要电话号码', '下单地址1_清洗', 
            '入黑名单原因_清洗', '风险等级'
        ]
        
        for index, row in df_deduplicated.head(5).iterrows():
            print(f"\n  记录 {index + 1}:")
            for col in sample_columns:
                if col in df_deduplicated.columns:
                    value = row[col]
                    if pd.notna(value):
                        print(f"    {col}: {value}")
                    else:
                        print(f"    {col}: [空]")
        
        # 保存清洗后的数据
        output_file = "data/blacklist/cleaned_blacklist_data.xlsx"
        df_deduplicated.to_excel(output_file, index=False)
        print(f"\n✅ 清洗后的数据已保存到: {output_file}")
        
        # 保存统计报告
        stats_file = "data/blacklist/data_cleaning_report.json"
        # 转换numpy类型为Python原生类型
        stats_serializable = {}
        for key, value in stats.items():
            if isinstance(value, dict):
                stats_serializable[key] = {k: int(v) if isinstance(v, (np.integer, np.int64)) else v for k, v in value.items()}
            elif isinstance(value, (np.integer, np.int64)):
                stats_serializable[key] = int(value)
            else:
                stats_serializable[key] = value
        
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats_serializable, f, ensure_ascii=False, indent=2)
        print(f"✅ 统计报告已保存到: {stats_file}")
        
        return df_deduplicated
        
    except Exception as e:
        print(f"❌ 数据清洗过程中出错: {e}")
        return None

def main():
    """主函数"""
    excel_file = "data/blacklist/副本-5_ktt手作骗子持更2025版.xlsx"
    
    if not Path(excel_file).exists():
        print(f"❌ 错误: 找不到文件 {excel_file}")
        return
    
    result = clean_and_organize_data(excel_file)
    
    if result is not None:
        print(f"\n✅ 数据清洗和整理完成！")
        print(f"📊 最终处理了 {len(result)} 条有效记录")
    else:
        print(f"\n❌ 数据清洗失败")

if __name__ == "__main__":
    main()
