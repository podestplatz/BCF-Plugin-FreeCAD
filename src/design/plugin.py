import sys
from PySide2.QtWidgets import QApplication, QMainWindow
from ui_plugin import Ui_Form

class MainWindow(QMainWindow, Ui_Form):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    plugin = MainWindow()
    plugin.show()
    app.exec_()
