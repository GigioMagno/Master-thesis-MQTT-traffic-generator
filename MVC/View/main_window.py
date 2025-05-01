from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QPushButton,
    QVBoxLayout, QHBoxLayout, QStackedWidget, QFileDialog
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QPoint, QEasingCurve
from View.manual_config import ManualConfig
from View.empirical_window import EmpiricalConfig

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Device Configuration")
        self.setGeometry(100, 100, 1000, 600)

        #Paths...
        #self.load_csv_path
        #self.save_csv_path


        # Main layout
        main_layout = QHBoxLayout()
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Side Menu + Buttons
        self.menu_layout = QVBoxLayout()
        self.menu_layout.setAlignment(Qt.AlignTop)
        self.manual_config_button = QPushButton("Manual Configuration")
        self.empirical_mode_button = QPushButton("Empirical Distribution Mode")
        self.menu_layout.addWidget(self.manual_config_button)
        self.menu_layout.addWidget(self.empirical_mode_button)
        self.menu_layout.addStretch()  # Spinge i bottoni in alto

        #Footer layout + buttons
        self.footer_layout = QVBoxLayout()
        self.footer_layout.setAlignment(Qt.AlignBottom)
        self.add_config = QPushButton("Add configuration")
        self.save_to_csv = QPushButton("Save to csv")
        self.load_csv = QPushButton("Load configs from csv")
        self.run_gen = QPushButton("Run generator")
        self.stop_gen = QPushButton("Stop generator")
        self.footer_layout.addWidget(self.add_config)
        self.footer_layout.addWidget(self.save_to_csv)
        self.footer_layout.addWidget(self.load_csv)
        self.footer_layout.addWidget(self.run_gen)
        self.footer_layout.addWidget(self.stop_gen)

        # Append footer to side menu
        self.menu_layout.addLayout(self.footer_layout)

        # Frame menu (container)
        self.menu_frame = QWidget()
        self.menu_frame.setLayout(self.menu_layout)

        # Pages stack: manual configuration - empirical configuration
        self.stack = QStackedWidget()
        self.manual_config = ManualConfig()
        self.empirical_config = EmpiricalConfig()
        self.stack.addWidget(self.manual_config)
        self.stack.addWidget(self.empirical_config)

        # Add the pages stack to main layout + add the menu frame to main layout
        main_layout.addWidget(self.menu_frame, 1)
        main_layout.addWidget(self.stack, 4)

        # Switch page button
        self.manual_config_button.clicked.connect(lambda: self.switch_page(0))
        self.empirical_mode_button.clicked.connect(lambda: self.switch_page(1))
        
    # Switch page given index
    def switch_page(self, index):
        current_index = self.stack.currentIndex()
        
        if current_index == index:
            return

        direction = 1 if index > current_index else -1
        current_widget = self.stack.currentWidget()
        next_widget = self.stack.widget(index)
        next_widget.setGeometry(self.stack.geometry())
        next_widget.move(direction * self.stack.width(), 0)
        next_widget.show()

        self.anim_current = QPropertyAnimation(current_widget, b"pos")
        self.anim_current.setDuration(300)
        self.anim_current.setStartValue(current_widget.pos())
        self.anim_current.setEndValue(current_widget.pos() - QPoint(direction * self.stack.width(), 0))
        self.anim_current.setEasingCurve(QEasingCurve.InOutQuad)

        self.anim_next = QPropertyAnimation(next_widget, b"pos")
        self.anim_next.setDuration(300)
        self.anim_next.setStartValue(next_widget.pos())
        self.anim_next.setEndValue(self.stack.geometry().topLeft())
        self.anim_next.setEasingCurve(QEasingCurve.InOutQuad)

        self.anim_current.start()
        self.anim_next.start()
        self.anim_next.finished.connect(lambda: self.stack.setCurrentIndex(index))