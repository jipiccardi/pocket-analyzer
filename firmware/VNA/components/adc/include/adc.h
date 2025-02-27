#ifndef ADC_H
#define ADC_H
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "soc/soc_caps.h"
#include "esp_log.h"
#include "esp_adc/adc_oneshot.h"
#include "esp_adc/adc_cali.h"
#include "esp_adc/adc_cali_scheme.h"

static int adc_raw[2][10];
static int voltage[2][10];

void adc_init(void);
bool adc_calibration_init(adc_channel_t );
void adc_calibration_deinit(adc_channel_t );
int adc_read_channel_raw(adc_channel_t );
int adc_read_channel_cali(adc_channel_t , bool );
#endif 
