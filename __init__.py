from flask import Flask, session, render_template, request, url_for, redirect, json, Response, flash
from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from control import Control, Climate, Mqtt_ServerA, Light, WriteOut, MESSAGE
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import threading
import time, os, atexit, sched

# Create app, initialize database, create control instance
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

Bootstrap(app)
db = SQLAlchemy(app)
controler = Control()
climateData = Climate()
lights = Light()
writeOut = WriteOut()
mqtt_data = Mqtt_ServerA()
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Sensor data file
sensor_data = "sensor_data.txt"

"""while True:
    print("Message Length: {}".format(len(MESSAGE)))
    time.sleep(4.0)"""

# Create database class
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def redirect_dest(fallback):
    dest = request.args.get('next')
    try:
        return redirect(dest)
    except:
        return redirect(fallback)

# Create form classes
class LoginForm(Form):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('Remember me')

class RegisterForm(Form):
    email = StringField('Email', validators=[InputRequired(), Email(message='Invalid Email'), Length(max=50)])
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])

# Error handling
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")

# Render homepage
@app.route('/')
def homepage():
    return render_template('index.html')

# Render login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                flash('Logged in!')
                return redirect_dest(fallback=url_for('homepage'))
        flash('Invalid credentials...')
        return render_template('login.html', form=form)
    return render_template('login.html', form=form)

# Logout user
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('homepage'))

# Render register page
@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('New user created!')
        return render_template('panel.html')
    return render_template('register.html', form=form)

# Render admin control panel
@app.route('/panel')
@login_required
def admin():
    return render_template('panel.html')

# Render light compensation slider
@app.route('/light', methods=['GET', 'POST'])
@login_required
def light():
    return render_template('light.html')

# Render charts page
@app.route('/charts')
def charts():
    return render_template('charts.html')

# Render temperature chart
@app.route('/temperature')
def temp():
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, "static/data/temperature", "0.json")
    data = json.load(open(json_url))
    return render_template('data/temperature/index.html', data=data)

# Render humidity chart
@app.route('/humidity')
def humidity():
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, "static/data/humidity", "0.json")
    data = json.load(open(json_url))
    return render_template('data/humidity/index.html', data=data)

# Render pressure chart
@app.route('/pressure')
def pressure():
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, "static/data/pressure", "0.json")
    data = json.load(open(json_url))
    return render_template('data/pressure/index.html', data=data)

# Render air flow chart
@app.route('/airflow')
def airflow():
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, "static/data/airflow", "0.json")
    data = json.load(open(json_url))
    return render_template('data/airflow/index.html', data=data)

# Render light Intensity chart
@app.route('/intensity')
def intensity():
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, "static/data/light", "0.json")
    data = json.load(open(json_url))
    return render_template('data/light/index.html', data=data)

# Render light Intensity chart
@app.route('/frequencies')
def frequencies():
    return render_template('data/frequencies/index.html')

# Start Of chart making process
# Lists/Variables for building charts
key = ["temperature","humidity","pressure","windSpeed","lux","timestamp"]
doValues  = [0,0,0,0,0,0]
tempJson  = "static/data/temperature"
humidJson = "static/data/humidity"
pressJson = "static/data/pressure"
winspJson = "static/data/airflow"
luxJson   = "static/data/light"
filename  = "0.json"
temp  = []
humid = []
press = []
winsp = []
lux   = []
#times = []
"""
# Function that appends new data to JSON files used by charts
def writeJSON(path, fileName, data):
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    writePath = os.path.join(SITE_ROOT, path, fileName)
    with open(writePath, 'w') as file:
        print(data)
        json.dump(data, file)"""

