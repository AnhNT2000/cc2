import os
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
from main_app.controller.main_controller import MainController
from PyQt5.QtWidgets import QApplication
import sys

if __name__ == '__main__':
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QApplication(sys.argv)
    main_controller = MainController()
    sys.exit(app.exec_())