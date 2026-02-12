.. _sys3_system_architecture:

SYS.3 - System Architecture Specification
==========================================

.. contents::
   :local:
   :depth: 1

**Document:** SYS-ARCH-SPEC-001
**Version:** 1.0
**Status:** Approved
**Domain:** Anti-Lock Braking System (ABS)

----

System Overview Architecture
------------------------------

.. sys_arch:: ABS System Overview - Component Architecture
   :id: SYS_ARCH_001
   :status: approved
   :derives_from: SYS_REQ_001, SYS_REQ_007, SYS_REQ_011
   :tags: architecture; system-overview; component
   :aspice_process: SYS.3
   :safety_class: ASIL-D
   :verification_method: inspection

   The ABS system consists of the following primary functional components:

   +----------------------+----------------------------------+---------------------------+
   | Component            | Function                         | Interface                 |
   +======================+==================================+===========================+
   | WSS (×4)             | Wheel speed sensing              | 12V pulse signal to ECU   |
   +----------------------+----------------------------------+---------------------------+
   | ABS ECU              | Central processing & control     | CAN, HCU control signals  |
   +----------------------+----------------------------------+---------------------------+
   | HCU                  | Hydraulic pressure modulation    | Solenoid/pump from ECU    |
   +----------------------+----------------------------------+---------------------------+
   | Brake Calipers (×4)  | Braking force application        | Hydraulic pressure        |
   +----------------------+----------------------------------+---------------------------+
   | ABS Warning Lamp     | Driver fault notification        | Digital signal from ECU   |
   +----------------------+----------------------------------+---------------------------+
   | CAN Bus              | Vehicle network communication    | CAN 2.0B @ 500 kbps       |
   +----------------------+----------------------------------+---------------------------+

**System Component Diagram:**

.. uml::
   :caption: ABS System Component Architecture

   @startuml ABS_System_Architecture
   skinparam componentStyle rectangle
   skinparam backgroundColor #FAFAFA
   skinparam component {
     BackgroundColor #BFD7EA
     BorderColor #2E86AB
     ArrowColor #1565C0
   }
   skinparam note {
     BackgroundColor #FFFDE7
   }

   title Anti-Lock Braking System - System Architecture (SYS.3)

   package "Driver Input" {
     [Brake Pedal\nSensor] as BPS
   }

   package "Wheel Speed Sensing" {
     [WSS\nFront Left] as WSS_FL
     [WSS\nFront Right] as WSS_FR
     [WSS\nRear Left] as WSS_RL
     [WSS\nRear Right] as WSS_RR
   }

   package "ABS Control Unit" as ECU_PKG {
     [ABS ECU\n(32-bit MCU)] as ECU
   }

   package "Hydraulic Actuation" {
     [Hydraulic\nControl Unit\n(HCU)] as HCU
     [Brake Caliper FL] as BRK_FL
     [Brake Caliper FR] as BRK_FR
     [Brake Caliper RL] as BRK_RL
     [Brake Caliper RR] as BRK_RR
   }

   package "Vehicle Network" {
     [CAN Bus\n500 kbps] as CAN
   }

   package "Driver Feedback" {
     [ABS Warning\nLamp] as LAMP
   }

   BPS --> ECU : brake pressure signal
   WSS_FL --> ECU : wheel speed pulse (12V, ~1kHz)
   WSS_FR --> ECU : wheel speed pulse (12V, ~1kHz)
   WSS_RL --> ECU : wheel speed pulse (12V, ~1kHz)
   WSS_RR --> ECU : wheel speed pulse (12V, ~1kHz)
   ECU --> HCU : solenoid valve commands (4 inlet + 4 outlet)
   ECU --> HCU : pump motor PWM control
   ECU --> LAMP : fault indication (12V digital)
   ECU <--> CAN : wheel speeds, ABS status, diagnostics
   HCU --> BRK_FL : hydraulic pressure
   HCU --> BRK_FR : hydraulic pressure
   HCU --> BRK_RL : hydraulic pressure
   HCU --> BRK_RR : hydraulic pressure

   note right of ECU
     Processor: 32-bit MCU @ 80 MHz
     Control cycle: 5 ms (200 Hz)
     RAM: 64 KB  ROM: 512 KB
     Operating voltage: 9–16 V DC
   end note

   note bottom of HCU
     4× inlet solenoid valves
     4× outlet solenoid valves
     1× hydraulic pump motor
   end note
   @enduml

----

ECU Architecture
-----------------

