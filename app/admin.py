from flask_admin.contrib.sqla import ModelView
from flask_admin.base import expose
from flask_admin import AdminIndexView
from sqlalchemy import func
from app import db

class DashboardView(AdminIndexView):
    @expose('/')
    def index(self):
        from app.models import Product, User, Order  # Import models here to avoid circular import
        total_revenue = db.session.query(func.sum(Order.total_price)).scalar() or 0
        total_orders = db.session.query(func.count(Order.id)).scalar() or 0
        top_products = db.session.query(Product.name, func.sum(Order.quantity).label('total_quantity')).join(Order, Product.id == Order.product_id).group_by(Product.name).order_by(func.sum(Order.quantity).desc()).limit(5).all()
        return self.render('admin/dashboard.html', total_revenue=total_revenue, total_orders=total_orders, top_products=top_products)


class ProductView(ModelView):
    column_list = ['name', 'price']
    column_searchable_list = ['name']
    form_columns = ['name', 'price']

class OrderView(ModelView):
    column_list = ['user_id', 'product_id', 'order_date', 'total_price', 'quantity']



