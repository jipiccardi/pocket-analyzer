idf_component_register(SRCS "rtos_init.c" "vna_task.c" "main.c"
                    INCLUDE_DIRS "include")
list(APPEND EXTRA_COMPONENT_DIRS components)