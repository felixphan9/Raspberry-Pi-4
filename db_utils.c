#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include "mariadb/mysql.h"
#include "db_utils.h"

// Function to Get Current Time
static char* get_current_time() {
    static char buffer[20];
    time_t now = time(NULL);
    struct tm *t = localtime(&now);
    strftime(buffer, sizeof(buffer), "%Y-%m-%d %H:%M:%S", t);
    return buffer;
}

// Function to insert temperature into MariaDB
void insert_temperature_to_db(float temperature) {
    MYSQL *conn;

    const char *server = "localhost";
    const char *user = "myuser";     // Replace with your MariaDB username
    const char *password = "123"; // Replace with your MariaDB password
    const char *database = "sensor_data";  // Replace with your database name

    // Initialize connection
    conn = mysql_init(NULL);
    if (conn == NULL) {
        fprintf(stderr, "mysql_init() failed\n");
        return;
    }

    // Connect to database
    if (mysql_real_connect(conn, server, user, password, database, 0, NULL, 0) == NULL) {
        fprintf(stderr, "mysql_real_connect() failed: %s\n", mysql_error(conn));
        mysql_close(conn);
        return;
    }

    // Create table if it doesn't exist
    const char *create_table_query = 
        "CREATE TABLE IF NOT EXISTS temperature_logs ("
        "id INT AUTO_INCREMENT PRIMARY KEY, "
        "timestamp DATETIME, "
        "temperature FLOAT)";
    if (mysql_query(conn, create_table_query)) {
        fprintf(stderr, "Table creation failed: %s\n", mysql_error(conn));
    }

    // Insert data
    char insert_query[256];
    snprintf(insert_query, sizeof(insert_query), 
             "INSERT INTO temperature_logs (timestamp, temperature) VALUES ('%s', %.2f)", 
             get_current_time(), temperature);

    if (mysql_query(conn, insert_query)) {
        fprintf(stderr, "Insert failed: %s\n", mysql_error(conn));
    } else {
        printf("Temperature data inserted into database successfully.\n");
    }

    // Close the connection
    mysql_close(conn);
}
