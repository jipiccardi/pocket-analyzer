
#include "max2870.h"

static uint32_t reg_str[6] = {0,0,0,0,0,0}; 


void MAX2870_write_register(uint32_t data){
    spi_transaction_t t;
    
    memset(&t, 0, sizeof(t));
    t.flags = SPI_TRANS_USE_TXDATA;
    t.cmd = 0;
    t.addr= 0;
    t.length = 32;

    //Little Endian correction
    t.tx_data[3] = (data & 0xFF);           // Primer byte (8 bits)   
    t.tx_data[2] = (data >> 8) & 0xFF;      // Segundo byte (8 bits)
    t.tx_data[1] = (data >> 16) & 0xFF;     // Tercer byte (8 bits)
    t.tx_data[0] = (data >> 24) & 0xFF;     // Cuarto byte (8 bits)
    spi_device_transmit(MAX2870_handle, &t);
    //printf("\n Write Register Ok");
 
    //Guardo el cambio si correspode, del REG0 al REG5
    if ((data & 0x7) < 6) 
        reg_str[(data & 0x7)] = data;
}



uint32_t MAX2870_get_register(uint8_t reg){
    if (reg < 6)
        return reg_str[reg];
    else 
        return 0xFFFFFFFF;
}


void MAX2870_init(void){

    //Default values two times as datasheet indicates
    
    MAX2870_write_register(0x4000005); 
    vTaskDelay(20/portTICK_PERIOD_MS);
    MAX2870_write_register(0x6180B21C); 
    vTaskDelay(20/portTICK_PERIOD_MS);
    MAX2870_write_register(0x0000000B);  
    vTaskDelay(20/portTICK_PERIOD_MS);
    MAX2870_write_register(0x00004042); 
    vTaskDelay(20/portTICK_PERIOD_MS);
    MAX2870_write_register(0x2000FFF9);  
    vTaskDelay(20/portTICK_PERIOD_MS);
    MAX2870_write_register(0x007D0000); 
    
    vTaskDelay(20/portTICK_PERIOD_MS);

    MAX2870_write_register(0x4000005); 
    vTaskDelay(20/portTICK_PERIOD_MS);
    MAX2870_write_register(0x6180B21C); 
    vTaskDelay(20/portTICK_PERIOD_MS);
    MAX2870_write_register(0x0000000B); 
    vTaskDelay(20/portTICK_PERIOD_MS);
    MAX2870_write_register(0x04004042); 
    vTaskDelay(20/portTICK_PERIOD_MS);
    MAX2870_write_register(0x2000FFF9); 
    vTaskDelay(20/portTICK_PERIOD_MS);
    MAX2870_write_register(0x007D0000); 
}


void sweep_MAX2870(const uint16_t* sweep, uint8_t sz, uint16_t delay){
    uint8_t out_div = 0;

    for (int i = 0; i < sz; i++){
        //OUTPUT Divider Selection
        if(sweep[i]<469)            out_div = 7;
        else if (sweep[i]<938)      out_div = 6;
        else if (sweep[i]<1875)     out_div = 5;
        else if (sweep[i]<3750)     out_div = 4;
        else if (sweep[i]<7500)     out_div = 3; 
        else if (sweep[i]<15000)    out_div = 2;
        else if (sweep[i]<30000)    out_div = 1;
        else                        out_div = 0;

        MAX2870_write_register( (0x61F801FC & 0xFF8FFFFF) | (uint32_t)out_div << 20); //Output divider 
        MAX2870_write_register( (0x804E8000 & 0X80007FFF) | (uint32_t)sweep[i] << 15); //N-Divider
        vTaskDelay(delay/portTICK_PERIOD_MS);
    }
}