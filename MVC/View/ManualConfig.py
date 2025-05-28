##################################### CLASSES #############################################
################## MANUAL_CONFIG, PUBLISHER_CONFIG, SUBSCRIBER_CONFIG #####################
# CURRENT # 
# This set of classes is designed to manage frames for manual configuration (it contains all
# the necessary to read the fields filled by hand by the user).
# This frame manages other two subframes to manage subscriber configurations and publisher
# configurations.

from PyQt5.QtWidgets import (QWidget, QLabel, QVBoxLayout, QComboBox, QLineEdit, QStackedWidget, QFormLayout, QDoubleSpinBox)
from View.DoS_frame import DosAttackConfig

#Panel for manual insertion of configuration fields
class ManualConfig(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        #Choose role
        self.role_selector = QComboBox()
        self.role_selector.addItems(["Publisher", "Subscriber", "Denial of Service"])
        layout.addWidget(QLabel("Role:"))
        layout.addWidget(self.role_selector)

        #Choose protocol
        self.protocol_selector = QComboBox()
        self.protocol_selector.addItems(["MQTTv5", "MQTTv311"])
        layout.addWidget(QLabel("Protocol:"))
        layout.addWidget(self.protocol_selector)

        #Create a stack of widgets and fill it with proper configs
        self.role_stack = QStackedWidget()
        self.publisher_config = PublisherConfig()
        self.subscriber_config = SubscriberConfig()
        self.dos_config = DosAttackConfig()

        self.role_stack.addWidget(self.publisher_config)
        self.role_stack.addWidget(self.subscriber_config)
        self.role_stack.addWidget(self.dos_config)

        layout.addWidget(self.role_stack)

        self.setLayout(layout)
        self.role_selector.currentIndexChanged.connect(self.role_stack.setCurrentIndex)




#Publisher panel
class PublisherConfig(QWidget):

    def __init__(self):
        super().__init__()
        layout = QFormLayout()

        self.topic_input = QLineEdit()
        layout.addRow("Topic:", self.topic_input)

        self.qos_selector = QComboBox()
        self.qos_selector.addItems(["0", "1", "2"])
        layout.addRow("Quality of Service:", self.qos_selector)

        self.payload_input = QLineEdit()
        layout.addRow("Payload:", self.payload_input)

        self.device_timing_selector = QComboBox()
        self.device_timing_selector.addItems(["Event", "Periodic"])
        layout.addRow("Device Timing:", self.device_timing_selector)

        self.min_time_input = QDoubleSpinBox()
        self.min_time_input.setSuffix(" s")
        layout.addRow("Minimum Time Range:", self.min_time_input)

        self.max_time_input = QDoubleSpinBox()
        self.max_time_input.setSuffix(" s")
        layout.addRow("Maximum Time Range:", self.max_time_input)

        self.period_input = QDoubleSpinBox()
        self.period_input.setSuffix(" s")
        layout.addRow("Period:", self.period_input)
        self.period_input.hide()

        self.distribution_selector = QComboBox()
        self.distribution_selector.addItems(["Gaussian", "Exponential", "Uniform"])
        layout.addRow("Distribution Type:", self.distribution_selector)

        self.device_type_selector = QComboBox()
        self.device_type_selector.addItems(["Legit", "Counterfeit"])
        layout.addRow("Device Type:", self.device_type_selector)

        self.hidden_message_input = QLineEdit()
        layout.addRow("Hidden Message:", self.hidden_message_input)

        self.embedding_method_selector = QComboBox()
        self.embedding_method_selector.addItems(["First letter", "ID"])   #Choose proper methods
        layout.addRow("Embedding Method:", self.embedding_method_selector)

        self.retain_selector = QComboBox()
        self.retain_selector.addItem("True", True)
        self.retain_selector.addItem("False", False)
        layout.addRow("Retain:", self.retain_selector)

        self.setLayout(layout)

        self.device_timing_selector.currentTextChanged.connect(self.update_timing_fields)
        self.device_type_selector.currentTextChanged.connect(self.update_device_type_fields)

        self.update_timing_fields(self.device_timing_selector.currentText())
        self.update_device_type_fields(self.device_type_selector.currentText())


    def update_timing_fields(self, timing):
        if timing == "Event":
            self.min_time_input.show()
            self.max_time_input.show()
            self.period_input.hide()
        else:
            self.min_time_input.hide()
            self.max_time_input.hide()
            self.period_input.show()





    def update_device_type_fields(self, device_type):
        if device_type == "Counterfeit":
            self.hidden_message_input.show()
            self.embedding_method_selector.show()
        else:
            self.hidden_message_input.hide()
            self.embedding_method_selector.hide()




#Subscriber panel
class SubscriberConfig(QWidget):
    def __init__(self):
        super().__init__()
        layout = QFormLayout()

        self.topic_input = QLineEdit()
        layout.addRow("Topic:", self.topic_input)

        self.qos_selector = QComboBox()
        self.qos_selector.addItems(["0", "1", "2"])
        layout.addRow("Quality of Service:", self.qos_selector)

        self.setLayout(layout)