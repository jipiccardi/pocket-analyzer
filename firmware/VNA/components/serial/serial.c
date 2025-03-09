#include "serial.h"

void uart_init(void)
{
    uart_config_t uart_config = {
        .baud_rate = 9600,
        .data_bits = UART_DATA_8_BITS,
        .parity = UART_PARITY_DISABLE,
        .flow_ctrl = UART_HW_FLOWCTRL_DISABLE,
        .source_clk = UART_SCLK_DEFAULT,
        .stop_bits = UART_STOP_BITS_1
    };
    
    uart_param_config(UART_NUM, &uart_config);
    uart_set_pin(UART_NUM,UART_TX_PIN,UART_RX_PIN,UART_PIN_NO_CHANGE,UART_PIN_NO_CHANGE);
    uart_driver_install(UART_NUM,BUFF_SIZE,BUFF_SIZE*2,0,NULL,0);

    //inicializo el buffer de data_uart con ceros
    data_uart[0] = '\0';
    
    ESP_LOGI(TAG_UART, "UART inicializada correctamente");

}

void state_machine_uart(void){
    static uint8_t STATE_UART = WAIT_UART; 
    size_t length = 0;
        if (flag_main == 0)
        {
            switch (STATE_UART)
            {
            case WAIT_UART:
                //ESP_LOGI(TAG_UART, "Estoy en el primer estado");
                uart_get_buffered_data_len(UART_NUM, (size_t*)&length);

                if (length < 11)
                    break;
                else{
                    int len = uart_read_bytes(UART_NUM, buff_uart, 11, 20 / portTICK_PERIOD_MS);
                    if (len > 0){
                        buff_uart[len] = '\0'; //Pongo final de caracter para tratarloc como un string
                        //ESP_LOGI(TAG_UART, "Buff RX: %s", (char *) buff_uart);
                        STATE_UART = STX_CHECK;
                        break;
                    }
                    else
                        break;
            }
            case STX_CHECK:
                /* code */
                //ESP_LOGI(TAG_UART, "Estoy en el segundo estado");
                if (buff_uart[0] == '\x02') //El primer caracter STX
                    STATE_UART = ETX_CHECK;
                else 
                    STATE_UART = WAIT_UART;
                break;
            case ETX_CHECK:
                //ESP_LOGI(TAG_UART, "Estoy en el tercer estado");
                if (buff_uart[10] == '\x03') //El ultimo caracter ETX
                    STATE_UART = DATA_CHECK;
                else
                    STATE_UART = WAIT_UART;
                break;
            case DATA_CHECK:
                //ESP_LOGI(TAG_UART, "Estoy en el cuarto estado");
                for(int i=0;i<9;i++)
                    data_uart[i] = (char) buff_uart[i+1];
                data_uart[9] = '\0';
                //(TAG_UART, "EL dato es %s",data_uart);
                STATE_UART = WAIT_UART;
                flag_main = 1;
                break;
            default:
                STATE_UART = WAIT_UART;
                break;
            }
        }
        
    
    
}


