from conn import SerialClient
from models import Settings

serial_client = SerialClient()
settings = Settings()

dict_s2p = {
                "S11":1,
                "S21":3,
                "S22":5,
                "S12":7 
            }

stylesheet_tabs = """
            QTabBar::tab:selected {
                background-color: #80b85b; /* Color salmón para la pestaña seleccionada */
                color: black;             /* Texto blanco en la pestaña seleccionada */
                border-radius: 5px;       /* Bordes redondeados */
                padding: 5px;             /* Espaciado interno */
            }

            QTabBar::tab {
                background-color: #F0F0F0; /* Color gris claro para pestañas no seleccionadas */
                color: black;              /* Texto negro para pestañas no seleccionadas */
                border: 1px solid #CCCCCC; /* Bordes grises */
                padding: 5px;
            }
        """
