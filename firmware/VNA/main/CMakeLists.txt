idf_component_register(SRCS "vna_hw_interface.c" "rtos_init.c" "vna_task.c" "main.c"
                    INCLUDE_DIRS "include")
list(APPEND EXTRA_COMPONENT_DIRS components)