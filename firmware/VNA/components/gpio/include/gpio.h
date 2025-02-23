#ifndef GPIO_H
#define GPIO_H
#include "../../spi/include/spi.h"

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

#define HIGH 1
#define LOW 0

#define INPUT 1
#define OUTPUT 0

void XRA1403_init(void);
void XRA1403_set_gpio_level(uint8_t,uint8_t);
void XRA1403_set_gpio_mode(uint8_t,uint8_t);

#endif
