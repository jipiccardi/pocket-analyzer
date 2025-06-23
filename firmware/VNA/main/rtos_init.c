#include "vna_sys_res.h"

SemaphoreHandle_t xGreenLedMutex = NULL;
TaskHandle_t xGreenLedTaskHandle = NULL;


void rtos_init(void){

    /*MUTEX & Sem definitios*/
    xGreenLedMutex = xSemaphoreCreateMutex();


    /*TASK init*/
    xTaskCreate(green_led_task, "green led", 2048, NULL, 1, &xGreenLedTaskHandle);
}