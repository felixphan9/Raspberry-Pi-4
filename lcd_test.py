from RPLCD.i2c import CharLCD
import time

# Set up LCD (replace 0x27 with your actual I2C address)
lcd = CharLCD('PCF8574', 0x27)

# Function to read CPU temperature
def read_cpu_temp():
    with open("/sys/class/thermal/thermal_zone0/temp", "r") as temp_file:
        temp = int(temp_file.read()) / 1000  # Convert to Celsius
    return temp

try:
    # Clear the LCD screen
    lcd.clear()

    while True:
        # Get the current CPU temperature
        cpu_temp = read_cpu_temp()
        
        # Display the CPU temperature on the LCD
        lcd.write_string(f"CPU Temp: {cpu_temp:.1f}C")
        
        # Wait for 2 seconds before updating
        time.sleep(2)

finally:
    # Clear the LCD and close
    lcd.clear()
    lcd.close()
