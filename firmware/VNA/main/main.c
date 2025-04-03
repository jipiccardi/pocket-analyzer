#include <stdio.h>
#include <unistd.h>
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


static const char *TAG_MAIN = "MAIN";
uint8_t flag_main = 0;
uint8_t data_uart[10];
bool cali_ch0;
bool cali_ch1;


/* INICIO (Pasar esta seccion a otro archivo)*/
void VNA_path(uint8_t path);

#define SWT_A_1     3
#define SWT_A_2     4
#define SWT_B_1     5
#define SWT_B_2     6
#define SWT_C_1     7
#define SWT_C_2     8

#define S11_PATH    0
#define S21_PATH    1
#define S22_PATH    2
#define S12_PATH    3

#define STEPMODE    1       //1 = LINEAR       2 = OCTAVE

#define END         0
#define ONEPORT     1
#define TWOPORT     2

#define ONE         1
#define TWO         2



static void set_VNA_path(uint8_t path){
    switch (path){
        case S11_PATH:
            XRA1403_set_gpio_level(SWT_A_2, LOW);
            XRA1403_set_gpio_level(SWT_A_1, HIGH);
            XRA1403_set_gpio_level(SWT_B_2, LOW);
            XRA1403_set_gpio_level(SWT_B_1, HIGH);
            break;

        case S21_PATH:
            XRA1403_set_gpio_level(SWT_A_2, LOW);
            XRA1403_set_gpio_level(SWT_A_1, HIGH);
            XRA1403_set_gpio_level(SWT_B_1, LOW);
            XRA1403_set_gpio_level(SWT_B_2, HIGH);
            break;
        
        case S22_PATH:
            XRA1403_set_gpio_level(SWT_A_1, LOW);
            XRA1403_set_gpio_level(SWT_A_2, HIGH);
            XRA1403_set_gpio_level(SWT_B_1, LOW);
            XRA1403_set_gpio_level(SWT_B_2, HIGH);
            break;

        case S12_PATH:
            XRA1403_set_gpio_level(SWT_A_1, LOW);  
            XRA1403_set_gpio_level(SWT_A_2, HIGH);
            XRA1403_set_gpio_level(SWT_B_2, LOW);
            XRA1403_set_gpio_level(SWT_B_1, HIGH);
            break;
    }
}

uint16_t get_sweep_step_lin(uint16_t f_low, uint16_t f_high, uint16_t npoints){
    uint16_t f_range = 0, f_step = 0;

    f_range = f_high - f_low;
    f_step = f_range / (npoints - 1);

    return f_step;
}
uint16_t get_sweep_step_octave(uint16_t f_out){
    uint16_t step = 0;

            if(f_out < 469)            step = 6;
            else if (f_out < 938)      step = 12;
            else if (f_out < 1875)     step = 24;  
            else if (f_out < 3750)     step = 48;
            else if (f_out < 7500)     step = 96; 
            else if (f_out < 15000)    step = 192;
            else if (f_out < 30000)    step = 384;
            else                       step = 768;
    return step;
}

void get_measure(uint16_t* data){
    uint32_t mag_value = 0, pha_value = 0;

    //Muestreo durante 10 mS que es el ciclo de ruido que mido en el osciloscopio
    for (int i = 0; i < 64; i++){
        mag_value += adc_read_channel_cali(ADC_CHANNEL_0,cali_ch0);
        usleep(10);
        pha_value += adc_read_channel_cali(ADC_CHANNEL_1,cali_ch1);
        usleep(10);
    }
    mag_value >>=  6;
    pha_value >>=  6;

    *(data) = mag_value;
    *(data+1) = pha_value;
}

void send_data (uint8_t mode, uint16_t* data){
    char data_str[60];

    uart_flush(UART_NUM);     
    switch (mode){
        case TWOPORT:
            sprintf(data_str, 
                "\x02VAL%05d%04d%04d%04d%04d%04d%04d%04d%04d\x03",
                 data[8], data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7]);
            uart_write_bytes(UART_NUM, data_str, strlen(data_str));
            break;
        case ONEPORT:
            sprintf(data_str, 
                "\x02VAL%05d%04d%04d\x03",
                data[2], data[0], data[1]);
            uart_write_bytes(UART_NUM, data_str, strlen(data_str));
            break;
        case END:
            uart_write_bytes(UART_NUM, "END", 3);
            break;
    }
}

