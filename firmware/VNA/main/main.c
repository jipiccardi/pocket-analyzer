#include <stdio.h>
#include "esp_timer.h"
#include "esp_mac.h"
#include "spi.h"
#include "gpio.h"
#include "adc.h"
#include "serial.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#define portTICK_PERIOD_MS              ((TickType_t) (1000 / configTICK_RATE_HZ))

static const char *TAG_MAIN = "MAIN";

void app_main(void)
{
    bool cali_ch0;
    bool cali_ch1;
    //spi_init();
    //XRA1403_init();
    
    adc_init();
    uart_init();
    cali_ch0 = adc_calibration_init(ADC_CHANNEL_0);
    cali_ch1 = adc_calibration_init(ADC_CHANNEL_1);
    
    int adc_ch0 = 0;

    //probamos primero el gpio
    //XRA1403_set_gpio_level(0,HIGH);
    //vTaskDelay(2000/portTICK_PERIOD_MS);
    //XRA1403_set_gpio_level(0,LOW);
    
    // Configure a temporary buffer for the incoming data
    uint8_t *data = (uint8_t *) malloc(BUFF_SIZE);
     //probamos el adc
    while(1){
        //adc_ch0 = adc_read_channel_cali(ADC_CHANNEL_0,cali_ch0);
        //

        // Read data from the UART
        int len = uart_read_bytes(UART_NUM, data, BUFF_SIZE, 20 / portTICK_PERIOD_MS);
        
        
        data[len] = '\0';
        ESP_LOGI(TAG_MAIN, "Recv str: %s", (char *) data);

    
        //ESP_LOGI(TAG_MAIN, "ERROR Recv str");
    
        vTaskDelay(pdMS_TO_TICKS(2000));
    }

    //spi_deinit();

}
