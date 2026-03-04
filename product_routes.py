from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.encoders import jsonable_encoder

from auth_routes import get_current_user
from database import session, engine
from models import User, Product
from schemas import ProductModel

product_router = APIRouter(
    prefix="/product",
)
session = session(bind=engine)


@product_router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductModel, user: User = Depends(get_current_user)):
    if user.is_staff:
        new_product = Product(
            name=product.name,
            price=product.price
        )
        session.add(new_product)
        session.commit()
        data = {
            "success": True,
            "code": status.HTTP_201_CREATED,
            "message": "Product created successfully",
            "data": {
                "id": new_product.id,
                "name": new_product.name,
                "price": new_product.price,
            }
        }
        return jsonable_encoder(data)
    else:
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not allowed")


@product_router.get("/list", status_code=status.HTTP_200_OK)
async def product_list(user: User = Depends(get_current_user)):
    if user.is_staff:
        products = session.query(Product).all()
        data = {
            "success": True,
            "code": status.HTTP_201_CREATED,
            "message": "Product list successfully",
            "data": products
        }
        return jsonable_encoder(data)
    else:
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not allowed")


@product_router.get("/{id}", status_code=status.HTTP_200_OK)
async def product_detail(id: int, user: User = Depends(get_current_user)):
    if user.is_staff:
        product = session.query(Product).get(id)
        data = {
            "success": True,
            "code": status.HTTP_200_OK,
            "message": "Product detail successfully",
            "data": product
        }
        return jsonable_encoder(data)
    else:
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not allowed")


@product_router.delete("/delete/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def product_delete(id: int, user: User = Depends(get_current_user)):
    if not user.is_staff:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not allowed")

    product = session.query(Product).filter(Product.id == id).first()
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product is not found")

    session.delete(product)
    session.commit()


@product_router.put("/update/{id}", status_code=status.HTTP_202_ACCEPTED)
async def product_update(id: int, update_data: ProductModel, user: User = Depends(get_current_user)):
    if not user.is_staff:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not allowed")

    product = session.query(Product).filter(Product.id == id).first()
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product is not found")

    for key, value in update_data.dict(exclude_unset=True).items():
        setattr(product, key, value)
    session.commit()
    data = {
        "success": True,
        "code": status.HTTP_202_ACCEPTED,
        "message": "Product detail successfully",
        "data": {
            "id": product.id,
            "name": product.name,
            "price": product.price
        }
    }
    return jsonable_encoder(data)
