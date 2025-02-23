#ifndef SPI_H
#define SPI_H

#include <stdio.h>
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/semphr.h"
#include "freertos/queue.h"
#include "driver/spi_master.h"
#include "driver/gpio.h"

#define GPIO_RESET          9
#define GPIO_IRQ            3
#define GPIO_MOSI           7
#define GPIO_MISO           2
#define GPIO_SCLK           6
#define GPIO_CS3            19
#define GPIO_CS2            18
#define SENDER_HOST SPI2_HOST
#define GPIO_MASK 0xFFFE

#define WRITE_CMD   0x0 
#define READ_CMD    0x1 

void spi_init(void);
void spi_deinit(void);
void XRA1403_write_register(uint8_t, uint8_t);
uint8_t XRA1403_read_register(uint8_t);
void MAX2870_write_register(uint8_t, uint32_t);
#endif


