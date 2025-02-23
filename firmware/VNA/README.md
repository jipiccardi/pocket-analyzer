| Supported Targets | ESP32 | ESP32-C2 | ESP32-C3 | ESP32-C5 | ESP32-C6 | ESP32-H2 | ESP32-P4 | ESP32-S2 | ESP32-S3 |
| ----------------- | ----- | -------- | -------- | -------- | -------- | -------- | -------- | -------- | -------- |

# _POCKET ANALYZER_

El proyecto esta separado en componentes, uno por cada modulo que usamos, ver [este video](https://www.youtube.com/watch?v=VgzGsHgItbE&list=LL&index=1&t=53s) para ver como agregar un componente.

## Contenido de las carpetas

EL proyecto **POCKET ANALYZER** contiene un solo [main.c](main/main.c). Los componentes se encuentran en [components](components) entre ellos tenemos [spi](components/spi/), [gpio](components/gpio/), [adc](components/adc/), etc.


Abajo se ve la estructura de archivos.

```
├── CMakeLists.txt
├── main
│   ├── CMakeLists.txt
│   └── main.c
├── Components
|   ├──adc
|   ├──gpio
|   ├──max2870
|   ├──spi                     Todos los componentes tienen esta estructura de archivo
|   |   ├──include
|   |   |   ├──spi.h
|   |   ├──CMakeLists.txt
|   |   ├──spi.c
└── README.md                  This is the file you are currently reading
```

