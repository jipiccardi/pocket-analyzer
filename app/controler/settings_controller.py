from view.settings_window import SettingsWindow
from view.dialogs import MessageBoxManager
from globals import settings


class SettingsController():
    def __init__(self,main_window = None):
        self.view = SettingsWindow(main_window)

        self.view.f_start_text.setText(settings.get_values()['f_init'])
       
        self.view.f_end_text.setText(settings.get_values()['f_end'])
        
        self.view.n_steps_text.setText(settings.get_values()['n_step'])

        self.view.save_button.clicked.connect(self.save_button_clicked)
        
    def save_button_clicked(self):
        if self.view.f_start_text.text() == "" or self.view.f_end_text.text() == "" or self.n_steps_text.text() == "":
            MessageBoxManager.open_error_box(caption="All values are mandatory.")
            return
        settings.update_values(self.view.f_start_text.text(), self.view.f_end_text.text(), self.n_steps_text.text())
        self.view.close()