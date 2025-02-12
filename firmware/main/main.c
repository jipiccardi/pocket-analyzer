/* SPI Slave example, sender (uses SPI master driver)

   This example code is in the Public Domain (or CC0 licensed, at your option.)

   Unless required by applicable law or agreed to in writing, this
   software is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
   CONDITIONS OF ANY KIND, either express or implied.
*/
#include <stdio.h>
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/semphr.h"
#include "freertos/queue.h"
#include "driver/spi_master.h"
#include "driver/gpio.h"
#include "esp_timer.h"
#include "esp_mac.h"

/*
SPI sender (master) example.

This example is supposed to work together with the SPI receiver. It uses the standard SPI pins (MISO, MOSI, SCLK, CS) to
transmit data over in a full-duplex fashion, that is, while the master puts data on the MOSI pin, the slave puts its own
data on the MISO pin.

This example uses one extra pin: GPIO_HANDSHAKE is used as a handshake pin. The slave makes this pin high as soon as it is
ready to receive/send data. This code connects this line to a GPIO interrupt which gives the rdySem semaphore. The main
task waits for this semaphore to be given before queueing a transmission.
*/

//////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////// Please update the following configuration according to your HardWare spec /////////////////
//////////////////////////////////////////////////////////////////////////////////////////////////////////
#define GPIO_RESET          9
#define GPIO_IRQ            3
#define GPIO_MOSI           7
#define GPIO_MISO           2
#define GPIO_SCLK           6
#define GPIO_CS3            19
#define GPIO_CS2            18

#define HIGH 1
#define LOW 0

// Commands par la expansion GPIO
#define GSR1_CMD    0x00
#define GSR2_CMD    0x01
#define OCR1_CMD    0x02
#define OCR2_CMD    0x03
#define PIR1_CMD    0x04
#define PIR2_CMD    0x05
#define GCR1_CMD    0x06
#define GCR2_CMD    0x07
#define PUR1_CMD    0x08
#define PUR2_CMD    0x09
#define IER1_CMD    0x0A 
#define IER2_CMD    0x0B
#define TSCR1_CMD    0x0C
#define TSCR2_CMD    0x0D
#define ISR1_CMD    0x0E
#define ISR2_CMD    0x0F
#define REIR1_CMD    0x10
#define REIR2_CMD    0x11
#define FEIR1_CMD    0x12
#define FEIR2_CMD    0x13
#define IFR1_CMD    0x14
#define IFR2_CMD    0x15

#define WRITE_CMD   0x0 
#define READ_CMD    0x1 

// Commands para el generador MAX2870

#define REG0_CMD 0x00
#define REG1_CMD 0x01
#define REG2_CMD 0x02
#define REG3_CMD 0x03
#define REG4_CMD 0x04
#define REG5_CMD 0x05
#define REG6_CMD 0x06

#define GPIO_MASK 0xFFFE

#define portTICK_PERIOD_MS              ((TickType_t) (1000 / configTICK_RATE_HZ))
#define CONFIG_BLINK_PERIOD 1000

#define REF 0
#define LD  1
#define CE  2

#ifdef CONFIG_IDF_TARGET_ESP32
#define SENDER_HOST HSPI_HOST
#else
#define SENDER_HOST SPI2_HOST
#endif

//The semaphore indicating the slave is ready to receive stuff.
//static QueueHandle_t rdySem;

/*
This ISR is called when the handshake line goes high.
*/

/*
static void IRAM_ATTR gpio_handshake_isr_handler(void* arg)
{
    //Sometimes due to interference or ringing or something, we get two irqs after eachother. This is solved by
    //looking at the time between interrupts and refusing any interrupt too close to another one.
    static uint32_t lasthandshaketime_us;
    uint32_t currtime_us = esp_timer_get_time();
    uint32_t diff = currtime_us - lasthandshaketime_us;
    if (diff < 1000) {
        return; //ignore everything <1ms after an earlier irq
    }
    lasthandshaketime_us = currtime_us;

    //Give the semaphore.
    BaseType_t mustYield = false;
    xSemaphoreGiveFromISR(rdySem, &mustYield);
    if (mustYield) {
        portYIELD_FROM_ISR();
    }
}
*/
//Hay que usar un Handle por cada dispositivo
spi_device_handle_t XRA1403_handle;
spi_device_handle_t MAX2870_handle;

