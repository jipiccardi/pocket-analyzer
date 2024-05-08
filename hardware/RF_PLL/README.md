# Documentación del PLL para el generador de RF
Para el PLL del generador se eligieron los chips de la familia MAX287x de Analog Devices. La primera opción para el proyecto es el modelo MAX2871 que posee mejoras respecto al ruido  del MAX2870. Sin embargo, el chip deseado está momentáneamente fuera de stock por lo que se decide hacer el diseño y simulación con el MAX2870, ya que el fabricante asegura la compatibilidad entre los pines de ambos chips. Si el chip MAX2871 no se encuentra en stock al momento de realizar las compras se usará el chip MAX2870.

## Archivos 
* **MAX2870.pdf** : datasheet del chip 
* **MAX2871.pdf** : datasheet del chip 
* **max2870.ibs** : modelo de simuación para el chip. Este no es un modelo de spice sino un archivo con la característica V/I de salida de cada pin. Simularlo con tina, que da soporte a este tipo de archivos. 
  

## Enlaces de Interés

* **Página oficial del chip**: https://www.analog.com/en/products/max2871.html
https://www.analog.com/en/products/max2870.html
* **Página para descargar el simuldor de ruido de fase del chip**:
https://www.analog.com/en/resources/evaluation-hardware-and-software/software/software-download.html?swpart=SFW0007420A