#include <stdio.h>
#include <unistd.h>
#include "stdint.h"
#include "gpio.h"
#include "vna_sys_res.h"

#define BLINK_T 1000

static uint8_t vna_conn = 1, vna_meas = 0;

void green_led_task (void *pvParameter){
    uint8_t conn, meas, gled_state=0;
    while (1){
        /*VNA Connected*/
    xSemaphoreTake(xGreenLedMutex, portMAX_DELAY);
    conn = vna_conn;
    meas = vna_meas;
    xSemaphoreGive(xGreenLedMutex);
        if (conn){
            if (!meas){
                gled_state = !gled_state;
                gpio_set_level (LED_VERDE,gled_state);
                vTaskDelay(BLINK_T/portTICK_PERIOD_MS); 
            }
            else{
                gpio_set_level (LED_VERDE,1);
                vTaskSuspend(NULL);
            }
        }else vTaskDelay(100/portTICK_PERIOD_MS); 
    }
}