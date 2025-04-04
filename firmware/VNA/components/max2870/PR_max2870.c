#include "PR_max2870.h"
#include <unistd.h>

void set_FRQ(uint32_t freq){
    uint8_t out_div = 0,diva = 0;
    uint16_t r_div =0, n_div = 0;
    uint32_t f_VCO = 0, f_PFD = 0;
    uint32_t reg0 = 0 , reg4 = 0, reg_mod = 0;
    
    r_div = get_Rdiv();
    f_PFD = CRYSTAL_FRQ / r_div ;
    reg4 = MAX2870_get_register(REG4_CMD);
    reg0 = MAX2870_get_register(REG0_CMD);

    //OUTPUT Divider Selection
    if(freq < 469)            out_div = 7;
    else if (freq < 938)      out_div = 6;
    else if (freq < 1875)     out_div = 5;  
    else if (freq < 3750)     out_div = 4;
    else if (freq < 7500)     out_div = 3; 
    else if (freq < 15000)    out_div = 2;
    else if (freq < 30000)    out_div = 1;
    else                      out_div = 0;

    //Ndivider selection
    f_VCO = freq * (1 << out_div);
    n_div = f_VCO / f_PFD;
    
    diva = (uint16_t) ((MAX2870_get_register(REG4_CMD) & 0x700000) >> 20); //DIVA_Divider

    if (out_div != diva){
        reg_mod = ((reg4 & 0xFF8FFFFF) | (uint32_t) out_div << 20);
        MAX2870_write_register(reg_mod);
    }

    
    usleep(1000);
    reg_mod = ((reg0 & 0X80007FFF) | (uint32_t) n_div << 15);
    MAX2870_write_register(reg_mod); //N-Divider
}

uint16_t get_FRQ(void){
    uint16_t r_div, n_div, diva, f_OUT, f_VCO, f_PFD;

    r_div = get_Rdiv();
    n_div = (uint16_t) ((MAX2870_get_register(REG0_CMD) & 0x7FFF8000) >> 15); //N_Divider
    diva = (uint16_t) ((MAX2870_get_register(REG4_CMD) & 0x700000) >> 20); //DIVA_Divider
    

    f_PFD = CRYSTAL_FRQ / r_div;
    f_VCO = n_div * f_PFD; 
    f_OUT = f_VCO / (1 << diva);    

    return f_OUT;
}

void set_PWR(uint8_t pwr, uint8_t RF_out){

}

void set_Rdiv(uint16_t rdivider){
    uint32_t reg2, reg4;
    uint32_t bselect;
    
    reg2 = MAX2870_get_register(REG2_CMD);
    reg4 = MAX2870_get_register(REG4_CMD);

    
    bselect = CRYSTAL_FRQ * 100 / (rdivider * 50 ); // Band Select ecuation
    MAX2870_write_register((reg2 & ~0x00FFC000) | (uint32_t) rdivider << 14); //R-Divider 
    MAX2870_write_register((reg4 & ~0x000FF000) | (bselect & 0xFF << 12)); //Band Select [7:0] LSB
    MAX2870_write_register((reg4 & ~0x03000000) | (bselect & 0x300 << 16)); //Band Select [9:8] MSB

}

uint16_t get_Rdiv (void){
    uint16_t r_div;

    r_div = (uint16_t) ((MAX2870_get_register(REG2_CMD) & 0xFFC000) >> 14); //R-Divider

    
    return r_div;
}

void en_output (uint8_t RF_out, uint8_t status){
    uint32_t reg4;

    reg4 = MAX2870_get_register(REG4_CMD);

    if (RF_out == RF_A)
        MAX2870_write_register((reg4 & ~0x20) | (uint32_t) status << 5);
    else if (RF_out == RF_B)
        MAX2870_write_register((reg4 & ~0x100) | (uint32_t) status << 8);
}

