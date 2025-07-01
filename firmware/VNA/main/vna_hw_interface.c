#include <stdio.h>
#include <unistd.h>
#include <stdint.h>

#include "gpio.h"
#include "adc.h"
#include "serial.h"
 


bool cali_ch0 = 0;
bool cali_ch1 = 0;


void set_VNA_path(uint8_t path){
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

void VNA_get_measure(uint16_t* data){
    uint32_t mag_value = 0, pha_value = 0;

    //Muestreo durante 10 mS que es el ciclo de ruido que mido en el osciloscopio
    for (int i = 0; i < 16; i++){
        mag_value += adc_read_channel_cali(ADC_CHANNEL_0,cali_ch0);
        pha_value += adc_read_channel_cali(ADC_CHANNEL_1,cali_ch1);
    }
    mag_value >>=  4;
    pha_value >>=  4;

    *(data) = mag_value;
    *(data+1) = pha_value;
}

void VNA_send_data(uint8_t mode, uint16_t* data){
    char data_str[60];
    char data_header[4] = {'\x02','V','A','L'};
    char data_footer = '\x03';
    uart_flush(UART_NUM);     

    /*UART CHART SEND MODE*/
    if (UART_MODE){
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
    }}
    /*UART BYTE SEND MODE*/
    else {
        switch (mode){
            case TWOPORT:
                sprintf(data_str, 
                    "\x02VAL%05d%04d%04d%04d%04d%04d%04d%04d%04d\x03",
                    data[8], data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7]);
                uart_write_bytes(UART_NUM, data_str, strlen(data_str));
                break;
            case ONEPORT:
                uart_write_bytes(UART_NUM,data_header, 4);
                uart_write_bytes(UART_NUM,&data[2],3);
                uart_write_bytes(UART_NUM,data,4);
                uart_write_bytes(UART_NUM,&data_footer,1);
                break;
            case END:
                uart_write_bytes(UART_NUM, "END", 3);
                break;
    }}
}

uint16_t get_sweep_step_lin(uint16_t f_low, uint16_t f_high, uint16_t npoints){
    uint16_t f_range = 0, f_step = 0;

    f_range = f_high - f_low;
    f_step = f_range / (npoints - 1);

    return f_step;
}