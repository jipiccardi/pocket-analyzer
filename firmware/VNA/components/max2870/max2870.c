#include <stdio.h>
#include "max2870.h"

static void MAX2870_init(void){

    //Default values two times as datasheet indicates
    
    MAX2870_write_register(REG5_CMD,0x4000005); 
    vTaskDelay(20/portTICK_PERIOD_MS);
    MAX2870_write_register(REG4_CMD,0x6180B21C); 
    vTaskDelay(20/portTICK_PERIOD_MS);
    MAX2870_write_register(REG3_CMD,0x0000000B);  
    vTaskDelay(20/portTICK_PERIOD_MS);
    MAX2870_write_register(REG2_CMD,0x00004042); 
    vTaskDelay(20/portTICK_PERIOD_MS);
    MAX2870_write_register(REG1_CMD,0x2000FFF9);  
    vTaskDelay(20/portTICK_PERIOD_MS);
    MAX2870_write_register(REG0_CMD,0x007D0000); 
    
    vTaskDelay(20/portTICK_PERIOD_MS);

    MAX2870_write_register(REG5_CMD,0x4000005); 
    vTaskDelay(20/portTICK_PERIOD_MS);
    MAX2870_write_register(REG4_CMD,0x6180B21C); 
    vTaskDelay(20/portTICK_PERIOD_MS);
    MAX2870_write_register(REG3_CMD,0x0000000B); 
    vTaskDelay(20/portTICK_PERIOD_MS);
    MAX2870_write_register(REG2_CMD,0x04004042); 
    vTaskDelay(20/portTICK_PERIOD_MS);
    MAX2870_write_register(REG1_CMD,0x2000FFF9); 
    vTaskDelay(20/portTICK_PERIOD_MS);
    MAX2870_write_register(REG0_CMD,0x007D0000); 
}


/*
*   Funcion para generar un barrido de frecuencias cada x delay
*   sweep: Array con valores de frecuencias a evaluar. Deben ser enteros y expresarse en 1x10^5 Hz (10.5 MHZ = 105)
*   sz: Cantidad de frecuencias en el array. Usar sizeof(sweep) / sizeof(uint16_t) para obterner el tamaño antes de hacer el llamado a funcion
*   delay: Duracion de cada frecuencia medido en mSec.
*/
void sweep_MAX2870(const uint16_t* sweep, uint8_t sz, uint16_t delay){
    uintt_t out_div = 0;

    for (int i = 0, i < sz, i++){
        //OUTPUT Divider Selection
        if(sweep[i]<469)            out_div = 7;
        else if (sweep[i]<938)      out_div = 6;
        else if (sweep[i]<1875)     out_div = 5;
        else if (sweep[i]<3750)     out_div = 4;
        else if (sweep[i]<7500)     out_div = 3;
        else if (sweep[i]<15000)    out_div = 2;
        else if (sweep[i]<30000)    out_div = 1;
        else                        out_div = 0;

        MAX2870_write_register(REG4_CMD, (0x61F801FC & 0xFF8FFFFF) | out_div << 20); //Output divider 
        MAX2870_write_register(REG0_CMD, (0x804E8000 & 0X80007FFF) | sweep[i] << 15); //N-Divider
        vTaskDelay(delay/portTICK_PERIOD_MS);
    }
}