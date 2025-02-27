#include <stdio.h>
#include "max2870.h"

uint32_t reg_str[6] = {0,0,0,0,0,0}; 

/**
*   @brief Funcion para escribir registro 0 a 5. Tambien guardar en memoria si corresponde a un registro de escritura el valor seteado
*
    @note ESP32C es little endian, por lo que se guarda el byte menos signficativo en la direccion de memoria mas baja el cual se envia primero
    MAX2870 necesita el byte mas significativo primero por lo que debo invertir el orden de guardado
    
    @param reg MAX2870 register adress de 0 a 5. Usar Flags MAX2870_REGx_CMD. Igual no se usa
    @param data Data value a enviar. Contiene tanto el dato como el address

*/
static void MAX2870_write_register(uint8_t reg, uint32_t data){
    spi_transaction_t t;
    uint32_t my_buff[1] = {0};
    uint8_t tx_data_test[4]={0,0,0,0};
    
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
    printf("\n Write Register Ok");
 
    //Guardo el cambio si correspode, del REG0 al REG5
    if ((data & 0x7) < 6) 
        reg_str[(data & 0x7)] = data;
}


/**
*   @brief Funcion para recuperar el ultimo valor del registro 0 a 5 escrito.
*
    @note La funcion no lee del chip sino que lleva el registros de lo escrito, por lo que puede que no coincida con el real, ejemplo ante un reinicio del chip.
    
    @param reg MAX2870 register adress de 0 a 5. Usar Flags MAX2870_REGx_CMD.

    @return Ultimo valor hexadecimal escrito en el registro. Puede no coincidir con el real.
    Si el registro no esta entre 0 y 5 devuelve 0xFFFFFFFF

*/
uint32_t MAX2870_get_register(uint8_t reg){
    if (reg < 6)
        return reg_str[reg];
    else 
        return 0xFFFFFFFF;
}

/*
*   Funcion para inicializar el MAX2870. 
*   Se escriben los valores por default 2 veces con un lapso de 20mSec.
*/
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
    uint8_t out_div = 0;

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

        MAX2870_write_register(REG4_CMD, (0x61F801FC & 0xFF8FFFFF) | (uint32_t)out_div << 20); //Output divider 
        MAX2870_write_register(REG0_CMD, (0x804E8000 & 0X80007FFF) | (uint32_t)sweep[i] << 15); //N-Divider
        vTaskDelay(delay/portTICK_PERIOD_MS);
    }
}