from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
import subprocess
from datetime import datetime
import schedule  

app = Flask(__name__, template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sensor_data.db'  # SQLite example
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Function to read temperature from the C program
def get_temperature():
    try:
        # Run the C program to read the temperature
        result = subprocess.run(["./read_temp"], capture_output=True, text=True)
        if result.returncode == 0:
            # Extract the temperature from the C program's output
            output = result.stdout.strip()
            if "Temperature:" in output:
                temperature = output.split("Temperature:")[1].strip()
                # Remove the oC and convert to float
                temperature = float(temperature.replace(' °C', ''))
                return temperature
            else:
                return None
        else:
            return None
    except Exception as e:
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
schedule.every(5).seconds.do(get_temperature)

# Home route to display the latest temperature
@app.route('/')
def index():
    # Run pending scheduled tasks
    schedule.run_pending()
    
    temperature = get_temperature()
    if temperature:
        #Save the temperature to the database
        new_data = SensorData(temperature=temperature)
        db.session.add(new_data)
        db.session.commit()
        sensor_data = {"temperature": temperature}
    else:
        sensor_data = {"error": "Failed to read temperature"}
    return render_template('index.html', sensor_data=sensor_data)

# API route to fetch the latest temperature
@app.route('/api/temperature', methods=['GET'])
def api_temperature():
    temperature = get_temperature()
    if temperature:
        #Save the temperature to the database
        new_data = SensorData(temperature=temperature)
        db.session.add(new_data)
        db.session.commit()
        return jsonify({"temperature": temperature})
    else:
        return jsonify({"error": "Failed to read temperature"}), 500

# API route to fetch historical temperature data
@app.route('/api/temperature_history', methods=['GET'])
def api_temperature_history():
    records = SensorData.query.order_by(SensorData.timestamp.desc()).limit(10).all()
    history = [{"timestamp": record.timestamp, "temperature": record.temperature} for record in records]
    return jsonify(history)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)