import os, logging
from flask import Flask, render_template, request
from flask_login import current_user
from datetime import datetime

from auth import Auth, login_required
from static import Static

toBoolean = {'true': True, 'false':False}

AGENDA_PORT = int(os.environ.get('AGENDA_PORT', '5000'))
AGENDA_DEBUG = toBoolean.get(os.environ.get('AGENDA_DEBUG', 'true'), True)
AGENDA_HOST = os.environ.get('AGENDA_HOST', '0.0.0.0')
AGENDA_DIR = os.environ.get('AGENDA_DIR', os.path.dirname(os.path.abspath(__file__)))
AGENDA_CALDAV = os.environ.get('CALDAV', 'http://localhost/')

app = Flask(__name__)
app.config["VERSION"] = "0.0.1"

app.config["APP_PORT"] = AGENDA_PORT
app.config["APP_HOST"] = AGENDA_HOST
app.config["APP_DEBUG"] = AGENDA_DEBUG
app.config["APP_DIR"] = AGENDA_DIR
app.config["APP_CALDAV"] = AGENDA_CALDAV
app.config["User"] = {}

# register Auth
app.register_blueprint(Auth(url_prefix="/"))
app.config['APP_NAME'] = os.environ.get('AGENDA_NAME', 'Agenda')
app.config['APP_DESC'] = os.environ.get('AGENDA_DESC', 'Minimalist Agenda')
# register Static
AGENDA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'files')
app.register_blueprint(Static(name="js", url_prefix="/javascripts/", path=os.path.join(AGENDA_PATH, "javascripts")))
app.register_blueprint(Static(name="siimple", url_prefix="/siimple/", path=os.path.join(AGENDA_PATH, "siimple")))
app.register_blueprint(Static(name="css", url_prefix="/css/", path=os.path.join(AGENDA_PATH, "css")))

# register AGENDA
from events import Events
app.register_blueprint(Events(url_prefix="/"))


if __name__ == "__main__":
    app.logger.setLevel(logging.DEBUG)
    app.run(host=AGENDA_HOST, port=AGENDA_PORT, debug=AGENDA_DEBUG)
