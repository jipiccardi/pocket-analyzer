#ifndef PR_MAX2870_H
#define PR_MAX2870_H

#include <stdio.h>
#include "max2870.h"
#include "../../gpio/include/gpio.h"

#define CRYSTAL_FRQ 192 //Cristal Freq in 10^5 Hz
#define INT_MODE    1

#define RF_A        1
#define RF_B        2
#define RF_HIGH     1
#define RF_LOW      0

#define LD_PIN      0
#define CE_PIN      1
#define RF_EN_PIN   2

void set_FRQ(uint32_t freq);

uint16_t get_FRQ(void);

void set_PWR(uint8_t pwr, uint8_t RF_out);

void set_Rdiv(uint16_t rdivider);

uint16_t get_Rdiv (void);

void en_output (uint8_t RF_out, uint8_t status);

void set_PLLmode(uint8_t mode);

void init_FRQ_gen(void);

void configure_MAX2870_20MHz(void);

#endif