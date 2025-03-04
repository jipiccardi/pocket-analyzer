#ifndef SERIAL_H
#define SERIAL_H

#include <stdio.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"
#include "driver/uart.h"

#define UART_NUM UART_NUM_0
#define UART_TX_PIN 16
#define UART_RX_PIN 17
#define BUFF_SIZE 1024
#define TASK_MEMORY 1024

static const char *TAG_UART = "UART";
void uart_init(void);

#endif