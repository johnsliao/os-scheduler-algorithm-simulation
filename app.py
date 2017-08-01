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
    number_of_processes = request.args.get('number_of_processes') if request.args.get('number_of_processes') else 10
    priority_range_max = request.args.get('priority_range_max') if request.args.get('priority_range_max') else 10
    burst_time_range_max = request.args.get('burst_time_range_max') if request.args.get('burst_time_range_max') else 10
    arrival_time_range_max = request.args.get('arrival_time_range_max') if request.args.get(
        'arrival_time_range_max') else 10
    time_quantum = request.args.get('time_quantum') if request.args.get('time_quantum') else 3

    params = [number_of_processes, priority_range_max, burst_time_range_max, arrival_time_range_max,
              time_quantum]

    number_of_processes = int(number_of_processes)
    priority_range_max = int(priority_range_max)
    burst_time_range_max = int(burst_time_range_max)
    arrival_time_range_max = int(arrival_time_range_max)
    time_quantum = int(time_quantum)


    results = algorithms.run_simulation(number_of_processes=number_of_processes,
                                        priority_range_max=priority_range_max,
                                        burst_time_range_max=burst_time_range_max,
                                        arrival_time_range_max=arrival_time_range_max,
                                        time_quantum=time_quantum)

    # Render the charts here

    #print results

    labels = [p for p in range(1, number_of_processes + 1)]

    fcfs_values_waiting = []
    sjf_values_waiting = []
    srtf_values_waiting = []
    rr_values_waiting = []
    ps_values_waiting = []

    fcfs_values_turnaround = []
    sjf_values_turnaround = []
    srtf_values_turnaround = []
    rr_values_turnaround = []
    ps_values_turnaround = []

    for p in labels:
        fcfs_values_waiting.append(results['First Come First Serve'][p]['waiting_time'])
        sjf_values_waiting.append(results['Shortest Job First'][p]['waiting_time'])
        srtf_values_waiting.append(results['Shortest Remaining Time First'][p]['waiting_time'])
        rr_values_waiting.append(results['Round Robin'][p]['waiting_time'])
        ps_values_waiting.append(results['Priority Scheduling'][p]['waiting_time'])

        fcfs_values_turnaround.append(results['First Come First Serve'][p]['turnaround_time'])
        sjf_values_turnaround.append(results['Shortest Job First'][p]['turnaround_time'])
        srtf_values_turnaround.append(results['Shortest Remaining Time First'][p]['turnaround_time'])
        rr_values_turnaround.append(results['Round Robin'][p]['turnaround_time'])
        ps_values_turnaround.append(results['Priority Scheduling'][p]['turnaround_time'])



    fcfs_values_waiting.append(results['First Come First Serve']['average_waiting_time'])
    sjf_values_waiting.append(results['Shortest Job First']['average_waiting_time'])
    srtf_values_waiting.append(results['Shortest Remaining Time First']['average_waiting_time'])
    rr_values_waiting.append(results['Round Robin']['average_waiting_time'])
    ps_values_waiting.append(results['Priority Scheduling']['average_waiting_time'])

    fcfs_values_turnaround.append(results['First Come First Serve']['average_turnaround_time'])
    sjf_values_turnaround.append(results['Shortest Job First']['average_turnaround_time'])
    srtf_values_turnaround.append(results['Shortest Remaining Time First']['average_turnaround_time'])
    rr_values_turnaround.append(results['Round Robin']['average_turnaround_time'])
    ps_values_turnaround.append(results['Priority Scheduling']['average_turnaround_time'])


    import copy
    labels_graph_waiting = copy.deepcopy(labels)
    labels_graph_turnaround = copy.deepcopy(labels)

    labels_graph_waiting.append('avg')
    labels_graph_turnaround.append('avg')


    return render_template('pages/cs575.home.html', results=results,
                           labels=labels,
                           fcfs_values_waiting=fcfs_values_waiting,
                           sjf_values_waiting=sjf_values_waiting,
                           srtf_values_waiting=srtf_values_waiting,
                           rr_values_waiting=rr_values_waiting,
                           ps_values_waiting=ps_values_waiting,
                           fcfs_values_turnaround=fcfs_values_turnaround,
                           sjf_values_turnaround=sjf_values_turnaround,
                           srtf_values_turnaround=srtf_values_turnaround,
                           rr_values_turnaround=rr_values_turnaround,
                           ps_values_turnaround=ps_values_turnaround,
                           labels_graph_waiting=labels_graph_waiting,
                           labels_graph_turnaround=labels_graph_turnaround,

                           )


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
