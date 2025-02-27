#include <stdio.h>
#include "esp_timer.h"
#include "esp_mac.h"
#include "spi.h"
#include "gpio.h"
#include "adc.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define portTICK_PERIOD_MS              ((TickType_t) (1000 / configTICK_RATE_HZ))

void app_main(void)
{
    bool cali_ch0;
    bool cali_ch1;
    spi_init();
    XRA1403_init();
    
    adc_init();
    cali_ch0 = adc_calibration_init(ADC_CHANNEL_0);
    cali_ch1 = adc_calibration_init(ADC_CHANNEL_1);
    
    int adc_ch0 = 0;

    //probamos primero el gpio
    XRA1403_set_gpio_level(0,HIGH);
    vTaskDelay(2000/portTICK_PERIOD_MS);
    XRA1403_set_gpio_level(0,LOW);
    
     //probamos el adc
    while(1){
        adc_ch0 = adc_read_channel_cali(ADC_CHANNEL_0,cali_ch0);
        vTaskDelay(pdMS_TO_TICKS(1000));
    }

    spi_deinit();

}
