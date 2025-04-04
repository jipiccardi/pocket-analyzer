#include "max2870.h"
#include "PR_max2870.h"

static uint32_t reg_str_adf[6] = {0,0,0,0,0,0};


#define RF_MAIN 0
#define RF_AUX 1
#define CRYSTAL_FRQ_ADF4351 350 //Son 35MHz

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
    spi_device_transmit(ADF4351_handle, &t);
    //printf("\n Write Register Ok");
 
    //Guardo el cambio si correspode, del REG0 al REG5
    if ((data & 0x7) < 6) 
        reg_str_adf[(data & 0x7)] = data;
}

void ADF4351_init(void){

    //Default values two times as datasheet indicates
    
    MAX2870_write_register(0x400005);  //reg5
    vTaskDelay(20/portTICK_PERIOD_MS);
    MAX2870_write_register(0x8014DC); //reg4
    vTaskDelay(20/portTICK_PERIOD_MS);
    MAX2870_write_register(0x800003);  //reg3
    vTaskDelay(20/portTICK_PERIOD_MS);
    MAX2870_write_register(0x400CE42); //reg2
    vTaskDelay(20/portTICK_PERIOD_MS);
    MAX2870_write_register(0x8011);  //reg1
    vTaskDelay(20/portTICK_PERIOD_MS);
    MAX2870_write_register(0xB8000); //reg0
    vTaskDelay(20/portTICK_PERIOD_MS);

}

uint32_t ADF4351_get_register(uint8_t reg){
    if (reg < 6)
        return reg_str_adf[reg];
    else 
        return 0xFFFFFFFF;
}

void set_FRQ_ADF4351(uint32_t freq){
    uint8_t out_div = 0,diva = 0;
    uint16_t r_div =0, band_select = 0;
    uint16_t N = 0, FRAC = 0, MOD = 0;
    uint16_t res = 1; //1MHz
    uint32_t f_VCO = 0, f_PFD = 0;
    uint32_t reg0 = 0 , reg2 = 0,reg4 = 0, reg_mod = 0, reg1 = 0;

    diva = (uint16_t) ((ADF4351_get_register(REG4_CMD) & 0x700000) >> 20); //DIVA_Divider
    
    r_div = 2; //Lo mantengo fijo
    band_select = 175; //Lo mantengo fijo

    f_PFD = CRYSTAL_FRQ_ADF4351 / r_div ;
    reg4 =  ADF4351_get_register(REG4_CMD);
    reg2 =  ADF4351_get_register(REG2_CMD);
    reg1 =  ADF4351_get_register(REG1_CMD);
    reg0 =  ADF4351_get_register(REG0_CMD);

    //OUTPUT Divider Selection
    if(freq < 687)            out_div = 6;
    else if (freq < 1375)      out_div = 5;
    else if (freq < 2750)     out_div = 4;  
    else if (freq < 5500)     out_div = 3;
    else if (freq < 11000)    out_div = 2;
    else if (freq < 22000)    out_div = 1;
    else                      out_div = 0;

    //Ndivider selection
    f_VCO = freq * (1 << out_div);
    N = (uint16_t) (f_VCO / f_PFD);
    MOD = (uint16_t) (f_PFD / res);
    FRAC = (uint16_t) ( ( ((float) (f_VCO / f_PFD)) -  ((float) N) ) * (float) MOD );


    if (out_div != diva){
        reg_mod = ((reg4 & 0xFF8FFFFF) | (uint32_t) (out_div) << 20);
        ADF4351_write_register(reg_mod);
    }

    
    usleep(1000);
    
    reg_mod = ((reg4 & 0XFF800FFF) | ((uint32_t) (out_div) << 20) | ((uint32_t) (band_select) << 12) ));
    ADF4351_write_register(reg_mod); //Output divider Band Select

    reg_mod = ((reg2 & 0XFF003FFF) | (uint32_t) (r_div) << 14)  ;
    ADF4351_write_register(reg_mod); //R-Divider

    reg_mod = ((reg1 & 0XFFFF8007) | (uint32_t) (MOD) << 3) | ;
    ADF4351_write_register(reg_mod); //MOD Divider

    reg_mod = ((reg0 & 0X80000007) | ((uint32_t) (N) << 15) | ((uint32_t) (FRAC) << 15));
    ADF4351_write_register(reg_mod); //N-Divider FRAC divider
    
    en_output_ADF4351(RF_MAIN, 1); //Enable RF output A
    en_output_ADF4351(RF_AUX, 1); //Enable RF output B
}

void en_output_ADF4351 (uint8_t RF_out, uint8_t status){
    uint32_t reg4;

    reg4 = ADF4351_write_register(REG4_CMD);

    if (RF_out == RF_MAIN)
        ADF4351_write_register((reg4 & ~0x20) | (uint32_t) (status) << 5);
    else if (RF_out == RF_AUX)
        ADF4351_write_register((reg4 & ~0x100) | (uint32_t) (status) << 8);
}