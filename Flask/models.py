from database import db
from datetime import datetime


class Product(db.Model):
    name = db.Column(db.String, primary_key=True)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    orders = db.relationship('ProductsOrder', back_populates='product')

    def to_dict(self):
        return dict(name=self.name, price=self.price, quantity=self.quantity)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    order_date = db.Column(db.DateTime, nullable=False, default=datetime.now())
    process_date = db.Column(db.DateTime, nullable=True)    # figure this out
    products = db.relationship('ProductsOrder', back_populates='order')

    def to_dict(self):
        products_list = []
        for prodord in self.products:
            products_list.append(dict(name=prodord.product.name, quantity=prodord.quantity))
        total_price = 0
        for prodord in self.products:
            total_price += prodord.product.price * prodord.quantity
        return dict(order_id=self.id,
                    customer_name=self.name, 
                    customer_address=self.address, 
                    order_date=self.order_date,
                    process_date=self.process_date,
                    completed=self.completed, 
                    products=products_list, 
                    price=round(total_price, 2))
        
    def process(self):
        for item in self.products:
            product = item.product
            if product.quantity < item.quantity:
                item.quantity = product.quantity
            product.quantity -= item.quantity
            if product.quantity < 0:
                product.quantity = 0
        self.process_date = datetime.now()
        self.completed = True
        db.session.commit()


class ProductsOrder(db.Model):
    product_name = db.Column(db.ForeignKey("product.name"), primary_key=True)
    order_id = db.Column(db.ForeignKey("order.id"), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    product = db.relationship('Product', back_populates='orders')  # add back_populate for Product too?
    order = db.relationship('Order', back_populates='products')
    