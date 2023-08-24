from flask import Blueprint, render_template

server_bp = Blueprint('main', __name__)


@server_bp.route('/')
def index():
    user = {'username': 'User'}
    return render_template("index.html", title='Home Page', user=user)

@server_bp.route('/parkrunner_app/')
def parkrunner_app_template():
    return render_template('dash.html', dash_url='/parkrunner_app_raw_dash/')
