import json
from flask import Flask, render_template, request, jsonify,redirect, Response
from flask_socketio import SocketIO, emit
from threading import Lock
from mq6_module import mq6_modules
import RPi.GPIO as GPIO
from datetime import datetime
from power import powers
from website import create_app
from website.views import views
from website.models import db, GasReading, CurrentReading




app = create_app()

# GPIO Pin Configuration

LED_Pin = 23
Buzzer_Pin = 26
Solenoid_Pin = 12


# Setup GPIO
GPIO.setmode(GPIO.BCM)

GPIO.setup(LED_Pin, GPIO.OUT)
GPIO.setup(Buzzer_Pin, GPIO.OUT)
GPIO.setup(Solenoid_Pin, GPIO.OUT)


# Set the initial state of the GPIO pins
GPIO.output(LED_Pin, GPIO.LOW)
GPIO.output(Buzzer_Pin, GPIO.LOW)
GPIO.output(Solenoid_Pin, GPIO.HIGH)

thread = None
thread_lock = Lock()


app.config["SECRET_KEY"] = "group3"
socketio = SocketIO(app, cors_allowed_origins="*")


"""
Background Thread
"""
def background_thread():
    while True:
        for mq6 in mq6_modules:
            gasvalue = mq6.get_sensor_readings()
            
            sensor_readings = {
                
                "gas_value": gasvalue,
                 
            }
            sensor_json = json.dumps(sensor_readings)
            socketio.emit("updateSensorData", json.dumps(sensor_readings))
            socketio.sleep(1)

        for power_instance in powers:
            electrical_sensor_value = power_instance.get_electricalsensor_readings()
            electricalsensor_readings = {
                "electrical_sensor_value": electrical_sensor_value,
                }
            sensor_json = json.dumps(electricalsensor_readings)
            socketio.emit('updateSensorData', json.dumps(electricalsensor_readings))
            socketio.sleep(1)


"""
Get current date time
"""
def get_current_datetime():
    now = datetime.now()
    return now.strftime("%m/%d/%Y %H:%M:%S")


"""
Generate random sequence of sensor values and send it to our clients
"""
def background_thread():
    print("Generating sensor values")
    while True:
        gas_sensor_value = mq6_modules[0].mq.MQPercentage()["GAS_LPG"] 
        current_value = powers[0].get_electricalsensor_readings()

         
        
        

        socketio.emit('updateSensorData', {'value': gas_sensor_value, "date": get_current_datetime()})
        socketio.emit('updateElectricalData', {'value': current_value, "date": get_current_datetime()})
        socketio.sleep(1)
       


    



"""
Decorator for connect
"""


@socketio.on("connect")
def connect():
    global thread
    print("Client connected")

    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)
            


"""
Decorator for disconnect
"""
@socketio.on("disconnect")
def disconnect():
    print("Client disconnected", request.sid)

if __name__ == "__main__":
    socketio.run(app, port=5000, host="0.0.0.0", debug=True, )
    
    

