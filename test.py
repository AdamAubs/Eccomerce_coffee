import os
os.environ['DATABASE_URL'] = 'sqlite://'

from datetime import datetime, timedelta
import unittest
from app import app, db
from app.models import User, Product

class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        u = User(username='susan')
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))

    def test_avatar(self):
        u = User(username='john', email='john@example.com')
        self.assertEqual(u.avatar(128), ('https://www.gravatar.com/avatar/'
                                         'd4c74594d841139328695756648b6bd6'
                                         '?d=wavatar&s=128'))
        
    def test_create_user_and_products(self):
        u = User(username='john', email='john@example.com')
        p = Product(name='Iced Coffee', price=5.00)
        db.session.add_all([u,p])
        db.session.commit()
        
        self.assertIsNotNone(u.id)
        self.assertIsNotNone(p.id)
        
    def test_add_to_cart(self):
        u = User(username='john', email='john@example.com')
        p = Product(name='Iced Coffee', price=5.00)
        u.add_to_cart(p)
        self.assertIn(p, u.products)
    
    def test_add_and_remove_from_cart(self):
        u = User(username='john', email='john@example.com')
        p = Product(name='Iced Coffee', price=5.00)
        u.add_to_cart(p)
        u.remove_from_cart(p)
        self.assertNotIn(p, u.products)
    
    

if __name__ == '__main__':
    unittest.main(verbosity=2)
