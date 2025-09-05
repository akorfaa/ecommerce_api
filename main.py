from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from db import products_collection, users_collection, cart_list
from bson.objectid import ObjectId
from utils import replace_mongo_id
from products import sample_products


class UserInfo(BaseModel):
    username: str
    email: str
    password: str


class Item(BaseModel):
    product_id: str
    quantity: int = 1


class UserCart(BaseModel):
    item: Item
    user_id: str


users = [replace_mongo_id(user) for user in users_collection.find()]
products = [replace_mongo_id(product) for product in products_collection.find()]

app = FastAPI()


@app.get("/")
def get_home():
    return {"message": "Welcome to our E-commerce API"}


# lists of sample products
@app.get("/products")
def get_products():
    # products = [replace_mongo_id(product) for product in products_collection.find()]
    return {"products": products}


@app.get("/products/{product_id}")
def get_product_by_id(product_id: str):
    # products = [replace_mongo_id(product) for product in products_collection.find()]
    for product in products:
        if product["id"] == product_id:
            return {"product": product}

    raise HTTPException(status_code=404, detail="Product not found")


@app.post("/register")
# POST /register → accept user details and add to the list.
def post_register(user: UserInfo):
    # Check if username/email exists
    if users_collection.find_one(
        {"$or": [{"username": user.username}, {"email": user.email}]}
    ):
        raise HTTPException(
            status_code=400, detail="Username or email already registered"
        )

    user_data = user.model_dump()
    result = users_collection.insert_one(user_data)
    saved_user = users_collection.find_one({"_id": result.inserted_id})
    saved_user = replace_mongo_id(saved_user)
    return {"message": "User registered successfully", "user": saved_user}


# POST /login → check username/email + password,
# return "Login successful" or "Invalid credentials".
@app.post("/login")
def post_login_details(user_name: str, user_password: str):
    # 3
    user = users_collection.find_one({"username": user_name, "password": user_password})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {"message": "Login successful", "user": replace_mongo_id(user)}


@app.post("/cart")
def add_to_cart(cart: UserCart):
    # Ensure user exists
    if not users_collection.find_one({"_id": ObjectId(cart.user_id)}):
        raise HTTPException(status_code=404, detail="User not found")

    # Ensure product exists
    product = products_collection.find_one({"id": (cart.item.product_id)})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Insert cart item
    cart_data = cart.model_dump()
    result = cart_list.insert_one(cart_data)

    saved_cart = cart_list.find_one({"_id": result.inserted_id})
    saved_cart = replace_mongo_id(saved_cart)

    return {"message": "Item added to cart", "cart": saved_cart}


@app.get("/cart/{user_id}")
def get_cart(user_id: str):
    items = list(cart_list.find({"user_id": user_id}))
    if not items:
        return {"cart": []}

    cart_items = [replace_mongo_id(item) for item in items]
    return {"cart": cart_items}
