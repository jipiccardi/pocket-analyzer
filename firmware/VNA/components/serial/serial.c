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

    ESP_LOGI(TAG_UART, "UART inicializada correctamente");

}
