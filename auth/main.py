from flask import Blueprint, current_app, flash, request, render_template, redirect, url_for
import uuid
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
import caldav
from caldav.elements import dav, cdav

class User():

    def __init__(self, id, url):
        self.id = id
        self.url = url
        self.client = None

    def is_active(self):
        """True, as all users are active."""
        return True

    @property
    def calendars(self):
        if self.client:
            return self.client.principal().calendars()
        return []

    def get_id(self):
        """Return the id to satisfy Flask-Login's requirements."""
        return self.id

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False
    
    def is_authenticated(self):
        return True
    
    def check_password(self, password):
        try:
            self.client = caldav.DAVClient(self.url, username=self.id, password=password)
            principal = self.client.principal()
            return True
        except:
            return False

def login():
    if request.method == 'POST':
        id = request.form['id']
        password = request.form['password']
        user = User(id, current_app.config["APP_CALDAV"])
        if user.check_password(password):
            current_app.config["User"][user.id] = user
            login_user(user, remember = True) 
            return redirect(url_for('events.day'))
        else:
            flash('User or password is wrong','error')
            print('error')
            return render_template('login.html')        
    return render_template('login.html')


def logout():
    current_app.config["User"].pop(current_user.id)
    logout_user()
    return redirect(url_for('events.day'))


class Auth(Blueprint):

    def __init__(self, name='auth', import_name=__name__, *args, **kwargs):
        Blueprint.__init__(self, name, import_name, template_folder='templates', *args, **kwargs)
        self.before_app_first_request(self._init)
        self.add_url_rule('/logout', 'logout', logout, methods=['GET'])
        self.add_url_rule('/login', 'login', login, methods=['POST', 'GET'])
        

    def _init(self):
        current_app.logger.debug("init auth on first request")
        self._login_manager = LoginManager()
        self._login_manager.init_app(current_app)
        if not current_app.secret_key:
            current_app.secret_key = str(uuid.uuid4())
            current_app.logger.warning("not secret key for app, generate secret key")

        @self._login_manager.user_loader
        def user_loader(id):
            return current_app.config["User"][id]
        
        @self._login_manager.unauthorized_handler
        def unauthorized():
            return redirect(url_for('auth.login'))
       
    def register(self, app, options, first_registration=False):
        try:
            Blueprint.register(self, app, options, first_registration)
        except:
            app.logger.error("init auth on register is failed")