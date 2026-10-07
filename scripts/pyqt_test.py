import sys
import logging
logging.basicConfig(level=logging.DEBUG)
print('Starting minimal PyQt6 test')
from PyQt6.QtWidgets import QApplication, QWidget
app = QApplication([])
print('QApplication created')
w = QWidget(); w.setWindowTitle('Test'); w.show(); print('Widget shown')
ret = app.exec()
print('Event loop exited', ret)
sys.exit(ret)
