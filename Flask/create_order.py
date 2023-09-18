import random

from app import app, db
from models import Order, Product, ProductsOrder

with app.app_context():
    o = Order(name="Tim", address="Vancouver") #create an order instance
    db.session.add(o)
    db.session.commit()

    print("New order, with ID", o.id)

    # Let's add five random products with random quantities to the order
    # Product.query.all() gets all products in database, k -> length of the sample
    products = random.sample(Product.query.all(), k=5)

    for p in products:
        quantity = random.randint(1, 10)
        # shouldnt it be product_name below? no because product name comes with product (foreign key)
        association = ProductsOrder(product=p, order=o, quantity=quantity)
        db.session.add(association)

    db.session.commit()
