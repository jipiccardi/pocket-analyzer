#include "PR_max2870.h"
#include <unistd.h>



#define RF_MAIN 0
#define RF_AUX 1
#define CRYSTAL_FRQ_ADF4351 1000 //Son 100MHz

static uint32_t reg_str_adf[6] = {0,0,0,0,0,0};

void ADF4351_write_register(uint32_t data){
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
        reg_str_adf[(data & 0x7)] = data;
}

uint32_t ADF4351_get_register(uint8_t reg){
    if (reg < 6)
        return reg_str_adf[reg];
    else 
        return 0xFFFFFFFF;
}

void ADF4351_init(void){

    //Default values two times as datasheet indicates
    
    ADF4351_write_register(0x00400005);  //reg5
    vTaskDelay(20/portTICK_PERIOD_MS);
    ADF4351_write_register(0xF013FC); //reg4
    vTaskDelay(20/portTICK_PERIOD_MS);
    ADF4351_write_register(0x00800003);  //reg3
    vTaskDelay(20/portTICK_PERIOD_MS);
    ADF4351_write_register(0x11050E42); //reg2
    vTaskDelay(20/portTICK_PERIOD_MS);
    ADF4351_write_register(0x00008011);  //reg1
    vTaskDelay(20/portTICK_PERIOD_MS);
    ADF4351_write_register(0x1FC0000); //reg0
    vTaskDelay(20/portTICK_PERIOD_MS);

}


void set_FRQ_ADF4351(uint32_t f_out){
    uint8_t D_out_n = 0, D_out;
    uint16_t r_div2 = 0, r_doubler = 0, band_select = 0, r_counter = 0;
    uint16_t N = 0, FRAC = 0, MOD = 0;
    uint16_t res = 0; 
    uint32_t f_VCO = 0, f_PFD = 0;
    uint32_t reg0 = 0 , reg2 = 0,reg4 = 0, reg_mod = 0, reg1 = 0;

    reg4 =  ADF4351_get_register(REG4_CMD);
    reg2 =  ADF4351_get_register(REG2_CMD);
    reg1 =  ADF4351_get_register(REG1_CMD);
    reg0 =  ADF4351_get_register(REG0_CMD);

    D_out = (uint16_t) ((ADF4351_get_register(REG4_CMD) & 0x700000) >> 20); //Output Divider value
    r_doubler = (uint16_t) ((reg2 & 0x2000000) >> 25);  //Ref doubler selection
    r_div2 = (uint16_t) ((reg2 & 0x1000000) >> 24);     //Ref divider selection 
    r_counter = (uint16_t) ((reg2 & 0xFFC000) >> 14);   //Ref counter Selection
    band_select = 1; //Lo mantengo fijo

    MOD = (uint16_t) ((reg1 & 0x7FF8) >> 3);    //Modulus value selection

    f_PFD = CRYSTAL_FRQ_ADF4351 / r_counter;
    f_PFD <<= r_doubler;
    f_PFD >>= r_div2;
    
    //OUTPUT Divider Selection
    if(f_out < 687)            D_out_n = 6;
    else if (f_out < 1375)     D_out_n = 5;
    else if (f_out < 2750)     D_out_n = 4;  
    else if (f_out < 5500)     D_out_n = 3;
    else if (f_out < 11000)    D_out_n = 2;
    else if (f_out < 22000)    D_out_n = 1;
    else                       D_out_n = 0;

    //N and F selection
    f_VCO = f_out * (1 << D_out_n);
    N = (uint16_t) (f_VCO / f_PFD);
    res = (uint16_t) ((f_VCO % f_PFD)<<4)/f_PFD;
    FRAC = (res * MOD) >> 4;


    if (D_out_n != D_out){
        reg_mod = ((reg4 & ~0x700000) | (uint32_t) (D_out_n) << 20);
        ADF4351_write_register(reg_mod);
    }

    reg_mod = ((reg2 & ~0xFFC000) | (uint32_t) (r_counter) << 14)  ;
    ADF4351_write_register(reg_mod); //R-Divider

    /*  MOD queda fijo en 2
    *   reg_mod = ((reg1 & 0XFFFF8007) | (uint32_t) (MOD) << 3) ;
    *   ADF4351_write_register(reg_mod); //MOD Divider
    */


    reg_mod = ((reg0 & 0X80000007) | ((uint32_t) (N) << 15) | ((uint32_t) (FRAC) << 3));
    ADF4351_write_register(reg_mod); //N-Divider F-divider
    
    en_output_ADF4351(RF_MAIN, 1); //Enable RF output A
    en_output_ADF4351(RF_AUX, 1); //Enable RF output B
}



void en_output_ADF4351 (uint8_t RF_out, uint8_t status){
    uint32_t reg4;

    reg4 = ADF4351_get_register(REG4_CMD);

    if (RF_out == RF_MAIN)
        ADF4351_write_register((reg4 & ~0x20) | (uint32_t) (status) << 5);
    else if (RF_out == RF_AUX)
        ADF4351_write_register((reg4 & ~0x100) | (uint32_t) (status) << 8);
}

void configure_ADF4351_40MHZ(void){ 
    int32_t aux_reg;
    //N = 256 | FRAC = 1 | MOD = 2 | F_REF = 100M | R = 10 | F_pfd = 10M | D_out = 64 | F_out = 40.078M
    //Registro 4
    //Feedback Fundamental | Out Div = 64 | Band CLK Div = 1 | Outs enabled, divided, and full power 
    ADF4351_write_register(0xE011FC);

    //Registro 0
    //I = 256 | F = 1 (Frac Mode)
    ADF4351_write_register(0x1FC0000);

    //Registro 3
    //Band CLK Fast | Pulsewidth = FRAC-N | Charge Dissable | Cycle Slip dis | CLK Div OFF | CLK Div Val = 1 
    ADF4351_write_register(0x0080000B);

    //Registro 2
    //LowNoise Mode | MUX = VDD | R-Div2 & RDoub dis | R-counter = 10 | Doubler Buff Dis | CP current = 2.5 | LDF y LDP = Frac | PD Pol = Pos | Pow down - CP 3state - Counter Res = dis
    ADF4351_write_register(0x11028E42);
    ADF4351_write_register(0xFA0008);
    //Registro 1
    //P adj = off | Prescaler = 8/9 | P value = 1 | MOD = 2 
    ADF4351_write_register(0x8011);

    ADF4351_write_register(0x1FC0000);
    //Registro 0
    //I = 256 | F = 1 (Frac Mode)
    ADF4351_write_register(0xE00008);   
}