void start_2p_meas(uint16_t f_low, uint16_t f_high){
    uint16_t f_out = 0, npoints = 500;
    uint16_t data[9];

    f_out = f_low;
    while (f_out < f_high){
        //XRA1403_set_gpio_level(CE_PIN, LOW); 
        //XRA1403_set_gpio_level(CE_PIN, HIGH);
        
        configure_MAX2870_20MHz();
        vTaskDelay(10/portTICK_PERIOD_MS);
        set_FRQ(f_out);
        set_VNA_path(S11_PATH);
        usleep(2000);
        get_measure(&data[0]);
        set_VNA_path(S21_PATH);
        usleep(2000);
        get_measure(&data[2]);
        set_VNA_path(S22_PATH);
        usleep(2000);
        get_measure(&data[4]);
        set_VNA_path(S12_PATH);
        usleep(2000);
        get_measure(&data[6]);
        data[8] = get_FRQ();
        send_data(TWOPORT, data);
        if (STEPMODE == 1)
            f_out += get_sweep_step_lin(f_low,f_high,npoints); 
        else if (STEPMODE == 2)
            f_out += get_sweep_step_octave(f_out);
    }
    send_data (END, NULL); 
}

void start_1p_meas(uint16_t f_low, uint16_t f_high, uint8_t port){
    uint16_t f_out = 0, npoints = 500;
    uint16_t data[3];

    f_out = f_low;
    while (f_out < f_high){   
        XRA1403_set_gpio_level(CE_PIN, LOW); 
        XRA1403_set_gpio_level(CE_PIN, HIGH);
        vTaskDelay(10/portTICK_PERIOD_MS);
        configure_MAX2870_20MHz();
        set_FRQ(f_out);
        if (port == ONE) set_VNA_path(S11_PATH);
        else set_VNA_path(S22_PATH);
        get_measure(&data[0]);
        data[2] = get_FRQ();
        send_data(ONEPORT, data);
        if (STEPMODE == 1)
            f_out += get_sweep_step_lin(f_low,f_high,npoints); 
        else if (STEPMODE == 2)
            f_out += get_sweep_step_octave(f_out); 
    }
    send_data (END, NULL);
}

void start_1p_meas_1point(uint16_t f_low, uint16_t f_high, uint8_t port){
    uint16_t f_out = 0;
    uint16_t data[3];

    f_out = get_FRQ();
    for (int i=0; i<1000; i++){  
        configure_MAX2870_20MHz();
        XRA1403_set_gpio_level(CE_PIN, HIGH); 
        set_FRQ(f_out);
        usleep(500000);
        if (port == ONE) set_VNA_path(S11_PATH);
        else set_VNA_path(S22_PATH);
        get_measure(&data[0]);
        data[2] = get_FRQ();
        send_data(ONEPORT, data);
        //f_out += get_sweep_step_octave(f_out); 
    }
    send_data (END, NULL);
}


/*FIN*/



