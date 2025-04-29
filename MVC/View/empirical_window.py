from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog)

# Panel for Empirical mode
class EmpiricalConfig(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        self.browse_button = QPushButton("Browse PCAP File")
        self.file_label = QLabel("No file selected")
        self.browse_button.clicked.connect(self.browse_file)

        layout.addWidget(QLabel("Select PCAP File for Analysis:"))
        layout.addWidget(self.browse_button)
        layout.addWidget(self.file_label)

        self.setLayout(layout)

    # Function for file browsing
    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open PCAP File", "", "PCAP Files (*.pcap *.pcapng);;All Files (*)")
        if file_path:
            
            self.file_label.setText(file_path)
        else:

            self.file_label.setText("No file selected")