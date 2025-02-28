#define CRYSTAL_FRQ 192  //Cristal Freq in 10^5 Hz

void set_FRQ(uint32_t freq){
    uint8_t out_div = 0;
    uint16_t r_div =0, n_div = 0;
    uint32_t f_VCO = 0, f_PFD = 0;
    uint32_t reg0 = 0 , reg4 = 0;
    
    r_div = get_Rdiv();
    f_PFD = CRYSTAL_FRQ / r_div;
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

    MAX2870_write_register((reg4 & 0xFF8FFFFF) | (uint32_t) out_div << 20); //Output divider 
    MAX2870_write_register((reg0 & 0X80007FFF) | (uint32_t) n_div << 15); //N-Divider
}

void set_PWR(uint8_t pwr, uint8_t RF_out){

}

void set_Rdiv(uint16_t rdivider){

}

uint16_t get_Rdiv (void){
    uint16_t r_div;

    r_div = (uint16_t) ((MAX2870_get_register(REG2_CMD) & 0xFFC000) >> 14);

    return r_div;
}

uint16_t get_Ndiv (void){

}

void en_output (uint8_t RF_out){

}

void set_PLLmode(uint8_t mode){

}

void init_FRQ(void){

}