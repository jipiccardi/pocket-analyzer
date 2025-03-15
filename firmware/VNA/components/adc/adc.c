#include "adc.h"

const static char *TAG = "ADC";
adc_oneshot_unit_handle_t adc_handle = NULL; //handle del adc

adc_cali_handle_t adc_cali_chan0_handle = NULL; //handle para la calibracion
adc_cali_handle_t adc_cali_chan1_handle = NULL;

/**
 * @brief Inicializa los recursos del adc, usa siempre la ADC_UNIT1 y la atenuación maxima
 * Solo se usan los ADC_CHANNEL_0 y ADC_CHANNEL_1
 */
void adc_init(void){
    adc_oneshot_unit_init_cfg_t init_config = {
        .unit_id = ADC_UNIT_1, //uso siempre la unidad 1
        .ulp_mode = ADC_ULP_MODE_DISABLE
    };
    ESP_ERROR_CHECK(adc_oneshot_new_unit(&init_config, &adc_handle)); //agrego el handler del adc
    
    //-------------ADC Config---------------//
    //COnfiguramos los gpio para que sean canales del ADC
    adc_oneshot_chan_cfg_t config = {
        .bitwidth = ADC_BITWIDTH_12, //Salidas de 12 bits
        .atten = ADC_ATTEN_DB_6, //uso 6db
    };
    //Agrego los canales del adc que voy a usar
    ESP_ERROR_CHECK(adc_oneshot_config_channel(adc_handle, ADC_CHANNEL_0, &config));
    ESP_ERROR_CHECK(adc_oneshot_config_channel(adc_handle, ADC_CHANNEL_1, &config));
}

/**
 * @brief Genera los recursos adecuados para calibrar el canal del adc especificado
 * Retorna un bool que indica si se calibro correctamente el canal o no
 */
bool adc_calibration_init(adc_channel_t channel)
{
    
    adc_cali_handle_t handle = NULL;
    esp_err_t ret = ESP_FAIL;
    bool calibrated = false;

    if (!calibrated) {
        ESP_LOGI(TAG, "calibration scheme version is %s", "Curve Fitting");
        adc_cali_curve_fitting_config_t cali_config = {
            .unit_id = ADC_UNIT_1, //uso siempre la unidad 1
            .chan = channel,
            .atten = ADC_ATTEN_DB_6, 
            .bitwidth = ADC_BITWIDTH_DEFAULT,
        };
        ret = adc_cali_create_scheme_curve_fitting(&cali_config, &handle);
        if (ret == ESP_OK) {
            calibrated = true;  
        }
    }
    if (channel == ADC_CHANNEL_0)
        adc_cali_chan0_handle = handle;
    else if (channel == ADC_CHANNEL_1)
        adc_cali_chan1_handle = handle;

    //Chekc de que todo salio bien    
    if (ret == ESP_OK) {
        ESP_LOGI(TAG, "Calibration Success");
    } else if (ret == ESP_ERR_NOT_SUPPORTED || !calibrated) {
        ESP_LOGW(TAG, "eFuse not burnt, skip software calibration");
    } else {
        ESP_LOGE(TAG, "Invalid arg or no memory");
    }

    return calibrated;
}

/**
 * @brief Libera los recursos usados por un canal del adc para la calibracion
 */
void adc_calibration_deinit(adc_channel_t channel)
{   
    ESP_LOGI(TAG, "deregister %s calibration scheme", "Curve Fitting");
    if (channel == ADC_CHANNEL_0)
        ESP_ERROR_CHECK(adc_cali_delete_scheme_curve_fitting(adc_cali_chan0_handle));
    else if (channel == ADC_CHANNEL_1)
        ESP_ERROR_CHECK(adc_cali_delete_scheme_curve_fitting(adc_cali_chan1_handle));
}

/**
 * @brief Leo en cuentas un canal del adc
 */
int adc_read_channel_raw(adc_channel_t channel){

    //Leo el valor en cuentas
    ESP_ERROR_CHECK(adc_oneshot_read(adc_handle, channel, &adc_raw[0][0]));
    ESP_LOGI(TAG, "ADC%d Channel[%d] Raw Data: %d", ADC_UNIT_1 + 1, channel, adc_raw[0][0]);
    
    return adc_raw[0][0];
}

/**
 * @brief Leo en tension un canal del adc, necesito indicarle si se calibro o no el canal
 * En caso de que no se haya calibrado retorna -1
 */
int adc_read_channel_cali(adc_channel_t channel, bool do_calibration_chan){
    adc_cali_handle_t cali_handle = NULL;

    //Veo que canal corresponde
    if (channel == ADC_CHANNEL_0)
        cali_handle = adc_cali_chan0_handle;
    else if (channel == ADC_CHANNEL_1)
        cali_handle = adc_cali_chan1_handle;

    //Leo el valor en cuentas
    adc_oneshot_read(adc_handle, channel, &adc_raw[0][0]);
    //ESP_LOGI(TAG, "ADC%d Channel[%d] Raw Data: %d", ADC_UNIT_1 + 1, channel, adc_raw[0][0]);
        if (do_calibration_chan) {
            //Leo el valor en voltaje con la calibracion
            adc_cali_raw_to_voltage(cali_handle, adc_raw[0][0], &voltage[0][0]);
            //ESP_LOGI(TAG, "ADC%d Channel[%d] Cali Voltage: %d mV", ADC_UNIT_1 + 1, channel, voltage[0][0]);

            return voltage[0][0]; //En caso de estar calibrado retorna el valor correspondiente
        }
        else
            return -1; //En caso de que no este calibrado retorna -1
}