# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

from flask import Flask, render_template, request
# from flask.ext.sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from forms import *
import os
import algorithms

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
# db = SQLAlchemy(app)

# Automatically tear down SQLAlchemy.
'''
@app.teardown_request
def shutdown_session(exception=None):
    db_session.remove()
'''

# Login required decorator.
'''
def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap
'''


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route('/')
def home():
    number_of_processes = request.args.get('number_of_processes')
    priority_range_max = request.args.get('priority_range_max')
    burst_time_range_max = request.args.get('burst_time_range_max')
    arrival_time_range_max = request.args.get('arrival_time_range_max')
    max_simulation_time = request.args.get('max_simulation_time')
    time_quantum = request.args.get('time_quantum')

    params = [number_of_processes, priority_range_max, burst_time_range_max, arrival_time_range_max, max_simulation_time,
             time_quantum]

    if None in params:
        results = algorithms.run_simulation()
    else:
        number_of_processes = int(number_of_processes)
        priority_range_max = int(priority_range_max)
        burst_time_range_max = int(burst_time_range_max)
        arrival_time_range_max = int(arrival_time_range_max)
        max_simulation_time = int(max_simulation_time)
        time_quantum = int(time_quantum)

        results = algorithms.run_simulation(number_of_processes=number_of_processes,
                                            priority_range_max=priority_range_max,
                                            burst_time_range_max=burst_time_range_max,
                                            arrival_time_range_max=arrival_time_range_max,
                                            max_simulation_time=max_simulation_time,
                                            time_quantum=time_quantum)

    print results

    # Render the charts here

    labels = ["January", "February", "March", "April", "May", "June", "July", "August"]
    values = [10, 9, 8, 7, 6, 4, 7, 8]

    return render_template('pages/cs575.home.html', results=results, values=values, labels=labels)


@app.route('/about')
def about():
    return render_template('pages/placeholder.about.html')


@app.route('/login')
def login():
    form = LoginForm(request.form)
    return render_template('forms/login.html', form=form)


@app.route('/register')
def register():
    form = RegisterForm(request.form)
    return render_template('forms/register.html', form=form)


@app.route('/forgot')
def forgot():
    form = ForgotForm(request.form)
    return render_template('forms/forgot.html', form=form)


# Error handlers.

#
# @app.errorhandler(500)
# def internal_error(error):
#     # db_session.rollback()
#     return render_template('errors/500.html'), 500
#
#
# @app.errorhandler(404)
# def not_found_error(error):
#     return render_template('errors/404.html'), 404


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
