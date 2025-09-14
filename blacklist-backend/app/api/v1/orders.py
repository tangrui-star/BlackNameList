"""
订单相关API
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional
import pandas as pd
import io
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel

from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.models.order import Order as OrderModel, OrderStatus
from app.models.blacklist import Blacklist
from app.schemas.order import (
    OrderCreate, OrderUpdate, Order as OrderSchema, OrderListResponse, 
    OrderSearchParams, ExcelUploadResponse, BlacklistCheckResponse
)

router = APIRouter()


@router.post("/list", response_model=OrderListResponse)
async def get_orders(
    search_params: OrderSearchParams,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取订单列表"""
    query = db.query(OrderModel).filter(OrderModel.is_active == True)
    
    # 搜索条件
    if search_params.group_id:
        query = query.filter(OrderModel.group_id == search_params.group_id)
    if search_params.group_tour_number:
        query = query.filter(OrderModel.group_tour_number.contains(search_params.group_tour_number))
    if search_params.orderer:
        query = query.filter(OrderModel.orderer.contains(search_params.orderer))
    if search_params.contact_phone:
        query = query.filter(OrderModel.contact_phone.contains(search_params.contact_phone))
    if search_params.order_status:
        query = query.filter(OrderModel.order_status == search_params.order_status)
    if search_params.is_blacklist_checked:
        query = query.filter(OrderModel.is_blacklist_checked == search_params.is_blacklist_checked)
    if search_params.payment_time_start:
        query = query.filter(OrderModel.payment_time >= search_params.payment_time_start)
    if search_params.payment_time_end:
        query = query.filter(OrderModel.payment_time <= search_params.payment_time_end)
    
    # 获取总数
    total = query.count()
    
    # 分页
    orders = query.offset(search_params.skip).limit(search_params.limit).all()
    
    return OrderListResponse(
        data=orders,
        total=total,
        page=search_params.skip // search_params.limit + 1,
        size=search_params.limit
    )


class OrderDetailRequest(BaseModel):
    """订单详情请求"""
    order_id: int

