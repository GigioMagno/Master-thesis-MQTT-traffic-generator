##################################### CLASS #############################################
################################### DOS_FRAME ###########################################
# CURRENT # 
# This class is designed to manage a frame for the Denial of Service attack.

from PyQt5.QtWidgets import (
	QWidget, QFormLayout, QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox
	)




class DosAttackConfig(QWidget):
    def __init__(self):
        super().__init__()
        layout = QFormLayout()

        #Topic textarea
        self.topic_input = QLineEdit()
        layout.addRow("Topic:", self.topic_input)

        #QoS selector
        self.qos_selector = QComboBox()
        self.qos_selector.addItems(["0", "1", "2"])
        layout.addRow("Quality of Service:", self.qos_selector)

        #Payload textarea
        self.payload_input = QLineEdit()
        layout.addRow("Payload:", self.payload_input)

        #Timing selector
        self.device_timing_selector = QComboBox()
        self.device_timing_selector.addItems(["Periodic"])
        layout.addRow("Device Timing:", self.device_timing_selector)

        #Period spinner
        self.period_input = QDoubleSpinBox()
        self.period_input.setSuffix(" s")
        layout.addRow("Period:", self.period_input)
        self.period_input.hide()

        #Num client spinner
        self.num_clients_input = QSpinBox()
        layout.addRow("Number of Clients:", self.num_clients_input)

        #Duration spinner
        self.duration_input = QDoubleSpinBox()
        self.duration_input.setSuffix(" s")
        layout.addRow("Duration:", self.duration_input)

        self.setLayout(layout)

        self.device_timing_selector.currentTextChanged.connect(self.update_timing_fields)
        self.update_timing_fields(self.device_timing_selector.currentText())




    def update_timing_fields(self, timing):
            self.period_input.show()