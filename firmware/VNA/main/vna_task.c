#include <stdio.h>
#include <unistd.h>
#include "stdint.h"

#include "gpio.h"
#include "serial.h"
#include "vna_sys_res.h"
#include "max2870.h"
#include "vna_hw_interface.h"

#define TRUE 1
#define FALSE 0

#define BLINK_T     1000

#define RXDATABUFF  10

#define N_COMMANDS  5
#define GPIO_MODE   0
#define FRQ_MODE    1
#define MEAS_MODE_1 2
#define MEAS_MODE_2 3
#define MEAS_MODE_3 4
#define NO_MODE     -1

#define P_ONE       1
#define P_TWO       2



static uint8_t vna_conn = 1, vna_meas = 0;
static uint8_t data_uart[RXDATABUFF];

/*Measurement data*/
static uint8_t meas_port;
static uint8_t meas_flag = FALSE;
static uint16_t f_low, f_high;

typedef struct {
    char * cmd;
    int mode;
} Rx_cmd;

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

void SM_serial_rx_task (void *pvParameter){
    static uint8_t STATE_UART = WAIT_UART; 
    uint16_t rx_len;
    size_t length = 0;
    uint8_t buff_uart[BUFF_SIZE];
    while (1){
        switch (STATE_UART){
            case WAIT_UART:
                uart_get_buffered_data_len(UART_NUM, (size_t*)&length);
                if (length >= 11)  
                    rx_len = uart_read_bytes(UART_NUM, buff_uart, 11, 20 / portTICK_PERIOD_MS);
                    if (rx_len > 0){
                        buff_uart[rx_len] = '\0'; //Pongo final de caracter para tratar como un string
                        STATE_UART = STX_CHECK;
                    }
                break;
            case STX_CHECK:
                if (buff_uart[0] == '\x02') //El primer caracter STX
                    STATE_UART = ETX_CHECK;
                else STATE_UART = WAIT_UART;
                break;
            case ETX_CHECK:
                if (buff_uart[10] == '\x03') //El ultimo caracter ETX
                    STATE_UART = DATA_CHECK;
                else
                    STATE_UART = WAIT_UART;
                break;
            case DATA_CHECK:
                xSemaphoreTake(xDataBufferRXMutex, portMAX_DELAY);
                for(int i=0;i<9;i++)
                    data_uart[i] = (char) buff_uart[i+1];
                data_uart[9] = '\0';
                xSemaphoreGive(xDataBufferRXMutex);
                STATE_UART = WAIT_UART;
                vTaskResume(xModeSelTaskHandle);
                vTaskSuspend(NULL);
                break;
            default:
                STATE_UART = WAIT_UART;
                break;
        }
    vTaskDelay(100/portTICK_PERIOD_MS); 
    }   
}      

