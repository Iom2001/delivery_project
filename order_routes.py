from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.encoders import jsonable_encoder

from auth_routes import get_current_user
from database import session, engine
from models import User, Order
from schemas import OrderModel

order_router = APIRouter(
    prefix="/order",
)

session = session(bind=engine)


@order_router.get("/")
async def welcome_page(user: User = Depends(get_current_user)):
    return jsonable_encoder(user)


@order_router.post("/make", status_code=status.HTTP_201_CREATED)
async def make_order(order: OrderModel, user: User = Depends(get_current_user)):
    if user.is_staff:
        new_order = Order(
            quantity=order.quantity,
            user_id=user.id,
            product_id=order.product_id
        )
        session.add(new_order)
        session.commit()
        session.refresh(new_order)
        data = {
            "success": True,
            "code": 201,
            "message": "Order is created successfully",
            "data": {
                "id": new_order.id,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email
                },
                "product": {
                    "id": new_order.product.id,
                    "name": new_order.product.name,
                    "price": new_order.product.price
                },
                "quantity": new_order.quantity,
                "order_status": new_order.order_statuses,
                "total_price": new_order.quantity * new_order.product.price
            }
        }
        return jsonable_encoder(data)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Only superusers can make orders')


@order_router.get("/list", status_code=status.HTTP_200_OK)
async def all_orders(user: User = Depends(get_current_user)):
    if user.is_staff:
        orders = session.query(Order).all()
        response = {
            "success": True,
            "code": 200,
            "message": "All orders are created successfully",
            "data": orders
        }
        return jsonable_encoder(response)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Only superusers can make orders')


@order_router.get("/order/{id}", status_code=status.HTTP_200_OK)
async def order_by_id(id: int, user: User = Depends(get_current_user)):
    if user.is_staff:
        order = session.query(Order).get(id)
        response = {
            "success": True,
            "code": 200,
            "message": "Order are created successfully",
            "data": order
        }
        return jsonable_encoder(response)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Only superusers can make orders')


@order_router.get("/all/order", status_code=status.HTTP_200_OK)
async def order_by_user_id(user: User = Depends(get_current_user)):
    orders = user.orders
    response = {
        "success": True,
        "code": 200,
        "message": "Order are created successfully",
        "data": {
            "orders": orders,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            }
        }
    }
    return jsonable_encoder(response)
