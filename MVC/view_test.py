##################################### CLASS #############################################
################################### VIEW_TEST ###########################################
# CURRENT # 
# This class is the entry point of the entire program. It has some configurations for the
# graphic components, and then it runs the generator.

from View.main_window import MainWindow
from PyQt5.QtCore import Qt, QPropertyAnimation, QPoint, QEasingCurve
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton, QLabel,
    QVBoxLayout, QHBoxLayout, QComboBox, QLineEdit, QFileDialog,
    QStackedWidget, QFormLayout, QSpinBox, QDoubleSpinBox, QTextEdit)
from Model.Generator.Generator import Generator
from Controller.MVC_Controller import MVC_Controller
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet("""
        QMainWindow {
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:1,
                stop:0 #0f2027,
                stop:0.5 #203a43,
                stop:1 #2c5364
            );
        }

        QDoubleSpinBox {
            background-color: rgba(255, 255, 255, 0.08);
        }

        QWidget {
            color: #ffffff;
            font-family: 'Arial';
            font-size: 14px;
        }

        QPushButton {
            background-color: rgba(255, 255, 255, 0.08);
            border: 1px solid #ffffff;
            border-radius: 8px;
            padding: 8px;
            min-width: 180px;
        }

        QPushButton:hover {
            background-color: rgba(255, 255, 255, 0.15);
        }

        QLineEdit, QTextEdit {
            background-color: rgba(255, 255, 255, 0.15);
            border: 1px solid #ffffff;
            border-radius: 6px;
            padding: 6px;
            min-width: 198px;
        }

        QComboBox {
            background-color: rgba(255, 255, 255, 0.15);
            border: 1px solid #ffffff;
            border-radius: 6px;
            padding: 6px;
            min-width: 180px; /* larghezza minima delle tendine */
            color: white;
        }

        QComboBox QAbstractItemView {
            background-color: rgba(0, 0, 0, 0.8);
            selection-background-color: #2c5364;
            selection-color: white;
            min-width: 180px; /* larghezza minima della dropdown */
        }
    """)
    window = MainWindow()
    gen = Generator(broker_address="broker.hivemq.com", port=1883)
    #gen = Generator(broker_address="public.mqtthq.com")
    #gen = Generator(port=80)
    #gen = Generator(broker_address="test.mosquitto.org", port=1883, interface="utun8") #SE VPN ON
    #gen = Generator(broker_address="test.mosquitto.org", port=1883)  #SE VPN OFF INTERFACCIA DA SETTARE en0 (WIFI-default)
    #gen = Generator(broker_address="127.0.0.1", port=1883, interface="lo0")
    controller = MVC_Controller(gen, window)

    window.show()
    sys.exit(app.exec_())