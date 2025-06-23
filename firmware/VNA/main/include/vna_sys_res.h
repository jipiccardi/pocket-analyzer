#ifndef VNA_SYS_RES_H
#define VNA_SYS_RES_H

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/semphr.h"

extern SemaphoreHandle_t xGreenLedMutex;
extern TaskHandle_t xGreenLedTaskHandle;


void green_led_task (void *);
void rtos_init (void);

#endif