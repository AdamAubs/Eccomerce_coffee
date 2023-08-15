from flask import Flask, request, g, current_app, Blueprint
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import logging
from logging.handlers import SMTPHandler,RotatingFileHandler
import os
from flask_mail import Mail
import stripe
from flask_babel import Babel
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView


app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
mail = Mail()
babel = Babel()


# Initialize Stripe API with STRIPE_SECRET_KEY
stripe.api_key = app.config["STRIPE_SECRET_KEY"]



def create_app(config_class=Config):
    app=Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    babel.init_app(app)
    
    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)
    
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)
    
    from app.checkout import bp as checkout_bp
    app.register_blueprint(checkout_bp)
    
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
   
    #set up email notifications for errors
    if not app.debug: #if not in dev mode
        if app.config['MAIL_SERVER']: #check if MAIL_SERVER variable is set in app.config file
            auth = None 
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']: #sets up auth variable with the email server credentials
                auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']: #secure variable is set based on MAIL_USE_TLS. (Transport Layer Security) a cryptographic protocol used to secure communications over a computer network, most commonly the internet.
                secure = ()
            #(Simple Mail Transfer Protocol Handler) SMTPhandler is instantiated with the nessary parameters
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']), #email server settings
                fromaddr='no-reply@' + app.config['MAIL_SERVER'], #the sender
                toaddrs=app.config['ADMINS'], subject= 'Coffee Shope failure', #the recipients and subject of the email
                credentials=auth, secure=secure) #secure connection details
            mail_handler.setLevel(logging.ERROR) #only send emails with a severity level of ERROR or higher; no warnings
            app.logger.addHandler(mail_handler) #attaches mail_handlers to app.logger object from Flask
            if not os.path.exists('logs'): #Create logs dir if it dosen't exists
                os.mkdir('logs')
            file_handler = RotatingFileHandler('logs/coffee_shop.log', maxBytes=10240, backupCount=10) #rotates the logs ensuring that the log files do not grow too large when application runs for long time. lim size to 10KB keep backup last 10
            file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')) #formates logs with timestamp, logging level, the message, and line number where log entry originated
            file_handler.setLevel(logging.INFO) #set logging level to INFO category diff. categories include(DEBUG, INFO, WARNING, ERROR, CRITICAL) in increasing level of severity
            app.logger.addHandler(file_handler)
            
            app.logger.setLevel(logging.INFO)
            app.logger.info('Coffee startup')
            
    from app.models import Order, User, Product
    from app.admin import OrderView, ProductView, DashboardView
    
    admin = Admin(app, index_view=DashboardView())
    admin.add_view(OrderView(Order, db.session))
    admin.add_view(ModelView(User, db.session))
    admin.add_view(ProductView(Product, db.session))
    
    
    return app

@babel.localeselector
def get_locale():
    user = getattr(g, 'user', None)
    if user is not None:
        return user.locale
    return request.accept_languages.best_match(current_app.config['LANGUAGES'])
    
from app import models, admin
