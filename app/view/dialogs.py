from PyQt5.QtWidgets import QFileDialog,QMessageBox,QWidget,QDialog,QProgressBar,QVBoxLayout\
                            ,QPushButton

class FileDialogManager():
    @staticmethod
    def get_open_filename(parent=None, caption="Select File", filter='S param files (*.csv *.s1p *.s2p)'):
        return QFileDialog.getOpenFileName(parent, caption, filter=filter)
    
class MessageBoxManager():
    @staticmethod
    def open_information_box(parent = None,title = "title", caption = ""):
        return QMessageBox.information(parent, title, caption)
    @staticmethod
    def open_warning_box(parent = None, caption = "No file selected"):
        return QMessageBox.warning(parent, "Warning", caption)
    @staticmethod
    def open_error_box(parent = None, caption = ""):
        return QMessageBox.critical(parent, "Error", caption)
    
class ProgressDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker_thread = None
        self.setWindowTitle("Processing")
        self.setModal(True)
        self.setFixedSize(300, 200)

        self.layout = QVBoxLayout()
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 0)  # Infinite progress
        self.layout.addWidget(self.progress_bar)

        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.clicked.connect(self.cancel_task)
        self.layout.addWidget(self.cancel_button)

        self.setLayout(self.layout)

    def set_worker_thread(self, thread):
        self.worker_thread = thread

    def cancel_task(self):
        if self.worker_thread:
            self.worker_thread.requestInterruption()  # Gracefully stop the thread
        self.reject()  # Close dialog