"""API Routers - روت‌های FastAPI"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from database.db import get_session
from database.models import (
    User, Product, Category, Panel, Order, Transaction,
    BankCard, VPSOrder, PanelType, OrderStatus,
)


# ========== Users ==========
users_router = APIRouter(prefix="/users", tags=["users"])


@users_router.get("/{telegram_id}")
async def get_user(telegram_id: int, session: AsyncSession = Depends(get_session)):
    """دریافت اطلاعات کاربر با آیدی تلگرام"""
    from sqlalchemy import select
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": user.id,
        "telegram_id": user.telegram_id,
        "username": user.username,
        "full_name": user.full_name,
        "balance": user.balance,
        "role": user.role.value,
        "is_active": user.is_active,
        "created_at": str(user.created_at),
    }


@users_router.post("/")
async def create_user(user_data: dict, session: AsyncSession = Depends(get_session)):
    """ساخت کاربر جدید"""
    user = User(
        telegram_id=user_data["telegram_id"],
        username=user_data.get("username"),
        full_name=user_data.get("full_name"),
    )
    session.add(user)
    await session.commit()
    return {"id": user.id}


# ========== Products ==========
products_router = APIRouter(prefix="/products", tags=["products"])


@products_router.get("/")
async def list_products(session: AsyncSession = Depends(get_session)):
    """لیست محصولات فعال"""
    from sqlalchemy import select
    result = await session.execute(
        select(Product).where(Product.is_active == True)
    )
    products = result.scalars().all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "price": p.price,
            "duration_days": p.duration_days,
            "traffic_gb": p.traffic_gb,
            "max_connections": p.max_connections,
            "panel_type": p.panel_type.value,
            "category_id": p.category_id,
        }
        for p in products
    ]


@products_router.get("/{product_id}")
async def get_product(product_id: int, session: AsyncSession = Depends(get_session)):
    """دریافت اطلاعات محصول"""
    from sqlalchemy import select
    result = await session.execute(select(Product).where(Product.id == product_id))
    p = result.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    return {
        "id": p.id,
        "name": p.name,
        "price": p.price,
        "duration_days": p.duration_days,
        "traffic_gb": p.traffic_gb,
        "max_connections": p.max_connections,
    }


# ========== Orders ==========
orders_router = APIRouter(prefix="/orders", tags=["orders"])


@orders_router.get("/")
async def list_orders(
    user_id: int = None,
    status: str = None,
    session: AsyncSession = Depends(get_session),
):
    """لیست سفارشات"""
    from sqlalchemy import select
    query = select(Order)
    if user_id:
        query = query.where(Order.user_id == user_id)
    if status:
        query = query.where(Order.status == OrderStatus(status))
    result = await session.execute(query.order_by(Order.created_at.desc()))
    orders = result.scalars().all()
    return [
        {
            "id": o.id,
            "user_id": o.user_id,
            "amount": o.amount,
            "status": o.status.value,
            "order_type": o.order_type,
            "created_at": str(o.created_at),
        }
        for o in orders
    ]


@orders_router.post("/")
async def create_order(order_data: dict, session: AsyncSession = Depends(get_session)):
    """ساخت سفارش جدید"""
    order = Order(
        user_id=order_data["user_id"],
        product_id=order_data.get("product_id"),
        order_type=order_data["order_type"],
        amount=order_data["amount"],
        status=OrderStatus.PENDING,
    )
    session.add(order)
    await session.commit()
    return {"id": order.id}


# ========== Panels ==========
panels_router = APIRouter(prefix="/panels", tags=["panels"])


@panels_router.get("/")
async def list_panels(session: AsyncSession = Depends(get_session)):
    """لیست پنل‌ها"""
    from sqlalchemy import select
    result = await session.execute(select(Panel))
    panels = result.scalars().all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "panel_type": p.panel_type.value,
            "host": p.host,
            "port": p.port,
            "is_active": p.is_active,
        }
        for p in panels
    ]


@panels_router.post("/{panel_id}/test")
async def test_panel(panel_id: int, session: AsyncSession = Depends(get_session)):
    """تست اتصال به پنل"""
    from sqlalchemy import select
    from api.bridges import get_bridge
    result = await session.execute(select(Panel).where(Panel.id == panel_id))
    panel = result.scalar_one_or_none()
    if not panel:
        raise HTTPException(status_code=404, detail="Panel not found")

    bridge = get_bridge(panel)
    result = await bridge.test_connection()
    await bridge.close()
    return result


# ========== Transactions ==========
transactions_router = APIRouter(prefix="/transactions", tags=["transactions"])


@transactions_router.get("/")
async def list_transactions(session: AsyncSession = Depends(get_session)):
    """لیست تراکنش‌ها"""
    from sqlalchemy import select
    result = await session.execute(select(Transaction))
    txs = result.scalars().all()
    return [
        {
            "id": t.id,
            "user_id": t.user_id,
            "amount": t.amount,
            "status": t.status.value,
            "created_at": str(t.created_at),
        }
        for t in txs
    ]


@transactions_router.post("/{tx_id}/verify")
async def verify_transaction(tx_id: int, data: dict, session: AsyncSession = Depends(get_session)):
    """تایید تراکنش"""
    from sqlalchemy import select
    result = await session.execute(select(Transaction).where(Transaction.id == tx_id))
    tx = result.scalar_one_or_none()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    tx.status = OrderStatus.PAID if data.get("approve") else OrderStatus.REJECTED
    await session.commit()
    return {"status": "ok"}


# ========== Bank Cards ==========
cards_router = APIRouter(prefix="/cards", tags=["cards"])


@cards_router.get("/")
async def list_cards(session: AsyncSession = Depends(get_session)):
    """لیست کارت‌های بانکی فعال"""
    from sqlalchemy import select
    result = await session.execute(
        select(BankCard).where(BankCard.is_active == True)
    )
    cards = result.scalars().all()
    return [
        {
            "id": c.id,
            "card_number": c.card_number,
            "card_holder": c.card_holder,
            "bank_name": c.bank_name,
        }
        for c in cards
    ]


# ========== VPS ==========
vps_router = APIRouter(prefix="/vps", tags=["vps"])


@vps_router.get("/")
async def list_vps_orders(session: AsyncSession = Depends(get_session)):
    """لیست سفارشات VPS"""
    from sqlalchemy import select
    result = await session.execute(select(VPSOrder))
    orders = result.scalars().all()
    return [
        {
            "id": v.id,
            "user_id": v.user_id,
            "cpu": v.cpu,
            "ram": v.ram,
            "disk": v.disk,
            "os": v.os,
            "status": v.status.value,
            "server_ip": v.server_ip,
        }
        for v in orders
    ]


@vps_router.post("/{vps_id}/deliver")
async def deliver_vps(
    vps_id: int, data: dict, session: AsyncSession = Depends(get_session)
):
    """تحویل VPS به کاربر"""
    from sqlalchemy import select
    result = await session.execute(select(VPSOrder).where(VPSOrder.id == vps_id))
    vps = result.scalar_one_or_none()
    if not vps:
        raise HTTPException(status_code=404, detail="VPS not found")

    vps.server_ip = data["ip"]
    vps.server_port = data.get("port", 22)
    vps.ssh_user = data["user"]
    vps.ssh_password = data["password"]
    vps.status = OrderStatus.COMPLETED
    await session.commit()
    return {"status": "delivered"}
