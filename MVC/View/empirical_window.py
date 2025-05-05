##################################### CLASS #############################################
################################ EMPIRICAL_WINDOW #######################################
# CURRENT # 
# This class is designed to manage a frame for the Empirical mode.

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog)

# Panel for Empirical mode
class EmpiricalConfig(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        #Path for selected pcap file
        #self.pcap_path

        self.browse_button = QPushButton("Browse PCAP File")
        self.file_label = QLabel("No file selected")
        

        layout.addWidget(QLabel("Select PCAP File for Analysis:"))
        layout.addWidget(self.browse_button)
        layout.addWidget(self.file_label)

        self.setLayout(layout)