void set_PLLmode(uint8_t mode){
    uint32_t reg_0, reg_1, reg_2;

    if (mode == INT_MODE){
        reg_2 = MAX2870_get_register(REG2_CMD);
        MAX2870_write_register((reg_2 & ~0x100) | (uint32_t) 1 << 8); // LD INT_N Mode

        reg_1 = MAX2870_get_register(REG1_CMD);
        MAX2870_write_register((reg_1 & ~0x80000000) | (uint32_t) 1 << 31); // CP_Clamp Enable | CP Lin Disable 

        reg_0 = MAX2870_get_register(REG0_CMD);
        MAX2870_write_register((reg_0 & ~0x80000000) | (uint32_t) 1 << 31); //INT_N Mode
    }
}

void init_FRQ_gen(void){

    MAX2870_init();

    /*Configuracion inicial del generador
    *   INT-N Mode
    *   R-div = 13 => Fpd =  1.43Mhz
    *   Fout = 23.5 Mhz 
    *   N = 2036
    *   MUX_OUT 3 states
    *   PA = 2db
    *   PB = 5db
    *   RFA y RFB dissable
    */
    MAX2870_write_register(0x01400005); // REG5
    vTaskDelay(20/portTICK_PERIOD_MS);
    MAX2870_write_register(0x61F801FC); // REG4
    vTaskDelay(20/portTICK_PERIOD_MS);
    MAX2870_write_register(0x0000000B); // REG3
    vTaskDelay(20/portTICK_PERIOD_MS);
    MAX2870_write_register(0x10004FD2); // REG2
    vTaskDelay(20/portTICK_PERIOD_MS);
    MAX2870_write_register(0x80008011); // REG1
    vTaskDelay(20/portTICK_PERIOD_MS);
    MAX2870_write_register(0x804E8000); // REG0 -> 23.5MHZ
}



void configure_MAX2870_20MHz(void){
    // Configuración básica del MAX2870 para generar 23 MHz con una referencia de 19.2 MHz
    
    // Registro 5: Configuración básica
    MAX2870_write_register(0x01400005); // Reset por seguridad
    // Registro 4 
    MAX2870_write_register(0x61F801FC); // DIVA = 128, RFOUTA habilitado
    // Registro 3: Configuración del VCO y autoselección
    MAX2870_write_register(0x0100000B); // Configuración básica del VCO
    // Registro 2: Configuración del divisor de referencia (R) y otros parámetros
    // R = 1, DBR = 0, RDIV2 = 0, MUXOUT = R divider output
    MAX2870_write_register(0x10004FD2); // R = 1, MUXOUT = R divider output
    // Registro 1: Configuración del valor de M (modulus)
    MAX2870_write_register(0x80008011);
    // Registro 0: Configuración del valor de N y F
    // N = 157, F = 0 (para 23 MHz)
    MAX2870_write_register(0x804E8000); // N = 157, F = 0
    //set_Rdiv(1);


//    XRA1403_set_gpio_level(LD_PIN, LOW);
//    XRA1403_set_gpio_level(CE_PIN, HIGH); // Habilitar el Charge Pump
//    XRA1403_set_gpio_level(RF_EN_PIN, HIGH);

    // Registro 0: Configuración del valor de N yF
    // N = 16, F = 0 (para 23 MHz)
   // MAX2870_write_register(0x804E8000);
    
}


void configure_MAX2870_FRAC(void){
    // Configuración básica del MAX2870 para generar 23 MHz con una referencia de 19.2 MHz
    
    // Registro 5: Configuración básica
    MAX2870_write_register(0x00400005); // Reset por seguridad
    
    // Registro 4 
    MAX2870_write_register(0x61F801FC); // DIVA = 128, RFOUTA habilitado
    
    // Registro 3: Configuración del VCO y autoselección
    MAX2870_write_register(0x0100000B); // Configuración básica del VCO
  
    // Registro 2: Configuración del divisor de referencia (R) y otros parámetros
    // R = 1, DBR = 0, RDIV2 = 0, MUXOUT = R divider output
    MAX2870_write_register(0x10004FD2); // R = 1, MUXOUT = R divider output
  
    // Registro 1: Configuración del valor de M (modulus)
    MAX2870_write_register(0x80008099);
   
    // Registro 0: Configuración del valor de N y F
    // N = 157, F = 0 (para 23 MHz)
    MAX2870_write_register(0x804E8000); // N = 157, F = 0

}