.. sys_arch:: ABS ECU Internal Functional Architecture
   :id: SYS_ARCH_002
   :status: approved
   :derives_from: SYS_REQ_003, SYS_REQ_004, SYS_REQ_005, SYS_REQ_006
   :tags: architecture; ecu; functional-decomposition
   :aspice_process: SYS.3
   :safety_class: ASIL-D
   :verification_method: inspection

   The ABS ECU internal functions are decomposed into the following modules:

   1. **Sensor Input Processing** – Acquires and filters wheel speed data
   2. **Vehicle Speed Estimation** – Computes vehicle reference speed
   3. **Slip Ratio Calculator** – Computes per-wheel slip ratios
   4. **ABS Control Algorithm** – Makes pressure modulation decisions
   5. **Actuator Output Driver** – Drives HCU solenoid valves and pump
   6. **Fault Manager** – Monitors system health and manages DTCs
   7. **Communication Manager** – Handles CAN Tx/Rx
   8. **Diagnostic Service** – Handles UDS/OBD-II requests

**ECU Functional Block Diagram:**

.. uml::
   :caption: ABS ECU Internal Functional Architecture

   @startuml ABS_ECU_Architecture
   skinparam packageStyle rectangle
   skinparam backgroundColor #FAFAFA
   skinparam component {
     BackgroundColor #BBDEFB
     BorderColor #1565C0
   }

   title ABS ECU - Internal Functional Architecture (SYS.3)

   package "ECU Inputs" {
     [WSS Input\nInterface] as WSS_IN
     [Brake Pressure\nInput] as BPS_IN
   }

   package "ABS Processing Core" {
     [Sensor Input\nProcessor] as SIP
     [Vehicle Speed\nEstimator] as VSE
     [Slip Ratio\nCalculator] as SRC
     [ABS Control\nAlgorithm] as ACA
   }

   package "ECU Outputs" {
     [HCU Actuator\nDriver] as HCU_DRV
     [Warning Lamp\nDriver] as LAMP_DRV
   }

   package "System Services" {
     [Fault Manager] as FM
     [CAN Manager] as CAN_MGR
     [Diagnostic\nService (UDS)] as DIAG
     [NVM Manager] as NVM
   }

   WSS_IN --> SIP : raw WSS signals (4 channels)
   BPS_IN --> ACA : brake demand
   SIP --> VSE : filtered wheel speeds
   SIP --> SRC : filtered wheel speeds
   VSE --> SRC : vehicle reference speed
   SRC --> ACA : slip ratios (4 channels)
   ACA --> HCU_DRV : valve commands (BUILD/HOLD/RELEASE)
   FM --> LAMP_DRV : fault status
   FM --> NVM : store DTCs
   FM <-- SIP : sensor fault status
   FM <-- HCU_DRV : actuator fault status
   CAN_MGR --> DIAG : UDS requests
   CAN_MGR <-- ACA : ABS status, wheel speeds

   note right of ACA
     Cycle time: 5ms
     4 independent channels
     Select-low logic (rear axle)
   end note
   @enduml

----

Wheel Speed Sensing Architecture
----------------------------------

.. sys_arch:: Wheel Speed Sensor Subsystem Architecture
   :id: SYS_ARCH_003
   :status: approved
   :derives_from: SYS_REQ_001, SYS_REQ_002, SYS_REQ_017
   :tags: architecture; wss; sensing; interface
   :aspice_process: SYS.3
   :safety_class: ASIL-D
   :verification_method: inspection

   Each wheel speed sensor (WSS) is a passive inductive or active Hall-effect sensor
   mounted at each wheel hub. The ECU interfaces with all four sensors via dedicated
   capture input channels.

   **Signal characteristics:**

   - Sensor type: Active Hall-effect (12V supply, differential output)
   - Signal format: Square wave pulse train, frequency proportional to wheel speed
   - Speed resolution: ±0.5 km/h at 50 km/h
   - Cable impedance: 120 Ω (differential)
   - ECU input: Schmitt-trigger input, VIH = 7 V, VIL = 3 V

   **Fault detection capability:**

   - Open circuit: detected by supply current monitoring (< 20 mA = open)
   - Short to ground: detected by over-current monitor (> 500 mA = short)
   - Plausibility: adjacent wheel comparison at 10 ms rate

----

Hydraulic Control Unit Architecture
--------------------------------------

