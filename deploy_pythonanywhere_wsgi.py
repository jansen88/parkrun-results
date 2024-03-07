"""
Code to deploy this to PythonAnywhere

Deploy instructions:
- From Bash console, git clone repo
- Set up virtual environment (couldn't find conda)
- Install dependencies (I installed from requirements file, didnt try Poetry)
- From Web page, set up web app to use that virtual environment
- Replace flask_app.py with the code from this scrip t(copy/paste in)
- Reload page
"""

import sys

# add your project directory to the sys.path
project_home = u'/home/parkrunner/parkrun-results'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# need to pass the flask app as "application" for WSGI to work
# for a dash app, that is at app.server
# see https://plot.ly/dash/deployment
from app import server
application = server