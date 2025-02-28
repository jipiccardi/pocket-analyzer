#ifndef MAX2870_H
#define MAX2870_H

#define REG0_CMD 0x00
#define REG1_CMD 0x01
#define REG2_CMD 0x02
#define REG3_CMD 0x03
#define REG4_CMD 0x04
#define REG5_CMD 0x05
#define REG6_CMD 0x06

/**
*   @brief Funcion para escribir registro 0 a 5. Tambien guardar en memoria si corresponde a un registro de escritura el valor seteado
*
*    @note ESP32C es little endian, por lo que se guarda el byte menos signficativo en la direccion de memoria mas baja el cual se envia primero
*    MAX2870 necesita el byte mas significativo primero por lo que debo invertir el orden de guardado
*    
*    @param data Data value a enviar. Contiene tanto el dato como el address
*/
void MAX2870_write_register(uint32_t data);


/**
*   @brief Funcion para recuperar el ultimo valor del registro 0 a 5 escrito.
*
*    @note La funcion no lee del chip sino que lleva el registros de lo escrito, por lo que puede que no coincida con el real, ejemplo ante un reinicio del chip.
*    
*    @param reg MAX2870 register adress de 0 a 5. Usar Flags MAX2870_REGx_CMD.
*
*    @return Ultimo valor hexadecimal escrito en el registro. Puede no coincidir con el real.
*    Si el registro no esta entre 0 y 5 devuelve 0xFFFFFFFF
*/
uint32_t MAX2870_get_register(uint8_t reg);


/**
*   @brief Funcion para inicializar el dispositivo
*
*    @note Se escriben los registros con el valores en default 2 veces con un intervalo de 20mSeg entre escritura
*/
static void MAX2870_init(void);


/**
*   @brief Funcion para generar un barrido de frecuencias cada x delay. Solo usada para testear
*
*   @param sweep: Array con valores de frecuencias a evaluar. Deben ser enteros y expresarse en 1x10^5 Hz (10.5 MHZ = 105)
*    @param sz: Cantidad de frecuencias en el array. Usar sizeof(sweep) / sizeof(uint16_t) para obterner el tamaño antes de hacer el llamado a funcion
*   @param delay: Duracion de cada frecuencia medido en mSec.
*
*/
void sweep_MAX2870(const uint16_t* sweep, uint8_t sz, uint16_t delay);


#endif