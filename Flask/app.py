from pathlib import Path
from flask import Flask, jsonify, render_template, request
from database import db
from models import Product, Order, ProductsOrder
from sqlalchemy import asc


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///store.db"
app.instance_path = Path(".").resolve()
db.init_app(app)


@app.route("/")
def home():
    data = Product.query.all()
    return render_template("index.html", products=data)

@app.route('/view-all-products', methods=['GET'])
def api_get_all_products():
    products = Product.query.all()
    if not products:
        return 'No products in the inventory!', 404
    return [product.to_dict() for product in products]


@app.route("/api/product/<string:name>", methods=["GET"])
def api_get_product(name):
    product = db.session.get(Product, name.lower())
    if not product:
        return f"{name} is not a valid product", 404
    product_json = product.to_dict()
    return jsonify(product_json)


@app.route("/api/product", methods=["POST"])
def api_create_product():
    data = request.json
    # Check all data is provided
    for key in ("name", "price", "quantity"):
        if key not in data:
            return f"The JSON provided is invalid (missing: {key})", 400
    try:
        price = float(data["price"])
        quantity = int(data["quantity"])
        # Make sure they are positive
        if price < 0 or quantity < 0:
            raise ValueError
    except ValueError:
        return (
            "Invalid values: Price must be a non-negative float and quantity a non-negative integer",
            400,
        )
    product = Product(
        name=data["name"],
        price=price,
        quantity=quantity,
    )
    db.session.add(product)
    db.session.commit()
    return "Item added to the database", 200


@app.route("/api/product/<string:name>", methods=["PUT"])
def api_update_product(name):
    data = request.json
    new_price = data.get('price', None)
    new_quantity = data.get('quantity', None)
    try:
        new_price = float(data["price"])
        new_quantity = int(data["quantity"])
        # Make sure they are positive
        if new_price < 0 or new_quantity < 0:
            raise ValueError
    except ValueError:
        return (
            "Invalid values: Price must be a non-negative float and quantity a non-negative integer",
            400,
        )
    product = Product.query.filter(Product.name == name).first()
    if product is None:
        return "Product not found", 404
    if new_price:
        product.price = new_price
    if new_quantity:
        product.quantity = new_quantity
    db.session.commit()
    return "Item was updated", 200


@app.route('/api/product/<string:name>', methods=['DELETE'])
def api_remove_product(name):
    product = Product.query.filter(Product.name == name).first()
    if product is None:
        return "Product not found", 404
    if ProductsOrder.query.filter(ProductsOrder.product_name == name).first():
        return "Cannot remove product since it has been ordered by customers!", 400     # referential integrity in database must be kept 
    db.session.delete(product)
    db.session.commit()
    return 'Product was removed', 200


@app.route('/api/product/not-in-stock', methods=['GET'])
def api_get_not_in_products():
    prod_list = Product.query.filter_by(quantity=0).all()
    if not prod_list:
        return "All products are in stock!", 404
    return [prod.to_dict() for prod in prod_list]


@app.route('/api/order/<int:order_id>')
def api_get_order(order_id):
    order = Order.query.get(order_id)
    if not order:
        return f"Order with id {order_id} does not exist!", 404
    return order.to_dict(), 200


@app.route('/api/order', methods=['POST'])
def api_create_order():
    data = request.json
    name = data['customer_name']
    address = data['customer_address']
    completed = data.get('completed', False)
    products = data['products']
    for item in products:
        prod = item['name']
        if not Product.query.get(item['name']):
            return f'Product {prod} is not in the store', 404
    order = Order(name=name, address=address, completed=completed)
    for item in products:
        product = Product.query.filter_by(name=item['name']).first()
        if item['quantity'] > int(product.quantity):
            return f"Insufficient inventory for product: {item['name']}", 400
        prod_quant = item['quantity']
        prod_name = item['name']
        if (not isinstance(prod_quant, int)) or (isinstance(prod_quant, int) and int(prod_quant) < 0): 
            return f"Invalid quantity for {prod_name}, only non-negative int values accepted", 400
        order_product = ProductsOrder(product=product, quantity=item['quantity'])
        order.products.append(order_product)
    db.session.add(order)
    db.session.commit()
    print(f'Order id: {order.id} was added!')
    return order.to_dict(), 200


@app.route('/api/order/process/<int:order_id>', methods=['PUT'])
def api_process_order(order_id):
    if not Order.query.get(order_id):
        return "Order not found", 404
    data = request.json
    if data is None:
        return "Missing request", 400
    order = Order.query.get(order_id)
    if order.completed is False:
        order.process()
    return order.to_dict(), 200


@app.route('/api/order/delete/<int:order_id>', methods=['DELETE'])
def api_delete_order(order_id):
    order = Order.query.get(order_id)
    if not order:
        return f"Order with id {order_id} does not exist!", 404
    for item in order.products:
        db.session.delete(item)
    db.session.delete(order)
    db.session.commit()
    return f"Order with id {order_id} was successfully removed", 200


@app.route('/api/order/<int:order_id>', methods=['PUT'])
def api_update_order(order_id):
    if (not isinstance(order_id, int)) or (isinstance(order_id, int) and int(order) < 0): 
            return f"{order_id} is not a valid order id, only non-negative int values accepted", 400
    product_list = request.json['products']
    if Order.query.filter_by(id=order_id).first() is None:
        return "Order not found", 400
    order = Order.query.filter_by(id=order_id).first()
    for item in product_list:
        prod_name = item['name']
        if not Product.query.get(prod_name):
            return f'Order not updated. Product {prod_name} is not in the database', 404
        prod_quant = item['quantity']
        if (not isinstance(prod_quant, int)) or (isinstance(prod_quant, int) and int(prod_quant) < 0): 
            return f"Invalid quantity for {prod_name}, only non-negative int values accepted", 400
        if prod_quant > Product.query.get(prod_name).quantity:
            return f"Insufficient inventory for product: {item['name']}", 400
        product_order = None
        for prod in order.products:
            if prod.product_name == prod_name:
                product_order = prod
                break
        if product_order:
            if prod_quant != 0:
                product_order.quantity = prod_quant
            else:
                db.session.delete(product_order)    # remove the ProductsOrder instance 
        else:
            if prod_quant != 0:
                new_products_order = ProductsOrder(product_name=prod_name, quantity=prod_quant)
                order.products.append(new_products_order)
    db.session.commit()
    return order.to_dict(), 200


@app.route('/api/order/pending', methods=['GET'])
def api_get_pending_orders():
    order_list = Order.query.filter_by(completed=False).order_by(asc(Order.order_date)).all()
    return [order.to_dict() for order in order_list], 200


@app.route('/api/order/processed', methods=['GET'])
def api_get_processed_orders():
    order_list = Order.query.filter_by(completed=True).all()
    order_list.sort(key=lambda order: (order.process_date, order.order_date))
    return [order.to_dict() for order in order_list], 200

@app.route('/api/order/user/<string:partial_name>', methods=['GET'])
def api_get_user_order(partial_name):
    order_list = Order.query.filter(Order.name.like(f'%{partial_name}%')).order_by(Order.name, Order.order_date).all()
    if not order_list:
        return "No order was found!", 404
    return [order.to_dict() for order in order_list], 200



if __name__ == "__main__":
    app.run(debug=True, port=5001)
