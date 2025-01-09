from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import subprocess
from datetime import datetime
import schedule  
import logging
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://myuser:123@localhost/sensor_data'  # MariaDB example
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'mysecretkey'
db = SQLAlchemy(app)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Function to run the C program and fetch the latest temperature from the database
def get_temperature():
    try:
        # Run the C program to read the temperature and insert it into the database
        result = subprocess.run(["./read_temp"], capture_output=True, text=True)

        # Connect to the database
        conn = mysql.connector.connect(
            host="localhost",
            user="myuser",
            password="123",
            database="sensor_data"
        )

        # Create a cursor object to execute queries
        cursor = conn.cursor()
        
        # Define the SQL query to fetch the most recent temperature data
        query = "SELECT temperature FROM temperature_logs ORDER BY timestamp DESC LIMIT 1"
        
        # Execute the query
        cursor.execute(query)

        # Fetch the most recent result
        result = cursor.fetchone()
        
        # Close the cursor and connection
        cursor.close()
        conn.close()
        
        # Log the fetched temperature
        if result:
            logging.debug(f"Fetched temperature from database: {result[0]}")
            return result[0]
        else:
            logging.debug("No temperature record found in the database.")
            return None
        
    except Exception as e:
        logging.error(f"Error in get_temperature: {e}")
        return None

# Database Model
class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    temperature = db.Column(db.Float, nullable=False)

# Create the database
with app.app_context():
    db.create_all()

# Schedule the temperature reading function
schedule.every(60).seconds.do(get_temperature)

# Home route to display the latest temperature
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Run pending scheduled tasks
    schedule.run_pending()
    
    temperature = get_temperature()
    if temperature:
        sensor_data = {"temperature": temperature}
        logging.debug(f"Temperature to be displayed: {temperature}")
    else:
        sensor_data = {"error": "Failed to read temperature"}
        logging.debug("Failed to read temperature")
    return render_template('index.html', sensor_data=sensor_data)

# API route to fetch the latest temperature
@app.route('/api/temperature', methods=['GET'])
def api_temperature():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    temperature = get_temperature()
    if temperature:
        return jsonify({"temperature": temperature})
    else:
        return jsonify({"error": "Failed to read temperature"}), 500

# API route to fetch historical temperature data
@app.route('/api/temperature_history', methods=['GET'])
def api_temperature_history():
    records = SensorData.query.order_by(SensorData.timestamp.desc()).limit(10).all()
    history = [{"timestamp": record.timestamp, "temperature": record.temperature} for record in records]
    return jsonify(history)

@app.route('/login', methods=['GET', 'POST'])
def login():
    static_username = 'admin'
    static_password = '123'

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == static_username and password == static_password:
            session['user_id'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Login failed. Check your username and/or password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)