static void spi_init(){

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
        .clock_speed_hz = 20000000,
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
        .clock_speed_hz = 20000000,
        .duty_cycle_pos = 128,      //50% duty cycle
        .mode = 0,
        .spics_io_num = GPIO_CS2,
        .cs_ena_pretrans = 3,      //Keep the CS low 3 cycles after transaction, to stop slave from missing the last bit when CS has less propagation delay than CLK
        .cs_ena_posttrans = 3,      //Keep the CS low 3 cycles after transaction, to stop slave from missing the last bit when CS has less propagation delay than CLK
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

//Escribe un registro de la expansion GPIO
static void XRA1403_write_register(uint8_t reg, uint8_t data){

    spi_transaction_t t;
    uint8_t my_buff[1] = {0};

    memset(&t, 0, sizeof(t));

    t.cmd = WRITE_CMD;
    t.addr= reg;
    t.length = 8;
    my_buff[0] = data;
    t.tx_buffer=my_buff;
    spi_device_transmit(XRA1403_handle, &t);
    printf("\n Write Register Ok");
}

//Lee un registro de la expansion GPIO
static uint8_t XRA1403_read_register(uint8_t reg){
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
    printf("\n output:%d",(int)out_data);

    return out_data;
}

//Pone el gpio indicado en HIGH o LOW
static void XRA1403_set_gpio(uint8_t pin,uint8_t value){
    uint8_t aux = 0;

    //Los primeros 8 pines van con OCR1
    if (pin<8){
        aux = XRA1403_read_register(GSR1_CMD);
        if (value == HIGH)
            aux = aux | (1<<pin);
        else
            aux = aux & (~(1<<pin));
        XRA1403_write_register(OCR1_CMD,aux);
    }

    //Los primeros 8 pines van con OCR2
    else if (8 <= pin && pin < 16){
        aux = XRA1403_read_register(GSR2_CMD);
        if (value == HIGH)
            aux = aux | (1<<pin);
        else
            aux = aux & (~(1<<pin));
        XRA1403_write_register(OCR2_CMD,aux);
    }
        
}

static void XRA1403_init(void){
    //Pongo todos como salidas, asi lo vamos a usar
    XRA1403_write_register(GCR1_CMD,0x00);
    XRA1403_write_register(GCR2_CMD,0x00);
    //Deshabilito las interrupciones
    XRA1403_write_register(IER1_CMD,0x00);
    XRA1403_write_register(IER2_CMD,0x00);
}

static void MAX2870_write_register(uint8_t reg, uint32_t data){
    spi_transaction_t t;
    uint32_t my_buff[1] = {0};

    memset(&t, 0, sizeof(t));

    t.cmd = 0;
    t.addr= 0;
    t.length = 32;
    my_buff[0] = data<<3|reg;
    t.tx_buffer=my_buff;
    spi_device_transmit(MAX2870_handle, &t);
    printf("\n Write Register Ok");
}

//Lee un registro del generador
static uint32_t MAX2870_read_register(uint8_t reg){
    spi_transaction_t t;
    uint32_t out_data=2;

    //MAX2870_write_register(REG2_CMD,); //MUX = 1100

    memset(&t, 0, sizeof(t));

    t.cmd = 0;
    t.addr= 0;
    t.length = 32;
    t.rxlength = 32;
    t.flags = SPI_TRANS_USE_RXDATA;
    spi_device_transmit(XRA1403_handle, &t);
    out_data=t.rx_data[0];
    printf("\n output:%d",(int)out_data);

    //MAX2870_write_register(REG2_CMD,); //MUX = 0000

    return out_data;
}

static void MAX2870_init(void){
    MAX2870_write_register(REG5_CMD,0x4000005); //Valor por defecto
    vTaskDelay(20/portTICK_PERIOD_MS);
    MAX2870_write_register(REG4_CMD,0x6180B21C); //Deshabilitamos ambas salidas
    vTaskDelay(20/portTICK_PERIOD_MS);
    MAX2870_write_register(REG3_CMD,0x0000000B); //Deshabilitamos ambas salidas  
    vTaskDelay(20/portTICK_PERIOD_MS);
    MAX2870_write_register(REG2_CMD,0x00004042); //Deshabilitamos ambas salidas 
    vTaskDelay(20/portTICK_PERIOD_MS);
    MAX2870_write_register(REG1_CMD,0x2000FFF9); //Deshabilitamos ambas salidas 
    vTaskDelay(20/portTICK_PERIOD_MS);
    MAX2870_write_register(REG0_CMD,0x007D0000); //Deshabilitamos ambas salidas 
    
    vTaskDelay(20/portTICK_PERIOD_MS);

    MAX2870_write_register(REG5_CMD,0x4000005); //Valor por defecto
    vTaskDelay(20/portTICK_PERIOD_MS);
    MAX2870_write_register(REG4_CMD,0x6180B21C); //Deshabilitamos ambas salidas
    vTaskDelay(20/portTICK_PERIOD_MS);
    MAX2870_write_register(REG3_CMD,0x0000000B); //Deshabilitamos ambas salidas  
    vTaskDelay(20/portTICK_PERIOD_MS);
    MAX2870_write_register(REG2_CMD,0x04004042); //Pongo el MUX como VDD 
    vTaskDelay(20/portTICK_PERIOD_MS);
    MAX2870_write_register(REG1_CMD,0x2000FFF9); //Deshabilitamos ambas salidas 
    vTaskDelay(20/portTICK_PERIOD_MS);
    MAX2870_write_register(REG0_CMD,0x007D0000); //Deshabilitamos ambas salidas 

    //Habilitiar la salida con reg4

}
//Main application
void app_main(void)
{
    esp_err_t ret;
    uint32_t data_reg_gen = 0;

    spi_init();

    //Create the semaphore.
    //rdySem = xSemaphoreCreateBinary();

    //Set up handshake line interrupt.
    //gpio_config(&io_conf);
    //gpio_install_isr_service(0);
    //gpio_set_intr_type(GPIO_HANDSHAKE, GPIO_INTR_POSEDGE);
    //gpio_isr_handler_add(GPIO_HANDSHAKE, gpio_handshake_isr_handler, NULL);

    //Assume the slave is ready for the first transmission: if the slave started up before us, we will not detect
    //positive edge on the handshake line.
    //xSemaphoreGive(rdySem);

    vTaskDelay(100/portTICK_PERIOD_MS);
    //XRA1403_write_register(GCR1_CMD,0x00);
    XRA1403_init();

    MAX2870_init(); //init basico del generador
    vTaskDelay(3000/portTICK_PERIOD_MS);

    MAX2870_write_register(REG2_CMD,0x08004042); //Pongo el MUX como GND 
    vTaskDelay(20/portTICK_PERIOD_MS);
    
    XRA1403_set_gpio(0,HIGH);
    XRA1403_set_gpio(1,HIGH);
    XRA1403_set_gpio(2,HIGH);
    XRA1403_set_gpio(13,HIGH);
    
    //Never reached.
    ret = spi_bus_remove_device(XRA1403_handle);
    assert(ret == ESP_OK);

    ret = spi_bus_remove_device(MAX2870_handle);
    assert(ret == ESP_OK);

    ret = spi_bus_free(SPI2_HOST);
    assert(ret == ESP_OK);

}
