#include "spi.h"

spi_device_handle_t XRA1403_handle;
spi_device_handle_t MAX2870_handle;

void spi_init(void)
{
    esp_err_t ret;
    //Habilitamos el BUS spi, indicamos los pines correspondientes al SPI
    spi_bus_config_t buscfg = {
        .mosi_io_num = GPIO_MOSI,
        .miso_io_num = GPIO_MISO,
        .sclk_io_num = GPIO_SCLK,
        .quadwp_io_num = -1,
        .quadhd_io_num = -1
    };
    
    //Agregamos el dispositivo al bus SPI, en este caso la Expansión GPIO
    spi_device_interface_config_t devcfg_XRA1403 = {
        .command_bits = 1,
        .address_bits = 6,
        .dummy_bits = 1,
        .clock_speed_hz = 40000000,
        .duty_cycle_pos = 128,      //50% duty cycle
        .mode = 0,
        .spics_io_num = GPIO_CS3,
        .cs_ena_posttrans = 3,      //Keep the CS low 3 cycles after transaction, to stop slave from missing the last bit when CS has less propagation delay than CLK
        .queue_size = 3,
    };

     //Agregamos el dispositivo al bus SPI, en este caso el Generador
    spi_device_interface_config_t devcfg_MAX2870 = {
        .command_bits = 0,
        .address_bits = 0,
        .dummy_bits = 0,
        .clock_speed_hz = 60000000,
        .duty_cycle_pos = 128,      //50% duty cycle
        .mode = 0,
        .spics_io_num = GPIO_CS2,
        .cs_ena_pretrans = 1,      //Keep the CS low 3 cycles after transaction, to stop slave from missing the last bit when CS has less propagation delay than CLK
        .cs_ena_posttrans = 1,      //Keep the CS low 3 cycles after transaction, to stop slave from missing the last bit when CS has less propagation delay than CLK
        .queue_size = 3,
        .flags = SPI_DEVICE_HALFDUPLEX,
    };

    //GPIO config for the RESET. Pin que indica el RESET
    gpio_config_t io_conf = {
        .mode = GPIO_MODE_OUTPUT,
        .pin_bit_mask = BIT64(GPIO_RESET),
    };

    gpio_config(&io_conf);

    //Funciones que inicializan el bus y agregan el dispositivo
    ret = spi_bus_initialize(SENDER_HOST, &buscfg, SPI_DMA_CH_AUTO);
    assert(ret == ESP_OK);
    ret = spi_bus_add_device(SENDER_HOST, &devcfg_XRA1403, &XRA1403_handle);
    assert(ret == ESP_OK);
    ret = spi_bus_add_device(SENDER_HOST, &devcfg_MAX2870, &MAX2870_handle);
    assert(ret == ESP_OK);
    gpio_set_level(GPIO_RESET,1); //Para evitar el reset
}

void spi_deinit(void){

    esp_err_t ret;
    
    ret = spi_bus_remove_device(XRA1403_handle);
    assert(ret == ESP_OK);

    ret = spi_bus_remove_device(MAX2870_handle);
    assert(ret == ESP_OK);

    ret = spi_bus_free(SPI2_HOST);
    assert(ret == ESP_OK);
}
//Escribe un registro de la expansion GPIO
void XRA1403_write_register(uint8_t reg, uint8_t data){

    spi_transaction_t t;
    uint8_t my_buff[1] = {0};

    memset(&t, 0, sizeof(t));

    t.cmd = WRITE_CMD;
    t.addr= reg;
    t.length = 8;
    my_buff[0] = data;
    t.tx_buffer=my_buff;
    spi_device_transmit(XRA1403_handle, &t);
    //printf("\n Write Register Ok");
}

//Lee un registro de la expansion GPIO
uint8_t XRA1403_read_register(uint8_t reg){
    spi_transaction_t t;
    uint8_t out_data=2;

    memset(&t, 0, sizeof(t));

    t.cmd = READ_CMD;
    t.addr= reg;
    t.length = 8; //si no anda probar length 16
    t.rxlength = 8;
    t.flags = SPI_TRANS_USE_RXDATA;
    spi_device_transmit(XRA1403_handle, &t);
    out_data=t.rx_data[0];
    //printf("\n output:%d",(int)out_data);

    return out_data;
}

