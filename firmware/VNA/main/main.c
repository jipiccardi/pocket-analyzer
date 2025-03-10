#include <stdio.h>
#include "stdint.h"
#include "esp_timer.h"
#include "esp_mac.h"
#include "spi.h"
#include "gpio.h"
#include "adc.h"
#include "serial.h"
#include "PR_max2870.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#define portTICK_PERIOD_MS              ((TickType_t) (1000 / configTICK_RATE_HZ))
#define LED_VERDE 23


/* INICIO (Pasar esta seccion a otro archivo)*/
void VNA_path(uint8_t path);

#define SWT_A_1     3
#define SWT_A_2     4
#define SWT_B_1     5
#define SWT_B_2     6
#define SWT_C_1     7
#define SWT_C_2     8

#define S11_PATH    0
/*FIN*/

static const char *TAG_MAIN = "MAIN";
uint8_t flag_main = 0;
uint8_t data_uart[10];
bool cali_ch0;
bool cali_ch1;

static void state_machine_process_data(void){
    uint8_t gpio_pin;
    uint8_t state;
    int mag_value_S11=0, pha_value_S11, frq_value;
    char mag_value_S11_str[5], pha_value_S11_str[5], frq_value_str[6];
    char test_str[27];
    char end_str[] = "Termine\n";


    if (flag_main == 1){
        if (data_uart[0] == 'G' && data_uart[1] == 'I' && data_uart[2] == 'O'){
            gpio_pin = data_uart[8] - 48;
            state = data_uart[7] - 48;
            XRA1403_set_gpio_level(gpio_pin,state);
            ESP_LOGI(TAG_MAIN, "Activando GPIO %d en estado %d",gpio_pin,state);
            flag_main = 0;
        }
        else if (data_uart[0] == 'F' && data_uart[1] == 'R' && data_uart[2] == 'Q'){
            char aux[6];
            int n = 0;
            for(int i=0;i<6;i++)
                aux[i] = data_uart[i+3];
            n = atoi(aux);
            set_FRQ((uint32_t)n);
            flag_main = 0;
        }
        else if (data_uart[0] == 'M' && data_uart[1] == 'T' && data_uart[2] == 'C'){
            int n = 1;
            // Write data to UART.
            uart_flush(UART_NUM);
            
            for(int i=0;i<1000;i++){
                VNA_path(S11_PATH);
                mag_value_S11 = adc_read_channel_cali(ADC_CHANNEL_0,cali_ch0);
                pha_value_S11 = adc_read_channel_cali(ADC_CHANNEL_1,cali_ch1);
                frq_value = get_FRQ();

                strcpy(test_str, "\x02VAL");
                sprintf(mag_value_S11_str, "%04d", mag_value_S11);
                sprintf(pha_value_S11_str, "%04d", pha_value_S11);
                sprintf(frq_value_str, "%05d", frq_value);

                strcat(test_str,frq_value_str);
                strcat(test_str,mag_value_S11_str);
                strcat(test_str,pha_value_S11_str);
                strcat(test_str,"ccccdddd");
                strcat(test_str,"\x03");

                uart_write_bytes(UART_NUM, test_str, strlen(test_str));
                //vTaskDelay(50/portTICK_PERIOD_MS);
            }
            uart_write_bytes(UART_NUM, end_str, strlen(end_str));
            //uart_flush(UART_NUM);
            //uart_write_bytes(UART_NUM, test_str, strlen(test_str));
            //ESP_ERROR_CHECK(uart_wait_tx_done(UART_NUM, 100)); // wait timeout is 100 RTOS ticks (TickType_t)
            //n = atoi(data_uart[8]);
            
            //ESP_LOGI(TAG_MAIN, "Recibimos el Match: %d",n);
            flag_main = 0;
        }

        flag_main = 0;
    }
}

void VNA_path(uint8_t path){
    switch (path){
        case S11_PATH:
            XRA1403_set_gpio_level(SWT_A_2, LOW);
            XRA1403_set_gpio_level(SWT_A_1, HIGH);
            XRA1403_set_gpio_level(SWT_B_2, LOW);
            XRA1403_set_gpio_level(SWT_B_1, HIGH);
            XRA1403_set_gpio_level(SWT_C_2, LOW);
            XRA1403_set_gpio_level(SWT_C_1, HIGH);
            break;
    }
}


void app_main(void)
{

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
    //MAX2870_init();
    //configure_MAX2870_20MHz();
    init_FRQ_gen();
    XRA1403_set_gpio_level(LD_PIN, LOW);
    XRA1403_set_gpio_level(CE_PIN, HIGH); // Habilitar el Charge Pump
    XRA1403_set_gpio_level(RF_EN_PIN, HIGH);
    en_output(RF_B,HIGH);
    en_output(RF_A,HIGH);
    VNA_path(S11_PATH);

    //vTaskDelay(1000/portTICK_PERIOD_MS);
    gpio_reset_pin(LED_VERDE);
    gpio_set_direction(LED_VERDE,GPIO_MODE_OUTPUT);
    gpio_set_level(LED_VERDE,1);

    //configure_MAX2870_20MHz();
    uart_flush(UART_NUM);

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
    
        vTaskDelay(pdMS_TO_TICKS(10));
    }

    //spi_deinit();

}
