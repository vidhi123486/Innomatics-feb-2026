from fastapi import FastAPI, Query
from pydantic import BaseModel, Field
from typing import Optional, List

app = FastAPI()

# ── Pydantic model ───────────────────────────────────────────────
class OrderRequest(BaseModel):
    customer_name: str = Field(..., min_length=2, max_length=100)
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0, le=100)
    delivery_address: str = Field(..., min_length=10)

# — Temporary data - acting as our database for now
products = [
    {'id': 1, 'name': 'Wireless Mouse', 'price': 499, 'category': 'Electronics', 'in_stock': True},
    {'id': 2, 'name': 'Notebook', 'price': 99, 'category': 'Stationery', 'in_stock': True},
    {'id': 3, 'name': 'USB Hub', 'price': 799, 'category': 'Electronics', 'in_stock': False},
    {'id': 4, 'name': 'Pen Set', 'price': 49, 'category': 'Stationery', 'in_stock': True},

    #Q1. Add 3 More Products
    {"id": 5, "name": "Laptop Stand", "price": 1299, "category": "Electronics", "in_stock": True}, 
    {"id": 6, "name": "Mechanical Keyboard", "price": 2499, "category": "Electronics", "in_stock": True}, 
    {"id": 7, "name": "Webcam", "price": 1899, "category": "Electronics", "in_stock": False},
]

# Order storage
orders = []
order_counter = 1

# ══ HELPER FUNCTIONS ════════════════════════════════

def find_product(product_id: int):
    """Search products list by ID. Returns product dict or None."""
    for p in products:
        if p['id'] == product_id:
            return p
    return None


def calculate_total(product: dict, quantity: int):
    """Multiply price by quantity and return total."""
    return product['price'] * quantity


def filter_products_logic(category=None, min_price=None, max_price=None, in_stock=None):
    """Apply filters and return matching products."""
    result = products
    if category is not None: result = [p for p in result if p['category'] == category]
    if min_price is not None: result = [p for p in result if p['price'] >= min_price]
    if max_price is not None: result = [p for p in result if p['price'] <= max_price]
    if in_stock is not None: result = [p for p in result if p['in_stock'] == in_stock]
    return result


# — Endpoint 0 - Home
@app.get('/')
def home():
    return {'message': 'Welcome to our E-commerce API'}

# — Endpoint 1 - Return all products
@app.get('/products')
def get_all_products():
    return {'products': products, 'total': len(products)}

@app.get('/products/filter')
def filter_products(
    category: str = Query(None, description='Electronics or Stationery'),
    min_price: int = Query(None, description='Minimum price'),
    max_price: int = Query(None, description='Maximum price'),
    in_stock: bool = Query(None, description='True = in stock only')
):

    result = filter_products_logic(category, min_price, max_price, in_stock)

    return {'filtered_products': result, 'count': len(result)}


# ══ Product Comparison Endpoint ═════════════════════
@app.get('/products/compare')
def compare_products(
    product_id_1: int = Query(..., description='First product ID'),
    product_id_2: int = Query(..., description='Second product ID')
):

    p1 = find_product(product_id_1)
    p2 = find_product(product_id_2)

    if not p1:
        return {'error': f'Product {product_id_1} not found'}

    if not p2:
        return {'error': f'Product {product_id_2} not found'}

    cheaper = p1 if p1['price'] < p2['price'] else p2

    return {
        'product_1': p1,
        'product_2': p2,
        'better_value': cheaper['name'],
        'price_diff': abs(p1['price'] - p2['price'])
    }


#Q2. Add a Category Filter Endpoint
@app.get("/products/category/{category_name}")
def get_by_category(category_name: str):
    result = [p for p in products if p["category"] == category_name]
    if not result:
        return {"error": "No products found in this category"}
    return {"category": category_name, "products": result, "total": len(result)}


#Q3. Show Only In-Stock Products
@app.get("/products/instock") 
def get_instock(): 
    available = [p for p in products if p["in_stock"] == True] 
    return {"in_stock_products": available, "count": len(available)}


#Q5. Search Products by Name
@app.get("/products/search/{keyword}") 
def search_products(keyword: str): 
    results = [p for p in products if keyword.lower() in p["name"].lower()] 
    if not results: 
        return {"message": "No products matched your search"} 
    return {"keyword": keyword, "results": results, "total_matches": len(results)}


