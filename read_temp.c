#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/i2c-dev.h>
#include <time.h>

// BMP280 I2C Address
#define BMP280_I2C_ADDR 0x76

// BMP280 Registers
#define REG_ID 0xD0
#define REG_CTRL_MEAS 0xF4
#define REG_TEMP_DATA 0xFA
#define REG_CALIBRATION_START 0x88

// Calibration coefficients
uint16_t dig_T1;
int16_t dig_T2, dig_T3;

// Function to convert raw temperature to Celsius
float convert_temperature(int32_t adc_T) {
    int32_t var1, var2, t_fine;
    float temperature;

    var1 = ((((adc_T >> 3) - ((int32_t)dig_T1 << 1))) * ((int32_t)dig_T2)) >> 11;
    var2 = (((((adc_T >> 4) - ((int32_t)dig_T1)) * ((adc_T >> 4) - ((int32_t)dig_T1))) >> 12) * ((int32_t)dig_T3)) >> 14;
    t_fine = var1 + var2;
    temperature = (t_fine * 5 + 128) >> 8;
    return temperature / 100.0; // Convert to Celsius
}

// Function to read a register
int read_register(int file, uint8_t reg, uint8_t *buf, int len) {
    if (write(file, &reg, 1) != 1) {
        perror("Failed to write register address");
        return -1;
    }
    if (read(file, buf, len) != len) {
        perror("Failed to read data");
        return -1;
    }
    return 0;
}

// Function to write a register
int write_register(int file, uint8_t reg, uint8_t value) {
    uint8_t buf[2] = {reg, value};
    if (write(file, buf, 2) != 2) {
        perror("Failed to write data");
        return -1;
    }
    return 0;
}

// Function to Get Current Time
char* get_current_time() {
    static char buffer[20];  // Static so it can be used outside this function
    time_t now = time(NULL);
    struct tm *t = localtime(&now);
    strftime(buffer, sizeof(buffer), "%Y-%m-%d %H:%M:%S", t);
    return buffer;
}

// Function to log temperature to the File
void log_temperature(float temperature) {
    FILE *file = fopen("temperature.log", "a");  // Open in append mode
    if (file == NULL) {
        perror("Failed to open log file");
        return;
    }

    // Append timestamp and temperature to the file
    fprintf(file, "%s - Temperature: %.2f°C\n", get_current_time(), temperature);

    fclose(file);  // Close the file to save changes
}

int main() {
    const char *i2c_device = "/dev/i2c-1"; // I2C bus
    int file;

    // Open the I2C device
    if ((file = open(i2c_device, O_RDWR)) < 0) {
        perror("Failed to open I2C bus");
        exit(1);
    }

    // Set the I2C slave address
    if (ioctl(file, I2C_SLAVE, BMP280_I2C_ADDR) < 0) {
        perror("Failed to set I2C address");
        close(file);
        exit(1);
    }

    // Check the BMP280 ID
    uint8_t chip_id;
    if (read_register(file, REG_ID, &chip_id, 1) < 0) {
        close(file);
        exit(1);
    }

    // Read calibration data
    uint8_t calib_data[24];
    if (read_register(file, REG_CALIBRATION_START, calib_data, 24) < 0) {
        close(file);
        exit(1);
    }
        // Extract calibration coefficients
    dig_T1 = (calib_data[1] << 8) | calib_data[0];
    dig_T2 = (calib_data[3] << 8) | calib_data[2];
    dig_T3 = (calib_data[5] << 8) | calib_data[4];

    // Configure the BMP280 (Normal mode, temperature oversampling x1)
    if (write_register(file, REG_CTRL_MEAS, 0x25) < 0) { // 0x25 = Temp oversampling x1, normal mode
        close(file);
        exit(1);
    }

    // Wait for measurement to complete
    usleep(100000); // 100ms delay

    // Read temperature data
    uint8_t data[3];
    if (read_register(file, REG_TEMP_DATA, data, 3) < 0) {
        close(file);
        exit(1);
    }

    // Combine raw temperature data
    int32_t raw_temp = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4);
    
    // printf("Raw Temperature: %d\n", raw_temp);

    // Close the I2C device
  
   close(file);
    
    float temperature = convert_temperature(raw_temp);

    // Log the temperature
    // log_temperature(temperature);

    // printf("Temperature logged successfully.\n");

    printf("Temperature: %.2f °C\n", temperature);
    
    return 0;
}