static void state_machine_process_data(void){
    uint16_t f_low, f_high;
    uint8_t gpio_pin;
    uint8_t state;
    int mag_value_S11=0, pha_value_S11, frq_value;
    char mag_value_S11_str[8], pha_value_S11_str[8], frq_value_str[6];
    char test_str[27];
    char end_str[] = "Termine\n";
    uint32_t frq = 235;


    if (flag_main == 1){
        if (data_uart[0] == 'G' && data_uart[1] == 'I' && data_uart[2] == 'O'){
            gpio_pin = data_uart[8] - 48;
            state = data_uart[7] - 48;
            if (gpio_pin != 9)
                XRA1403_set_gpio_level(gpio_pin,state);
                
            else {
                XRA1403_set_gpio_level(CE_PIN, LOW); // Habilitar el Charge Pump
                XRA1403_set_gpio_level(RF_EN_PIN, LOW);
                MAX2870_init();
                configure_MAX2870_20MHz();   
                XRA1403_set_gpio_level(CE_PIN, HIGH); // Habilitar el Charge Pump
                XRA1403_set_gpio_level(RF_EN_PIN, HIGH);
            }
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
        else if (data_uart[0] == 'S' && data_uart[1] == 'M'){
            uart_flush(UART_NUM);
            f_low = 235;
            f_high = 25000;
            if (data_uart[2] == '1')
                start_1p_meas(f_low, f_high, ONE);
            if (data_uart[2] == '2')
                start_1p_meas(f_low, f_high, TWO);
            if (data_uart[2] == '3')
                start_2p_meas(f_low, f_high);
            flag_main = 0; 
        }
/*        else if (data_uart[0] == 'S' && data_uart[1] == 'M' && data_uart[2] == '1'){
            int n = 1;
            // Write data to UART.
            uart_flush(UART_NUM);
            set_VNA_path(S11_PATH);
            for(int k=0;k<100;k++){
                configure_MAX2870_FRAC();   
                
                set_FRQ(frq);
                usleep(3000000);
                frq += 300;
                
                frq_value = get_FRQ();
                mag_value_S11 = 0;
                pha_value_S11 = 0;
                for (int i=0; i<128; i++){
                    mag_value_S11 += adc_read_channel_cali(ADC_CHANNEL_0,cali_ch0);
                    usleep(21);
                    pha_value_S11 += adc_read_channel_cali(ADC_CHANNEL_1,cali_ch1);
                    usleep(21);
                }
                mag_value_S11 >>=  8;
                pha_value_S11 >>=  8;
                strcpy(test_str, "\x02VAL");
                sprintf(mag_value_S11_str, "%04d", (uint16_t) mag_value_S11);
                sprintf(pha_value_S11_str, "%04d", (uint16_t) pha_value_S11);
                sprintf(frq_value_str, "%05d", frq_value);

                strcat(test_str,frq_value_str);
                strcat(test_str,mag_value_S11_str);
                strcat(test_str,pha_value_S11_str);
                strcat(test_str,"ccccdddd");
                strcat(test_str,"\x03");
            
                uart_write_bytes(UART_NUM, test_str, strlen(test_str));
        }
            uart_write_bytes(UART_NUM, end_str, strlen(end_str));
            //uart_flush(UART_NUM);
            //uart_write_bytes(UART_NUM, test_str, strlen(test_str));
            //ESP_ERROR_CHECK(uart_wait_tx_done(UART_NUM, 100)); // wait timeout is 100 RTOS ticks (TickType_t)
            //n = atoi(data_uart[8]);
            
            //ESP_LOGI(TAG_MAIN, "Recibimos el Match: %d",n);
            flag_main = 0;
        }
*/
        flag_main = 0;
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
    //init_FRQ_gen();
    //MAX2870_init();
    
    vTaskDelay(20/portTICK_PERIOD_MS);
    //en_output(RF_B,HIGH);
    vTaskDelay(20/portTICK_PERIOD_MS);
    //en_output(RF_A,HIGH);
    set_VNA_path(S11_PATH);
    //configure_MAX2870_20MHz();
    

    //vTaskDelay(1000/portTICK_PERIOD_MS);
    gpio_reset_pin(LED_VERDE);
    gpio_set_direction(LED_VERDE,GPIO_MODE_OUTPUT);
    gpio_set_level(LED_VERDE,1);
    XRA1403_set_gpio_level(SWT_C_2, LOW);
    XRA1403_set_gpio_level(SWT_C_1, HIGH);

    //configure_MAX2870_20MHz();
    uart_flush(UART_NUM);

    //Inicializacion del ADF 
    //Los pines no cambian al igual que el CHIP SELECT conectarlos de la misma forma
    XRA1403_set_gpio_level(LD_PIN, LOW);
    XRA1403_set_gpio_level(CE_PIN, HIGH); // Habilitar el Charge Pump
    XRA1403_set_gpio_level(RF_EN_PIN, HIGH);

    MAX2870_write_register(0x400005);
    vTaskDelay(pdMS_TO_TICKS(100));
    MAX2870_write_register(0x8014DC);
    vTaskDelay(pdMS_TO_TICKS(100));
    MAX2870_write_register(0x800003);
    vTaskDelay(pdMS_TO_TICKS(100));
    MAX2870_write_register(0x400CE42);
    vTaskDelay(pdMS_TO_TICKS(100));
    MAX2870_write_register(0x8011);
    vTaskDelay(pdMS_TO_TICKS(100));
    MAX2870_write_register(0xB8000);

    //N = 146 R = 2 FRAC = 0 MOD = 2 Activo las dos salidas Fvco = 2560MHz Fpfd = 17.5MHz Fo = 39.92MHz
    MAX2870_write_register(0x8014DC | (64<<20) | (175<<12) | (1<<5) | (1<<8));
    MAX2870_write_register(0x400CE42 | (2<<14));
    MAX2870_write_register(0xB8000 | (146<<15))






    while(1){
        //adc_ch0 = adc_read_channel_cali(ADC_CHANNEL_0,cali_ch0);
        //

        // Read data from the UART
        //int len = uart_read_bytes(UART_NUM, data, BUFF_SIZE, 20 / portTICK_PERIOD_MS);
        
        //if (len > 0){
            //data[len] = '\0';
            //state_machine_uart();
            //ESP_LOGI(TAG_MAIN, "Recv str: %s",data_uart);
           // state_machine_process_data();
            //ESP_LOGI(TAG_MAIN, "Len str: %d", len);

        //}
        
    
        //ESP_LOGI(TAG_MAIN, "ERROR Recv str");
    
        vTaskDelay(pdMS_TO_TICKS(100));
    }

    //spi_deinit();

}
