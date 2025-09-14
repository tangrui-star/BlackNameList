#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
黑名单匹配服务
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from difflib import SequenceMatcher
from app.models.blacklist import Blacklist
from app.models.order import Order
from app.models.user import RiskLevel


class BlacklistMatcher:
    """黑名单匹配器"""
    
    def __init__(self):
        self.phone_pattern = re.compile(r'1[3-9]\d{9}')  # 手机号正则
        self.name_similarity_threshold = 0.8  # 姓名相似度阈值
        self.phone_similarity_threshold = 0.9  # 电话相似度阈值
        self.address_similarity_threshold = 0.7  # 地址相似度阈值
    
    def extract_phones(self, text: str) -> List[str]:
        """从文本中提取电话号码"""
        if not text:
            return []
        phones = self.phone_pattern.findall(str(text))
        return list(set(phones))  # 去重
    
    def normalize_name(self, name: str) -> str:
        """标准化姓名（去除空格、特殊字符）"""
        if not name:
            return ""
        return re.sub(r'[^\u4e00-\u9fa5a-zA-Z]', '', str(name)).strip()
    
    def calculate_similarity(self, str1: str, str2: str) -> float:
        """计算字符串相似度"""
        if not str1 or not str2:
            return 0.0
        return SequenceMatcher(None, str1, str2).ratio()
    
    def match_phone(self, order_phone: str, blacklist_phones: List[str]) -> Tuple[bool, float, str]:
        """匹配电话号码"""
        if not order_phone or not blacklist_phones:
            return False, 0.0, ""
        
        order_phones = self.extract_phones(order_phone)
        if not order_phones:
            return False, 0.0, ""
        
        for order_phone_num in order_phones:
            for blacklist_phone in blacklist_phones:
                if isinstance(blacklist_phone, str):
                    blacklist_phones_extracted = self.extract_phones(blacklist_phone)
                    for bp in blacklist_phones_extracted:
                        similarity = self.calculate_similarity(order_phone_num, bp)
                        if similarity >= self.phone_similarity_threshold:
                            return True, similarity, f"电话匹配: {order_phone_num} ≈ {bp}"
        
        return False, 0.0, ""
    
    def match_name(self, order_name: str, blacklist_names: List[str]) -> Tuple[bool, float, str]:
        """匹配姓名"""
        if not order_name or not blacklist_names:
            return False, 0.0, ""
        
        normalized_order_name = self.normalize_name(order_name)
        if not normalized_order_name:
            return False, 0.0, ""
        
        for blacklist_name in blacklist_names:
            if not blacklist_name:
                continue
            normalized_blacklist_name = self.normalize_name(str(blacklist_name))
            if not normalized_blacklist_name:
                continue
            
            similarity = self.calculate_similarity(normalized_order_name, normalized_blacklist_name)
            if similarity >= self.name_similarity_threshold:
                return True, similarity, f"姓名匹配: {normalized_order_name} ≈ {normalized_blacklist_name}"
        
        return False, 0.0, ""
    
    def match_address(self, order_address: str, blacklist_addresses: List[str]) -> Tuple[bool, float, str]:
        """匹配地址"""
        if not order_address or not blacklist_addresses:
            return False, 0.0, ""
        
        normalized_order_address = self.normalize_name(order_address)
        if not normalized_order_address:
            return False, 0.0, ""
        
        for blacklist_address in blacklist_addresses:
            if not blacklist_address:
                continue
            normalized_blacklist_address = self.normalize_name(str(blacklist_address))
            if not normalized_blacklist_address:
                continue
            
            similarity = self.calculate_similarity(normalized_order_address, normalized_blacklist_address)
            if similarity >= self.address_similarity_threshold:
                return True, similarity, f"地址匹配: {normalized_order_address} ≈ {normalized_blacklist_address}"
        
        return False, 0.0, ""
    
    def match_order_with_blacklist(self, order: Order, blacklist_item: Blacklist) -> Dict[str, Any]:
        """匹配单个订单与黑名单项"""
        match_result = {
            "is_match": False,
            "match_type": None,
            "match_score": 0.0,
            "match_details": "",
            "risk_level": "LOW",
            "blacklist_id": blacklist_item.id,
            "blacklist_reason": blacklist_item.blacklist_reason
        }
        
        # 准备黑名单数据
        blacklist_phones = []
        if blacklist_item.phone_numbers:
            if isinstance(blacklist_item.phone_numbers, list):
                blacklist_phones.extend(blacklist_item.phone_numbers)
            else:
                blacklist_phones.append(str(blacklist_item.phone_numbers))
        
        blacklist_names = [
            blacklist_item.ktt_name,
            blacklist_item.wechat_name,
            blacklist_item.order_name_phone
        ]
        
        blacklist_addresses = [
            blacklist_item.order_address1,
            blacklist_item.order_address2
        ]
        
        # 1. 电话匹配（优先级最高）
        phone_match, phone_score, phone_detail = self.match_phone(
            order.contact_phone, blacklist_phones
        )
        if phone_match:
            match_result.update({
                "is_match": True,
                "match_type": "phone",
                "match_score": phone_score,
                "match_details": phone_detail,
                "risk_level": "HIGH"
            })
            return match_result
        
        # 2. 姓名匹配
        name_match, name_score, name_detail = self.match_name(
            order.orderer, blacklist_names
        )
        if name_match:
            match_result.update({
                "is_match": True,
                "match_type": "name",
                "match_score": name_score,
                "match_details": name_detail,
                "risk_level": "MEDIUM"
            })
            return match_result
        
        # 3. 地址匹配
        address_match, address_score, address_detail = self.match_address(
            order.detailed_address, blacklist_addresses
        )
        if address_match:
            match_result.update({
                "is_match": True,
                "match_type": "address",
                "match_score": address_score,
                "match_details": address_detail,
                "risk_level": "LOW"
            })
            return match_result
        
        return match_result
    
    def check_order_blacklist(self, order: Order, blacklist_items: List[Blacklist]) -> Dict[str, Any]:
        """检查订单是否在黑名单中"""
        matches = []
        
        for blacklist_item in blacklist_items:
            match_result = self.match_order_with_blacklist(order, blacklist_item)
            if match_result["is_match"]:
                matches.append(match_result)
        
        if not matches:
            return {
                "is_blacklist": False,
                "risk_level": "LOW",
                "matches": []
            }
        
        # 按风险等级和匹配分数排序
        matches.sort(key=lambda x: (x["risk_level"] == "HIGH", x["match_score"]), reverse=True)
        
        # 确定最终风险等级
        risk_levels = [match["risk_level"] for match in matches]
        if "HIGH" in risk_levels:
            final_risk = "HIGH"
        elif "MEDIUM" in risk_levels:
            final_risk = "MEDIUM"
        else:
            final_risk = "LOW"
        
        return {
            "is_blacklist": True,
            "risk_level": final_risk,
            "matches": matches,
            "match_count": len(matches)
        }


# 全局匹配器实例
blacklist_matcher = BlacklistMatcher()