#Q4. Build a Store Info Endpoint
@app.get("/store/summary") 
def store_summary(): 
    in_stock_count = len([p for p in products if p["in_stock"]]) 
    out_stock_count = len(products) - in_stock_count 
    categories = list(set([p["category"] for p in products])) 
    return {
        "store_name": "My E-commerce Store",
        "total_products": len(products),
        "in_stock": in_stock_count,
        "out_of_stock": out_stock_count,
        "categories": categories,
    }

#Assignment 2: Q4. Build a Product Summary Dashboard
@app.get("/products/summary")
def product_summary():
    in_stock   = [p for p in products if     p["in_stock"]]
    out_stock  = [p for p in products if not p["in_stock"]]
    expensive  = max(products, key=lambda p: p["price"])
    cheapest   = min(products, key=lambda p: p["price"])
    categories = list(set(p["category"] for p in products))
    return {
        "total_products":     len(products),
        "in_stock_count":     len(in_stock),
        "out_of_stock_count": len(out_stock),
        "most_expensive":     {"name": expensive["name"], "price": expensive["price"]},
        "cheapest":           {"name": cheapest["name"],  "price": cheapest["price"]},
        "categories":         categories,
    }

# — Endpoint 2 - Return one product by its ID
@app.get('/products/{product_id}')
def get_product(product_id: int):

    product = find_product(product_id)

    if not product:
        return {"error": "Product not found"}

    return {"product": product}


# ── POST Endpoint: Place Order ───────────────────────────────────
@app.post('/orders')
def place_order(order_data: OrderRequest):

    global order_counter

    product = find_product(order_data.product_id)

    if product is None:
        return {'error': 'Product not found'}

    if not product['in_stock']:
        return {'error': f"{product['name']} is out of stock"}

    total_price = calculate_total(product, order_data.quantity)

    order = {
        'order_id': order_counter,
        'customer_name': order_data.customer_name,
        'product': product['name'],
        'quantity': order_data.quantity,
        'delivery_address': order_data.delivery_address,
        'total_price': total_price,
        'status': 'confirmed' 
    }

    orders.append(order)
    order_counter += 1

    return {'message': 'Order placed successfully', 'order': order}


# ── GET Endpoint: View All Orders ─────────────────────────────────
@app.get('/orders')
def get_all_orders():
    return {'orders': orders, 'total_orders': len(orders)}

#Day 2 Assignment
#Q1. Filter Products by Minimum Price
@app.get("/products/filter")
def filter_products(min_price: int = 0, max_price: int = None):

    filtered_products = []

    for product in products:
        price = product["price"]

        if price >= min_price and (max_price is None or price <= max_price):
            filtered_products.append(product)

    return {
        "filtered_products": filtered_products,
        "count": len(filtered_products)
    }

#Q2. Get Only the Price of a Product
@app.get("/products/{product_id}/price")
def get_product_price(product_id: int):
    for product in products:
        if product["id"] == product_id:
            return {"name": product["name"], "price": product["price"]}
    return {"error": "Product not found"}

#Q3. Accept Customer Feedback
class CustomerFeedback(BaseModel):
    customer_name: str            = Field(..., min_length=2, max_length=100)
    product_id:   int            = Field(..., gt=0)
    rating:       int            = Field(..., ge=1, le=5)
    comment:      Optional[str]  = Field(None, max_length=300)

feedback = []

@app.post("/feedback")
def submit_feedback(data: CustomerFeedback):
    feedback.append(data.dict())
    return {
        "message":        "Feedback submitted successfully",
        "feedback":       data.dict(),
        "total_feedback": len(feedback),
    }

#Q5. Validate & Place a Bulk Order
class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity:   int = Field(..., gt=0, le=50)

class BulkOrder(BaseModel):
    company_name:  str           = Field(..., min_length=2)
    contact_email: str           = Field(..., min_length=5)
    items:         List[OrderItem] = Field(..., min_items=1)

@app.post("/orders/bulk")
def place_bulk_order(order: BulkOrder):
    confirmed, failed, grand_total = [], [], 0
    for item in order.items:
        product = next((p for p in products if p["id"] == item.product_id), None)
        if not product:
            failed.append({"product_id": item.product_id, "reason": "Product not found"})
        elif not product["in_stock"]:
            failed.append({"product_id": item.product_id, "reason": f"{product['name']} is out of stock"})
        else:
            subtotal = product["price"] * item.quantity
            grand_total += subtotal
            confirmed.append({"product": product["name"], "qty": item.quantity, "subtotal": subtotal})
    return {"company": order.company_name, "confirmed": confirmed,
            "failed": failed, "grand_total": grand_total}