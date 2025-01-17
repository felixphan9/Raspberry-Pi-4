#include <stdio.h>
#include <stdlib.h>
#include "db_utils.h"
#include <wiringPi.h>
#include <wiringPiI2C.h>
#include <pcf8574.h>
#include <lcd.h>
#include <time.h>

// Define the LCD parameters
#define I2C_ADDR 0x27
#define LCD_ROWS 4
#define LCD_COLS 20

#define BASE 64         // BASE any number above 64
//Define the output pins of the PCF8574, which are directly connected to the LCD2004 pin.
#define RS      BASE+0
#define RW      BASE+1
#define EN      BASE+2
#define LED     BASE+3
#define D4      BASE+4
#define D5      BASE+5
#define D6      BASE+6
#define D7      BASE+7

int lcdhd;// used to handle LCD

int main() {

    wiringPiSetup();  // Initialize wiringPi

    pcf8574Setup(BASE, I2C_ADDR); // Inititalize PCF8574
    for(int i=0 ; i < 8 ; i++ ) {
        pinMode(BASE+i,OUTPUT);     //set PCF8574 port to output mode
    } 

    digitalWrite(LED,HIGH);     // Turn on LCD backlight
    
    digitalWrite(RW,LOW);       // Allow writing to LCD
    lcdhd = lcdInit(4,20,4,RS,EN,D4,D5,D6,D7,0,0,0,0);      // initialize LCD and return “handle” used to handle LCD
    
    if(lcdhd == -1){
        printf("lcdInit failed !");
        return 1;
    }

    float temperature = get_temperature_from_db();
    if (temperature == -1) {
        printf("Failed to get temperature from database.\n");
        return 1;
    }

    // Display temperature on LCD
    lcdPosition(lcdhd, 0, 0); // set the LCD cursor position to (0,0)
    lcdPrintf(lcdhd, "Temperature:");
    lcdPosition(lcdhd, 0, 1); // set the LCD cursor position to (0,1)
    lcdPrintf(lcdhd, "%.2f C", temperature); // print the temperature value on the LCD
    return 0;
}