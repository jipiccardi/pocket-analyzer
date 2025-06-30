#ifndef SERIAL_H
#define SERIAL_H

#include <stdio.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"
#include "driver/uart.h"


#define portTICK_PERIOD_MS              ((TickType_t) (1000 / configTICK_RATE_HZ))

#define UART_NUM UART_NUM_0
#define UART_TX_PIN 16
#define UART_RX_PIN 17
#define BUFF_SIZE 1024
#define TASK_MEMORY 1024

#define WAIT_UART 0
#define STX_CHECK 1
#define DATA_CHECK 2
#define ETX_CHECK 3

#define END         0
#define ONEPORT     1
#define TWOPORT     2

#define UART_MODE   0  // 0 = BYTE mode UART      1 = CHAR mode UART

static const char *TAG_UART = "UART";

static uint8_t buff_uart[BUFF_SIZE];
extern uint8_t data_uart[];
extern uint8_t flag_main;

void VNA_uart_init(void);
void VNA_send_data(uint8_t , uint16_t*);
void state_machine_uart(void);

#endif