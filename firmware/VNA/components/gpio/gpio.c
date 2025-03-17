#include "gpio.h"

void XRA1403_init(void){
    //Pongo todos como salidas, asi lo vamos a usar
    XRA1403_write_register(GCR1_CMD,0x00);
    XRA1403_write_register(GCR2_CMD,0x00);
    //Deshabilito las interrupciones
    XRA1403_write_register(IER1_CMD,0x00);
    XRA1403_write_register(IER2_CMD,0x00);
    //Los pongo todos en 0
    XRA1403_write_register(OCR1_CMD,0x00);
    XRA1403_write_register(OCR2_CMD,0x00);
}

//Pone el gpio indicado en HIGH o LOW
void XRA1403_set_gpio_level(uint8_t pin,uint8_t value){
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

//Pone el gpio indicado como INPUT o OUTPUT
//INPUT = 1 OUTPUT = 0
void XRA1403_set_gpio_mode(uint8_t pin,uint8_t mode){
    
    uint8_t aux = 0;
    //Los primeros 8 pines van con GCR1
    if (pin<8){
        aux = XRA1403_read_register(GCR1_CMD);
        if (mode == INPUT)
            aux = aux | (1<<pin);
        else
            aux = aux & (~(1<<pin));
        XRA1403_write_register(GCR1_CMD,aux);
    }

    //Los primeros 8 pines van con GCR2
    else if (8 <= pin && pin < 16){
        aux = XRA1403_read_register(GCR2_CMD);
        if (mode == INPUT)
            aux = aux | (1<<pin);
        else
            aux = aux & (~(1<<pin));
        XRA1403_write_register(GCR2_CMD,aux);
    }
}