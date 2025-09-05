from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

# Connect to Mongo Atlas Clutter
mongo_client = MongoClient(os.getenv("MONGO_URI"))

# Access database
ecommerce_db = mongo_client["ecommerce_db"]

# Pick a collection to operate on
products_collection = ecommerce_db["products"]
users_collection = ecommerce_db["users"]
cart_list = ecommerce_db["carts"]
