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
uint8_t flag_main = 0;
uint8_t data_uart[10];

static void state_machine_process_data(void){
    uint8_t gpio_pin;
    uint8_t state;

    if (flag_main == 1){
        if (data_uart[0] == 'G' && data_uart[1] == 'I' && data_uart[2] == 'O'){
            gpio_pin = data_uart[8] - 48;
            state = data_uart[7] - 48;
            XRA1403_set_gpio_level(gpio_pin,state);
            ESP_LOGI(TAG_MAIN, "Activando GPIO %d en estado %d",gpio_pin,state);
            flag_main = 0;
        }
        flag_main = 0;
    }
    
}

void app_main(void)
{
    bool cali_ch0;
    bool cali_ch1;
    spi_init();
    XRA1403_init();
    
    adc_init();
    uart_init();
    cali_ch0 = adc_calibration_init(ADC_CHANNEL_0);
    cali_ch1 = adc_calibration_init(ADC_CHANNEL_1);
    
    flag_main = 0;
    int adc_ch0 = 0;

    //probamos primero el gpio
    XRA1403_set_gpio_level(1,LOW);
    //vTaskDelay(2000/portTICK_PERIOD_MS);
    //XRA1403_set_gpio_level(0,LOW);
    
    // Configure a temporary buffer for the incoming data
    //uint8_t *data = (uint8_t *) malloc(BUFF_SIZE);
     //probamos el adc

     //Prueba del Generador a 23Mhz
    configure_MAX2870_20MHz(void);
    
    while(1){
        //adc_ch0 = adc_read_channel_cali(ADC_CHANNEL_0,cali_ch0);
        //

        // Read data from the UART
        //int len = uart_read_bytes(UART_NUM, data, BUFF_SIZE, 20 / portTICK_PERIOD_MS);
        
        //if (len > 0){
            //data[len] = '\0';
            state_machine_uart();
            //ESP_LOGI(TAG_MAIN, "Recv str: %s",data_uart);
            state_machine_process_data();
            //ESP_LOGI(TAG_MAIN, "Len str: %d", len);

        //}
        
    
        //ESP_LOGI(TAG_MAIN, "ERROR Recv str");
    
        vTaskDelay(pdMS_TO_TICKS(500));
    }

    //spi_deinit();

}
