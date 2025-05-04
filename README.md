# MQTT Traffic Generator (MVC Edition)
## Introduction
This project is an enhanced and refactored version of the original [project](https://github.com/CamillaCP/MQTT-traffic-generator/tree/main).
The architecture of the program follows the well known MVC structural pattern, in order to separate domain logic from graphical components.
This application generates MQTT traffic simulating normal (publish/subscribe) and anomalous (Denial of Services and covert traffic) behaviours, useful to test the robustness of IoT networks.
## Main Features
- Realistic MQTT traffic generated using statistical distributions.
- Attacks simulations.
- Functions to generate covert traffic for the transmission of a covert message.
- MVC architecture in order to guarantee modularity, scalability and simpler maintainment of the source code.
- Intuitive GUI designed with PyQt.
## Project architecture
``Insert project tree``
### Model
Manages the domain logic and the communications using MQTT protocol:
- ``Generator.py``: contains the modelization and the logic that describes the behaviour of the Generator.
- ``MQTT_handler.py``: manages connections and operations with MQTT.
- ``EvilTasks.py``: implements the logic of attacks and covert channels.
### View
Manages the Graphic User Interface based on PyQt6:
- ``main_window.py``: main script to run and configure the entire generator.
- ``empirical_window.py``: graphic configuration for empirical distributions.
- ``manual_config.py``: graphic configuration to insert "by hand" parameters in order to create custom scenarios.
- ``DoS_frame.py``: graphic configuration for DoS attacks.
### Controller and Handlers
Manages interactions between user (View) and domain logic (Model):
- ``MVC_Controller.py``: orchestrates the behaviour of the entire application.
- ``Configs_Handler.py``: manages the devices configurations and parameters inserted by users.
- ``IO_Handler.py``: manages input/output (Load configs, Store custom configs...).
### Utils
Support classes:
- ``NetSniffer.py``: allows the capture of the generated traffic.
- ``Distributions.py``: manages the statistical distributions used in the generation of the traffic.
