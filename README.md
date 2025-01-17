# Raspberry-Pi-4
This is a project for fetching temperature from BMP280 sensor then displaying it on LCD2004A.

Make sure to install wiringPi library `git clone https://github.com/WiringPi/WiringPi.git`
- 
To compile reading temperature program:

``` 
gcc -o main read_temp.c db_utils.c -lmariadb
```
To compile the LCD program:

```
gcc -o lcd lcd.c db_utils.c -lmariadb -I/home/pi/WiringPi/devLib -L/home/pi/WiringPi/devLib -lwiringPi -lwiringPiDev
```