# Scheduled function that manages new data and calls "writeJSON"
def doCharts(values):
    sizeA = len(MESSAGE)
    delta = sizeA - values[0]
    index = 0
    for x in range(delta):
        index = x + (values[0] - 0)
        if (index):
            temp.append([MESSAGE[index][key[5]],MESSAGE[index][key[0]]])
            humid.append([MESSAGE[index][key[5]],MESSAGE[index][key[1]]])
            press.append([MESSAGE[index][key[5]],MESSAGE[index][key[2]]])
            winsp.append([MESSAGE[index][key[5]],MESSAGE[index][key[3]]])
            #lux.append([MESSAGE[index][key[5]],MESSAGE[index][key[4]]])
            #print(MESSAGE[index][key[5]])
    if (index):
        if(len(temp) > values[1]):
            writeOut.writeJSON(tempJson, filename, temp)
            values[1] = len(temp)
        if(len(humid) > values[2]):
            writeOut.writeJSON(humidJson, filename, humid)
            values[2] = len(humid)
        if(len(press) > values[3]):
            writeOut.writeJSON(pressJson, filename, press)
            values[3] = len(press)
        if(len(winsp) > values[4]):
            writeOut.writeJSON(winspJson, filename, winsp)
            values[4] = len(winsp)
        """if(len(lux) > values[5]):
            writeOut.writeJSON(luxJson, filename, press)
            values[5] = len(lux)"""
            #print("Temp data made: {}".format(winsp))
    values[0] = sizeA
    #return(values)

# Function that calls function "doCharts"
STOP = True
def exitHandler():
    STOP = False
def makeCharts():
    def callCharts(Sc):
        #time.sleep(5)
        print("Doing Charts")
        doCharts(doValues)
        Sc.enter(10, 5, callCharts, (Sc,))
    S = sched.scheduler(time.time, time.sleep)
    S.enter(5, 1, callCharts, (S,))
    S.run()

T = threading.Thread(target=makeCharts, args=())
T.daemon = True
T.start()
#atexit.register(lambda: exitHandler())

"""scheduler = BackgroundScheduler()
scheduler.start()
scheduler.add_job(
    func = makeCharts,
    trigger = IntervalTrigger(seconds = 5),
    id='write_out',
    name='Update charts',
    replace_existing=True)
# Shut down the scheduler when exiting the app"""

# End Of chart making process

# SSE (Server Sent Events)
# Maintains dashboard climate data
@app.route('/climate')
def climate():
    def get_climate_values():
        """writeData = "{},{},{},{}".format(data[key[0]],data[key[1]],
        data[key[2]],data[key[3]],data[key[4]])
        temp  = []
        humid = []
        press = []
        winsp = []
        lux   = []
        times = []"""

        key = ["temperature","humidity","pressure","windSpeed","lux","timestamp"]
        luxFile = "lux.txt"
        while True:
            sizeB = 0
            sizeA = len(MESSAGE)
            data = MESSAGE[sizeA - 1]
            with open(luxFile) as file:
                for line in file:
                    line.strip()
                    lux = int(line)
                    print("Look here: {}".format(lux))
                    time.sleep(5)
            writeData = "{},{},{},{},{}".format(data[key[0]],data[key[1]],
            data[key[2]],data[key[3]],data[key[4]])
            yield('data: {}\n\n'.format(writeData))
            time.sleep(1)
    return Response(get_climate_values(), mimetype='text/event-stream')

# Read device state for admin panel
@app.route('/read-state')
def readState():
    def getState():
        while True:
            data = controler.read_sensorA()
            yield('data: {}\n\n'.format(data))
            time.sleep(1.0)
    return Response(getState(), mimetype='text/event-stream')

# Set device state for admin panel
@app.route('/device-b/<int:device_state>', methods=['POST'])
def deviceB(device_state):
    # Check input and write to deviceA
    if device_state == 0:
        controler.write_deviceA(False)
    elif device_state == 1:
        controler.write_deviceA(True)
    else:
        return ("Lolwhat?!", 400)
    return ("Good Job!", 204)

# Set state of LED strip
@app.route('/led-strip/<key>', methods=['POST'])
def ledStrip(key):
    # Check input and write to deviceA
    key = map(int, key.split(','))
    lights.rgb(key)
    print(key)
    return ("Good Job!", 204)

# Run app
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=False, use_reloader=False, threaded=True)
