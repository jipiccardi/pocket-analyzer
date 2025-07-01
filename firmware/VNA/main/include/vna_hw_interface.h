#ifndef VNA_HW_INTERFACE_H
#define VNA_HW_INTERFACE_H

#include <stdio.h>
#include <unistd.h>
#include <stdint.h>

#define S11_PATH    0
#define S21_PATH    1
#define S22_PATH    2
#define S12_PATH    3

#define END         0
#define ONEPORT     1
#define TWOPORT     2
#define UART_MODE   0  // 0 = BYTE mode UART      1 = CHAR mode UART

extern bool cali_ch0;
extern bool cali_ch1;

void set_VNA_path (uint8_t );
void VNA_get_measure (uint16_t* );
void VNA_send_data (uint8_t, uint16_t* );
uint16_t get_sweep_step_lin(uint16_t , uint16_t , uint16_t );

#endif
