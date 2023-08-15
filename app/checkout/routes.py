from app import app, db
from flask import render_template, render_template, flash, redirect, url_for, request
from flask_login import current_user, login_required

from app.checkout.forms import CheckOut
from app.main.forms import EmptyForm
from app.models import User, Order
from app.checkout import bp
import stripe

from flask_babel import _

@bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    form = EmptyForm()
    user = current_user
    cart_items = user.cart_items.all()
    
    cart_total = sum(cart_item.product.price * cart_item.quantity for cart_item in cart_items)
    
    return render_template('checkout/checkout_page.html', title=_('Checkout'), cart_items=cart_items, form=form, cart_total=cart_total)

@bp.route('/order', methods=['POST'])
@login_required
def order():
    form = CheckOut()
    user = current_user
    cart_items = user.cart_items.all()
    
    if form.validate_on_submit():
        line_items = []
        
        for cart_item in cart_items:
            product = cart_item.product
            product_name = product.name
            product_price = int(product.price * 100)

            quantity = cart_item.quantity

            line_items.append({
                'price_data': {
                    'product_data': {
                        'name': product_name,
                    },
                    'unit_amount': product_price,
                    'currency': 'usd',
                },
                'quantity': quantity
            })
            
        if len(line_items) < 1:
            flash(_("No Items In Cart"))
            return redirect(url_for('checkout.checkout_page.html'))

        checkout_session = stripe.checkout.Session.create(
            line_items=line_items,
            payment_method_types=['card'],
            mode='payment',
            success_url=request.host_url + 'order/success',
            cancel_url=request.host_url + 'order/cancel',
        )

        return redirect(checkout_session.url)
    
    return render_template('checkout.order.html', form=form, cart_items=cart_items)

@bp.route('/order/success')
@login_required
def succcess():
    
    user = User.query.get(current_user.id)
    
    print(user.student_id, user.username, user.email)
    cart_items = user.cart_items.all()
    
    cart_total = sum(cart_item.product.price * cart_item.quantity for cart_item in cart_items)
        
    print(cart_total)
    
    # product_total = sum(cart_item.product.price * cart_item.quantity for cart_item in cart_items if cart_item.product.name == product_name)
    
    # print(product_total)
    
    purchased_items = []
    for cart_item in cart_items:
        product = cart_item.product
        product_name = product.name
        product_price = int(product.price * 100)
        quantity = cart_item.quantity
        product_total = sum(cart_item.product.price * cart_item.quantity for cart_item in cart_items if cart_item.product.name == product_name)
        
        new_order = Order(user_id=current_user.id, product_id=product_name, student_id=user.student_id, total_price=product_total, quantity=cart_item.quantity)

        db.session.add(new_order)
        db.session.commit()
    
    # for line_item in line_items:
    #     product_name = line_item.price_data.product_data.name
    #     unit_amount = line_item.price_data.unit_amount
    #     currency = line_item.price_data.currency
    #     quantity = line_item.quantity

    #new_order = Order(user_id=current_user.id, product_id=product_name, student_id=user.student_id, total_price=cart_total)
    
    # print(new_order)
    return render_template('checkout/success.html')

@bp.route('/order/cancel')
def cancel():
    return render_template('checkout/cancel.html')
