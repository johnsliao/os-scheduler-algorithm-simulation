# os-scheduler-algorithm-simulation
Operating System Scheduling Algorithm Simulation

![alt text](http://i.imgur.com/2mPGAy5.gif)

# Background
Final Project for CS 575 - Operating Systems. Boston University MET College Summer 2017

# Features
- Visualization	of	the following	algorithms:  
o First	come,	first	serve (FCFS) (Non-preemptive)  
o Shortest	Job	First (SJF) (Non-preemptive)  
o Shortest	Remaining	Time	First	(SRTF) (pre-emptive)  
o Round	Robin (RR) (pre-emptive)  
o Priority	Scheduling (PS) (pre-emptive)  

- Adjustable	input	parameters:  
o #	processes  
o time  
o burst time max range  
o arrival time max range  

- Dashboard-style	visualization  
o GANTT	chart  
o average	waiting	time  
o average	turnaround time  
o total	execution	time  
o process id chart  

# Prerequisites
- Python 2.7+  

# How to setup
- Clone repo

- `python pip install -r requirements.txt`

- `python app.py`

- Navigate to `http://127.0.0.1:5000/`

# Future
- Host on Heroku  
- Make the UI actually look good  
- Color scheme for processes  
