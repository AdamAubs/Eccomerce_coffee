from flask_wtf import FlaskForm
from wtforms import SubmitField
from flask_babel import _, lazy_gettext as _l

class CheckOut(FlaskForm):
    checkout = SubmitField(_l('Check Out'))
