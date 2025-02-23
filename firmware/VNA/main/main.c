#include <stdio.h>
#include "esp_timer.h"
#include "esp_mac.h"
#include "spi.h"
#include "gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define portTICK_PERIOD_MS              ((TickType_t) (1000 / configTICK_RATE_HZ))

void app_main(void)
{
    spi_init();
    XRA1403_init();

    //probamos primero el gpio
    XRA1403_set_gpio_level(0,HIGH);
    vTaskDelay(2000/portTICK_PERIOD_MS);
    XRA1403_set_gpio_level(0,LOW);

    spi_deinit();

}
