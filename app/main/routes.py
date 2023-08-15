from app import app, db
from flask import render_template, render_template, flash, redirect, url_for, request, jsonify
from flask_login import current_user, login_required

from app.main.forms import EditProfileForm, EmptyForm
from app.models import User, Product
from app.main import bp

from app.translate import translate
from flask_babel import _
from langdetect import detect, LangDetectException

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = EmptyForm()
    products = Product.query.all()
    for product in products:
        try:
            language = detect(product.name)
        except LangDetectException:
            language = ''
        product_language = Product(language=language)
        print(product_language)

    return render_template('index.html', title=_('Home'), products=products, product_language=product_language, form=form)

@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        db.session.commit()
        flash(_('Your changes have been saved'))
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
    return render_template('edit_profile.html', title=_('Edit Profile'), form=form)

@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)

@bp.route('/addToCart/<name>', methods=['POST'])
@login_required
def addToCart(name):
    form = EmptyForm()
    if form.validate_on_submit():
        product = Product.query.filter_by(name=name).first()
        if product is None:
            flash(_('Product %(name)s is not avalible', name=name), 'error')
            return redirect(url_for('main.index'))
        current_user.add_to_cart(product)
        db.session.commit()
        flash(_('%(name)s added to order!', name=name), 'success')
        return redirect(url_for('main.index'))
    else:
        return redirect(url_for('main.index'))

@bp.route('/removeFromCart/<name>', methods=['POST'])
@login_required
def removeFromCart(name):
    form = EmptyForm()
    if form.validate_on_submit():
        product = Product.query.filter_by(name=name).first()
        if product is None:
            flash(_('Product %(name)s is not in cart', name=name))
            return redirect(url_for('checkout.checkout'))
        current_user.remove_from_cart(product)
        db.session.commit()
        flash(_('%(name)s has been removed from cart', name=name))
        return redirect(url_for('checkout.checkout'))
    else:
        return redirect(url_for('checkout.checkout'))

@bp.route('/translate', methods=['POST'])
@login_required
def translate_text():
    
    return jsonify({'text': translate(request.form['text'],
                                      request.form['source_language'],
                                      request.form['dest_language'])})
