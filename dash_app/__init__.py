from flask import Flask
from flask.helpers import get_root_path
from dash import Dash
from dash_extensions.enrich import DashProxy, ServersideOutputTransform, MultiplexerTransform
import os
from os import getpid
import dash_bootstrap_components as dbc


def create_app(dash_debug, dash_auto_reload):
    server = Flask(__name__, static_folder='static')

    # configure flask app/server here
    server.config.from_object('config.Config')

    # register all dash apps
    from dash_app.parkrunner_app.layout import layout as parkrunner_app_layout
    from dash_app.parkrunner_app.callbacks import register_callbacks as parkrunner_app_callbacks
    register_dash_app(
        flask_server=server,
        title='Parkrunner',
        base_pathname='parkrunner_app_raw_dash',
        layout=parkrunner_app_layout,
        register_callbacks_funcs=[parkrunner_app_callbacks],
        dash_debug=dash_debug,
        dash_auto_reload=dash_auto_reload
    )

    # register extensions here
    register_blueprints(server)

    # if running on gunicorn with multiple workers this message should print once for each worker if preload_app is set to False
    print(f'Flask With Dash Apps Built Successfully with PID {str(getpid())}.')
    return server


def register_dash_app(flask_server, title, base_pathname, layout, register_callbacks_funcs, dash_debug, dash_auto_reload):
    # Meta tags for viewport responsiveness
    meta_viewport = {"name": "viewport", "content": "width=device-width, initial-scale=1, shrink-to-fit=no"}

    root_path = get_root_path(__name__)

    # if in /parkrunFun
    if os.path.isdir(os.path.join(root_path, 'dash_app')) & \
        os.path.isdir(os.path.join(root_path, 'assets')):
        assets_folder = os.path.join(root_path, 'assets')
    else:
    # otherwise - if in /parkrunFun/dash_app
        assets_folder = os.path.abspath(os.path.join(root_path, '..', 'assets'))

    # parkrunner_app = Dash(
    parkrunner_app = DashProxy(
        __name__,
        server=flask_server,
        suppress_callback_exceptions=True,
        transforms=[ServersideOutputTransform()],
        assets_folder=assets_folder,
        # meta_tags=[meta_viewport],
        external_stylesheets=[
            dbc.themes.BOOTSTRAP,
            {  # font-awesome
                "href": "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.3.0/css/all.min.css",
                "rel": "stylesheet",
                # "integrity": "sha512-iBBXm8fW90+nuLcSKlbmrPcLa0OT92xO1BIsZ+ywDWZCvqsWgccV3gFoRBv0z+8dLJgyAHIhR35VZc2oM/gI1w==",
                "crossorigin": "anonymous",
                "referrerpolicy": "no-referrer"
            }],
    )

    with flask_server.app_context():
        parkrunner_app.title = title
        parkrunner_app.layout = layout
        parkrunner_app.css.config.serve_locally = True
        parkrunner_app.enable_dev_tools(debug=dash_debug, dev_tools_hot_reload=dash_auto_reload)
        for call_back_func in register_callbacks_funcs:
            call_back_func(parkrunner_app)


def register_blueprints(server):
    from dash_app.routes import server_bp
    server.register_blueprint(server_bp)