void mode_sel_task (void *pvParameter){
    uint16_t f_point;
    uint8_t gpio_pin, gpio_lvl;
    int8_t mode;
    uint8_t rx_data[RXDATABUFF];
    Rx_cmd command [] = {
        {"GIO" , GPIO_MODE},
        {"FRQ" , FRQ_MODE},
        {"MS1" , MEAS_MODE_1},
        {"MS2" , MEAS_MODE_2},
        {"MS3" , MEAS_MODE_3}};

    while (1){   
        xSemaphoreTake(xDataBufferRXMutex,portMAX_DELAY) ;
        for (int i=0; i<RXDATABUFF; i++)
            rx_data[i] = data_uart[i];
        xSemaphoreGive(xDataBufferRXMutex);

        /*Mode selection*/
        mode = NO_MODE;
        for (int i=0; i<N_COMMANDS; i++){
            if (strncmp(rx_data, command[i].cmd, 3)){
                mode = command[i].mode;
                break;
            }
        }

        switch (mode){
        case GPIO_MODE:
            gpio_pin =(rx_data[7] - '0')*10 + (rx_data[8] - '0');
            gpio_lvl = rx_data[6] - '0';

            if (gpio_pin < 90)
                XRA1403_set_gpio_level(gpio_pin,gpio_lvl);
            else 
                //special_debug_fuction(gpio_pin); /*Llama a la funcion especiales de debug*/
            break;

        case FRQ_MODE:
            f_point = (rx_data[4] - '0')*10000
                +(rx_data[5] - '0')*1000
                +(rx_data[6] - '0')*100
                +(rx_data[7] - '0')*10
                +(rx_data[8] - '0');
            set_FRQ_ADF4351((uint32_t)f_point);
            break;
        
        case MEAS_MODE_1:
            xSemaphoreTake(xMeasParamMutex,portMAX_DELAY) ;
            meas_port = P_ONE;
            f_low = F_MIN_LOW;
            f_high = F_MAX_HIGH;
            meas_flag = TRUE;
            xSemaphoreGive(xMeasParamMutex);
            vTaskResume (xMeas1PTaskHandle);
            //start_1p_meas(f_low, f_high, ONE);
            break;

        case MEAS_MODE_2:
            xSemaphoreTake(xMeasParamMutex,portMAX_DELAY) ;
            meas_port = P_TWO;
            f_low = F_MIN_LOW;
            f_high = F_MAX_HIGH;
            meas_flag = TRUE;
            xSemaphoreGive(xMeasParamMutex) ;
            vTaskResume (xMeas1PTaskHandle);
            //start_1p_meas(f_low, f_high, ONE);
            break;

        case MEAS_MODE_3:
            xSemaphoreTake(xMeasParamMutex,portMAX_DELAY) ;
            f_low = F_MIN_LOW;
            f_high = F_MAX_HIGH;
            meas_flag = TRUE;
            xSemaphoreGive(xMeasParamMutex) ;
            vTaskResume(xMeas2PTaskHandle);
            //start_1p_meas(f_low, f_high, ONE);
            break;

        default:
            break;
        }
    vTaskResume(xSerialRxTaskHandle);
    vTaskSuspend(NULL);
    }
}

void meas_1p_task (void *pvParameter){
    uint16_t f_low_local, f_high_local, f_out = 0, npoints = 1000;
    uint16_t data[3];

    xSemaphoreTake(xMeasParamMutex,portMAX_DELAY) ;
    f_low_local = f_low;
    f_high_local = f_high;
    if (meas_port == P_ONE)
        set_VNA_path(S11_PATH);
    else set_VNA_path(S22_PATH);
    xSemaphoreGive(xMeasParamMutex) ;

    f_out = f_low_local;
    set_FRQ_ADF4351(f_out);
    vTaskDelay(1/portTICK_PERIOD_MS); 
    while (f_out < f_high_local){  
        VNA_get_measure(&data[0]);
        data[2] = get_FRQ_ADF4351();
        //if (STEPMODE == 1)
        f_out += get_sweep_step_lin(f_low_local,f_high_local,npoints); 
        set_FRQ_ADF4351(f_out);
        VNA_send_data(P_ONE, data);
        vTaskDelay(1/portTICK_PERIOD_MS); 
    }
    VNA_send_data (END, NULL);
}

void meas_2p_task (void *pvParameter){
    uint16_t f_low_local, f_high_local, f_out = 0, npoints = 1000;
    uint16_t data[9];

    xSemaphoreTake(xMeasParamMutex,portMAX_DELAY) ;
    f_low_local = f_low;
    f_high_local = f_high;
    xSemaphoreGive(xMeasParamMutex);

    f_out = f_low_local;
    set_FRQ_ADF4351(f_out);
    vTaskDelay(1/portTICK_PERIOD_MS); 
    while (f_out < f_high_local){

        set_VNA_path(S11_PATH);
        VNA_get_measure(&data[0]);
        set_VNA_path(S21_PATH);
        VNA_get_measure(&data[2]);
        set_VNA_path(S22_PATH);
        VNA_get_measure(&data[4]);
        set_VNA_path(S12_PATH);
        VNA_get_measure(&data[6]);  
        data[8] = get_FRQ_ADF4351();

        //if (STEPMODE == 1)
        f_out += get_sweep_step_lin(f_low_local,f_high_local,npoints); 
        set_FRQ_ADF4351(f_out);
        VNA_send_data(P_ONE, data);
        vTaskDelay(1/portTICK_PERIOD_MS); 
    }
    VNA_send_data (END, NULL);
}