.. sys_arch:: Hydraulic Control Unit (HCU) Architecture
   :id: SYS_ARCH_004
   :status: approved
   :derives_from: SYS_REQ_007, SYS_REQ_008, SYS_REQ_009, SYS_REQ_010
   :tags: architecture; hcu; hydraulic; solenoid
   :aspice_process: SYS.3
   :safety_class: ASIL-D
   :verification_method: inspection

   The HCU contains the hydraulic components required for brake pressure modulation:

   +------------------------+----------------+--------------------------------------+
   | Component              | Quantity       | Function                             |
   +========================+================+======================================+
   | Inlet Solenoid Valve   | 4 (1/wheel)    | Isolates master cylinder pressure    |
   +------------------------+----------------+--------------------------------------+
   | Outlet Solenoid Valve  | 4 (1/wheel)    | Releases pressure to accumulator     |
   +------------------------+----------------+--------------------------------------+
   | Hydraulic Pump Motor   | 1              | Returns fluid to master cylinder     |
   +------------------------+----------------+--------------------------------------+
   | Pressure Accumulator   | 1 (shared)     | Temporary fluid storage              |
   +------------------------+----------------+--------------------------------------+

   **Electrical interface (ECU → HCU):**

   - Inlet valve control: 4 × high-side switch outputs (12V, max 3A)
   - Outlet valve control: 4 × high-side switch outputs (12V, max 3A)
   - Pump motor control: PWM output (400 Hz carrier, 0–100% duty cycle)
   - Current monitoring: dedicated ADC channels per valve for fault detection

**HCU Pressure Modulation Sequence:**

.. uml::
   :caption: HCU Pressure Modulation Phase Diagram

   @startuml HCU_Pressure_Phases
   skinparam backgroundColor #FAFAFA

   title HCU Pressure Modulation Phases - State Transitions

   [*] --> NORMAL_BRAKING : ABS inactive

   NORMAL_BRAKING --> PRESSURE_BUILD : slip > threshold\n(ABS activated)
   PRESSURE_BUILD --> PRESSURE_HOLD : slip approaching\nthreshold
   PRESSURE_HOLD --> PRESSURE_RELEASE : wheel lock\ndetected (slip > 80%)
   PRESSURE_RELEASE --> PRESSURE_BUILD : wheel recovering\n(slip < threshold)
   PRESSURE_BUILD --> NORMAL_BRAKING : ABS deactivated\n(speed < 3 km/h)

   NORMAL_BRAKING : Inlet: OPEN (de-energized)
   NORMAL_BRAKING : Outlet: CLOSED (de-energized)
   NORMAL_BRAKING : Pump: OFF

   PRESSURE_BUILD : Inlet: OPEN (de-energized)
   PRESSURE_BUILD : Outlet: CLOSED (de-energized)
   PRESSURE_BUILD : Pump: OFF

   PRESSURE_HOLD : Inlet: CLOSED (energized)
   PRESSURE_HOLD : Outlet: CLOSED (de-energized)
   PRESSURE_HOLD : Pump: OFF

   PRESSURE_RELEASE : Inlet: CLOSED (energized)
   PRESSURE_RELEASE : Outlet: OPEN (energized)
   PRESSURE_RELEASE : Pump: ON (70% PWM)
   @enduml

----

Communication System Architecture
------------------------------------

.. sys_arch:: ABS Communication System Architecture
   :id: SYS_ARCH_005
   :status: approved
   :derives_from: SYS_REQ_011, SYS_REQ_012, SYS_REQ_013
   :tags: architecture; communication; can; obd-ii
   :aspice_process: SYS.3
   :safety_class: ASIL-B
   :verification_method: inspection

   The ABS ECU communicates with the vehicle network and diagnostic tools via CAN bus:

   **CAN Messages (Transmission):**

   +------------------+--------+----------+-----------------------------------------+
   | Message Name     | CAN ID | Period   | Content                                 |
   +==================+========+==========+=========================================+
   | WheelSpeeds      | 0x3A0  | 10 ms    | FL, FR, RL, RR speeds (4×16-bit)        |
   +------------------+--------+----------+-----------------------------------------+
   | ABSStatus        | 0x3A2  | 20 ms    | Per-channel ABS active flags + faults   |
   +------------------+--------+----------+-----------------------------------------+

   **CAN Messages (Reception):**

   +------------------+--------+----------+-----------------------------------------+
   | Message Name     | CAN ID | Expected | Content                                 |
   +==================+========+==========+=========================================+
   | VehicleStatus    | 0x1A0  | 10 ms    | Ignition state, battery voltage         |
   +------------------+--------+----------+-----------------------------------------+

   **Diagnostic Interface:**

   - Protocol: UDS over ISO 15765-4 (CAN-based)
   - Addressing: Physical (0x7B0) and Functional (0x7DF)
   - Baud rate: CAN 2.0B @ 500 kbps

----

Summary
-------

.. needtable::
   :filter: type == "sys_arch"
   :columns: id, title, status, derives_from
   :style: table
   :sort: id
