#ifndef VNA_SYS_RES_H
#define VNA_SYS_RES_H

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/semphr.h"

extern SemaphoreHandle_t xGreenLedMutex;
extern SemaphoreHandle_t xDataBufferRXMutex;
extern SemaphoreHandle_t xMeasParamMutex;


extern TaskHandle_t xGreenLedTaskHandle;
extern TaskHandle_t xSerialRxTaskHandle;
extern TaskHandle_t xModeSelTaskHandle;
extern TaskHandle_t xMeas1PTaskHandle;
TaskHandle_t xMeas2PTaskHandle = NULL;



void green_led_task (void *);
void SM_serial_rx_task (void *);
void mode_sel_task (void *);
void rtos_init (void);
void meas_1p_task (void);
void meas_2p_task (void);

#endif