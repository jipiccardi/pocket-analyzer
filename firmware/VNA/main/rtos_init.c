#include "vna_sys_res.h"

SemaphoreHandle_t xGreenLedMutex = NULL;
SemaphoreHandle_t xDataBufferRXMutex = NULL;
SemaphoreHandle_t xMeasParamMutex = NULL;


TaskHandle_t xGreenLedTaskHandle = NULL;
TaskHandle_t xSerialRxTaskHandle = NULL;
TaskHandle_t xModeSelTaskHandle = NULL;
TaskHandle_t xMeas1PTaskHandle = NULL;
TaskHandle_t xMeas2PTaskHandle = NULL;


void rtos_init(void){

    /*MUTEX & Sem definitios*/
    xGreenLedMutex = xSemaphoreCreateMutex();
    xSerialRxTaskHandle = xSemaphoreCreateMutex();

    /*TASK init*/
    xTaskCreate(green_led_task, "green led", 2048, NULL, 1, &xGreenLedTaskHandle);
    xTaskCreate(SM_serial_rx_task, "rx data task", 2048, NULL, 1, &xSerialRxTaskHandle);
    xTaskCreate(mode_sel_task, "mode selection task", 2048, NULL, 1, &xModeSelTaskHandle);
    xTaskCreate(meas_1p_task, "1Port Measurement", 2048, NULL, 1, &xMeas1PTaskHandle);
    xTaskCreate(meas_2p_task, "1Port Measurement", 2048, NULL, 1, &xMeas2PTaskHandle);
}