@router.post("/detail", response_model=OrderSchema)
async def get_order(
    request: OrderDetailRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取单个订单详情"""
    order = db.query(OrderModel).filter(OrderModel.id == request.order_id, OrderModel.is_active == True).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    return order


@router.post("/create", response_model=OrderSchema)
async def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建订单"""
    order = OrderModel(**order_data.dict())
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@router.post("/update", response_model=OrderSchema)
async def update_order(
    order_id: int,
    order_data: OrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新订单"""
    order = db.query(OrderModel).filter(OrderModel.id == order_id, OrderModel.is_active == True).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    update_data = order_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(order, field, value)
    
    db.commit()
    db.refresh(order)
    return order


class OrderDeleteRequest(BaseModel):
    """订单删除请求"""
    order_id: int

@router.post("/delete")
async def delete_order(
    request: OrderDeleteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除订单"""
    order = db.query(OrderModel).filter(OrderModel.id == request.order_id, OrderModel.is_active == True).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    order.is_active = False
    db.commit()
    return {"message": "订单删除成功"}


@router.post("/upload-excel", response_model=ExcelUploadResponse)
async def upload_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """上传Excel文件并导入订单数据"""
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="只支持Excel文件")
    
    try:
        # 读取Excel文件
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
        
        # 验证列名 - 根据您提供的Excel列头
        required_columns = [
            '跟团号', '下单人（可以对应kkt名字）', '团员备注', '支付时间', '团长备注',
            '商品', '订单金额', '退款金额', '订单状态',
            '自提点', '收货人', '联系电话（对应phone）', '详细地址'
        ]
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=400, 
                detail=f"Excel文件缺少必要列: {', '.join(missing_columns)}"
            )
        
        imported_count = 0
        failed_count = 0
        errors = []
        
        # 处理每一行数据
        for index, row in df.iterrows():
            try:
                # 数据清洗和转换 - 根据新的Excel列头
                order_data = {
                    'group_tour_number': str(row['跟团号']) if pd.notna(row['跟团号']) else None,
                    'orderer': str(row['下单人（可以对应kkt名字）']) if pd.notna(row['下单人（可以对应kkt名字）']) else None,
                    'member_remarks': str(row['团员备注']) if pd.notna(row['团员备注']) else None,
                    'payment_time': row['支付时间'] if pd.notna(row['支付时间']) else None,
                    'group_leader_remarks': str(row['团长备注']) if pd.notna(row['团长备注']) else None,
                    'product': str(row['商品']) if pd.notna(row['商品']) else None,
                    'order_amount': Decimal(str(row['订单金额'])) if pd.notna(row['订单金额']) else None,
                    'refund_amount': Decimal(str(row['退款金额'])) if pd.notna(row['退款金额']) else Decimal('0'),
                    'order_status': str(row['订单状态']).lower() if pd.notna(row['订单状态']) else 'pending',
                    'pickup_point': str(row['自提点']) if pd.notna(row['自提点']) else None,
                    'consignee': str(row['收货人']) if pd.notna(row['收货人']) else None,
                    'contact_phone': str(row['联系电话（对应phone）']) if pd.notna(row['联系电话（对应phone）']) else None,
                    'detailed_address': str(row['详细地址']) if pd.notna(row['详细地址']) else None,
                }
                
                # 创建订单
                order = Order(**order_data)
                db.add(order)
                imported_count += 1
                
            except Exception as e:
                failed_count += 1
                errors.append(f"第{index + 2}行数据错误: {str(e)}")
        
        db.commit()
        
        return ExcelUploadResponse(
            success=True,
            message=f"成功导入{imported_count}条订单，失败{failed_count}条",
            imported_count=imported_count,
            failed_count=failed_count,
            errors=errors
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件处理失败: {str(e)}")


@router.post("/{order_id}/check-blacklist", response_model=BlacklistCheckResponse)
async def check_blacklist(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """检测订单是否在黑名单中"""
    order = db.query(OrderModel).filter(OrderModel.id == order_id, OrderModel.is_active == True).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    # 检查收货人姓名和电话是否在黑名单中
    matched_blacklists = []
    risk_level = "low"
    match_info = []
    
    if order.consignee:
        # 按姓名匹配
        name_matches = db.query(Blacklist).filter(
            Blacklist.is_active == True,
            or_(
                Blacklist.ktt_name.contains(order.consignee),
                Blacklist.order_name_phone.contains(order.consignee)
            )
        ).all()
        
        for blacklist in name_matches:
            matched_blacklists.append(blacklist.id)
            match_info.append(f"姓名匹配: {blacklist.ktt_name}")
            if blacklist.risk_level == "high":
                risk_level = "high"
            elif blacklist.risk_level == "medium" and risk_level != "high":
                risk_level = "medium"
    
    if order.contact_phone:
        # 按电话匹配
        phone_matches = db.query(Blacklist).filter(
            Blacklist.is_active == True,
            Blacklist.phone_numbers.contains([order.contact_phone])
        ).all()
        
        for blacklist in phone_matches:
            if blacklist.id not in matched_blacklists:
                matched_blacklists.append(blacklist.id)
                match_info.append(f"电话匹配: {blacklist.ktt_name}")
                if blacklist.risk_level == "high":
                    risk_level = "high"
                elif blacklist.risk_level == "medium" and risk_level != "high":
                    risk_level = "medium"
    
    # 更新订单的黑名单检测状态
    order.is_blacklist_checked = "yes"
    order.blacklist_risk_level = risk_level if matched_blacklists else "none"
    order.blacklist_match_info = "; ".join(match_info) if match_info else None
    db.commit()
    
    return BlacklistCheckResponse(
        is_blacklist=len(matched_blacklists) > 0,
        risk_level=risk_level if matched_blacklists else None,
        match_info="; ".join(match_info) if match_info else None,
        matched_blacklist_ids=matched_blacklists
    )


@router.post("/batch-check-blacklist")
async def batch_check_blacklist(
    order_ids: List[int],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """批量检测黑名单"""
    results = []
    
    for order_id in order_ids:
        try:
            result = await check_blacklist(order_id, db, current_user)
            results.append({
                "order_id": order_id,
                "is_blacklist": result.is_blacklist,
                "risk_level": result.risk_level,
                "match_info": result.match_info
            })
        except Exception as e:
            results.append({
                "order_id": order_id,
                "error": str(e)
            })
    
    return {"results": results}


@router.post("/export")
async def export_orders(
    search_params: OrderSearchParams,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """导出订单数据为Excel文件"""
    query = db.query(OrderModel).filter(OrderModel.is_active == True)
    
    # 应用搜索条件
    if search_params.group_tour_number:
        query = query.filter(OrderModel.group_tour_number.contains(search_params.group_tour_number))
    if search_params.orderer:
        query = query.filter(OrderModel.orderer.contains(search_params.orderer))
    if search_params.contact_phone:
        query = query.filter(OrderModel.contact_phone.contains(search_params.contact_phone))
    if search_params.order_status:
        query = query.filter(OrderModel.order_status == search_params.order_status)
    if search_params.is_blacklist_checked:
        query = query.filter(OrderModel.is_blacklist_checked == search_params.is_blacklist_checked)
    if search_params.payment_time_start:
        query = query.filter(OrderModel.payment_time >= search_params.payment_time_start)
    if search_params.payment_time_end:
        query = query.filter(OrderModel.payment_time <= search_params.payment_time_end)
    
    orders = query.all()
    
    # 创建DataFrame
    data = []
    for order in orders:
        data.append({
            '跟团号': order.group_tour_number,
            '下单人（可以对应kkt名字）': order.orderer,
            '团员备注': order.member_remarks,
            '支付时间': order.payment_time.strftime('%Y-%m-%d %H:%M:%S') if order.payment_time else '',
            '团长备注': order.group_leader_remarks,
            '商品': order.product,
            '订单金额': float(order.order_amount) if order.order_amount else 0,
            '退款金额': float(order.refund_amount) if order.refund_amount else 0,
            '订单状态': order.order_status.value if order.order_status else '',
            '自提点': order.pickup_point,
            '收货人': order.consignee,
            '联系电话（对应phone）': order.contact_phone,
            '详细地址': order.detailed_address,
            '黑名单检测状态': order.is_blacklist_checked,
            '风险等级': order.blacklist_risk_level,
            '匹配信息': order.blacklist_match_info,
            '创建时间': order.created_at.strftime('%Y-%m-%d %H:%M:%S') if order.created_at else '',
            '更新时间': order.updated_at.strftime('%Y-%m-%d %H:%M:%S') if order.updated_at else ''
        })
    
    df = pd.DataFrame(data)
    
    # 生成Excel文件
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='订单数据', index=False)
    
    output.seek(0)
    
    from fastapi.responses import StreamingResponse
    from datetime import datetime
    
    filename = f"订单数据导出_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    return StreamingResponse(
        io.BytesIO(output.read()),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )