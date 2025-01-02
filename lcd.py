from RPLCD.i2c import CharLCD
import time
import subprocess
import mysql.connector

# Set up LCD (replace 0x27 with your actual I2C address)
lcd = CharLCD('PCF8574', 0x27)

# Function to read the most recent temperature from the database
def read_temperature_from_db():
    # Connect to the database (adjust the credentials)
    conn = mysql.connector.connect(
        host="localhost",      # Database host (can be 'localhost' for local database)
        user="myuser",           # Database username
        password="123",  # Database password
        database="sensor_data"  # Name of your database
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
    
    # Return the temperature if available, else None
    if result:
        return result[0]
    else:
        return None

# Function to run the ./read_temp application (without reading output)
def run_read_temp_application():
    try:
        # Run the external application
        subprocess.run(["./read_temp"], check=True)
    except Exception as e:
        print("Error running ./read_temp:", e)

try:
    # Clear the LCD screen and turn on the backlight
    lcd.clear()
    lcd.backlight_enabled = True

    while True:
        # Run the ./read_temp application first
        run_read_temp_application()
        
        # Now, fetch the most recent temperature from the database
        temperature = read_temperature_from_db()
        
        # Check if temperature data is available
        if temperature is not None:
            # Display the temperature on the LCD
            lcd.clear()  # Clear screen before writing new data
            lcd.write_string(f"Temp: {temperature:.2f}C")
        else:
            lcd.clear()
            lcd.write_string("No data available")
        
        # Wait for 2 seconds before updating
        time.sleep(2)

finally:
    # Clear the LCD and close
    lcd.clear()
    lcd.close()