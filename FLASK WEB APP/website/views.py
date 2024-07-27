from flask import Blueprint, render_template,jsonify, flash, request
from flask_login import login_user, login_required, current_user
from mq6_module import mq6_modules
from power import powers
import RPi.GPIO as GPIO
from .models import GasReading, CurrentReading
from . import db
from flask import Flask
from flask_mail import Mail, Message
from flask import current_app
from website.email import send_email
from flask_mail import Message

from . import mail

views = Blueprint('views', __name__)
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


    



@views.route('/')
@login_required
def home():
    gas_value = mq6_modules[0].mq.MQPercentage()["GAS_LPG"]
    current_value = powers[0].get_electricalsensor_readings()

    if gas_value >= 0.2:
        flash('High gas value detected!', 'danger')  # Add flash message
        
    if current_value is not None and float(current_value) >= 0.2:
        flash('High current value detected!', 'danger') 
        

    return render_template("home.html", user=current_user)



@views.route('/gas_value')
def gas_value():
    gas_value = mq6_modules[0].mq.MQPercentage()["GAS_LPG"]   # Assuming the first instance is used
    if gas_value >= 0.2:
        gas_reading = GasReading(value=gas_value)
        db.session.add(gas_reading)
        db.session.commit()
        send_email('High Gas Value Alert', ' Gas leak detected in your residence. Immediate action required to ensure safety! ', current_user.email)
        
    return jsonify({'gas_value': gas_value})
    

# API endpoint to control LED, buzzer, and solenoid valve based on gas value
@views.route('/control')
def control_led_buzzer_valve():
    gas_value = mq6_modules[0].mq.MQPercentage()["GAS_LPG"]  # Assuming the first instance is used
    valve_status = ''
    if gas_value >= 0.2:
        GPIO.output(LED_Pin, GPIO.HIGH)  # Turn on LED
        GPIO.output(Buzzer_Pin, GPIO.HIGH)  # Turn on Buzzer
        GPIO.output(Solenoid_Pin, GPIO.LOW)  # Close the valve
        valve_status = 'Shutdown'  # Valve is shut down
        
        
    else:
        GPIO.output(LED_Pin, GPIO.LOW)  # Turn off LED
        GPIO.output(Buzzer_Pin, GPIO.LOW)  # Turn off Buzzer
        GPIO.output(Solenoid_Pin, GPIO.HIGH)  # Open the valve
        valve_status = 'Open'  # Valve is open

    return jsonify({'gas_value': gas_value, 'valve_status': valve_status})

@views.route('/current_value')
def current_value():
    current_value = powers[0].get_electricalsensor_readings()
    if current_value is not None:
        current_value_float = float(current_value)  # Convert current_value to float
        
        # Display the current value continuously
        response = {'current_value': current_value}

        # Store in the database if the value is greater than or equal to 0.2
        if current_value_float >= 0.2:
            current_reading = CurrentReading(value=current_value_float)
            db.session.add(current_reading)
            db.session.commit()
            send_email('High Current Value Alert', 'High current detected in your residence. Immediate action required to ensure safety!', current_user.email)

        return jsonify(response)
    else:
        return jsonify({'current_value': 'Unavailable'})
    
@views.route('/control_current')
def control_led_valve():
    current_value = powers[0].get_electricalsensor_readings()
    
    if current_value is not None:  # Check if the value is not None
        try:
            current_value = float(current_value)
            contactor_status = ''
            ledb_status = ''
            buzzerb_status = ''
            
            if current_value >= 0.2:
                contactor_status = 'Shutdown'
                ledb_status = 'On'
                buzzerb_status = 'On'

                
            else:
                contactor_status = 'Open'
                ledb_status = 'Off'
                buzzerb_status = 'off'
            return jsonify({'current_value': current_value, 'contactor_status': contactor_status, 'ledb_status': ledb_status, 'buzzerb_status': buzzerb_status})
        except ValueError as e:
            # Handle the case where the conversion to float fails
            return jsonify({'error': 'Unable to convert value to float'})
    else:
        return jsonify({'current_value': 'Unavailable'})
