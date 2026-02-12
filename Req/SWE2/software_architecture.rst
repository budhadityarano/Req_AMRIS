.. _swe2_software_architecture:

SWE.2 - Software Architecture Specification
============================================

.. contents::
   :local:
   :depth: 1

**Document:** SW-ARCH-SPEC-001
**Version:** 1.0
**Status:** Approved
**Domain:** ABS ECU Software

----

Software Overall Architecture
-------------------------------

.. sw_arch:: ABS Software Layered Architecture Overview
   :id: SW_ARCH_001
   :status: approved
   :refines: SYS_ARCH_001
   :tags: architecture; software-overview; layers; module-decomposition
   :aspice_process: SWE.2
   :safety_class: ASIL-D
   :verification_method: inspection

   The ABS ECU software is organized into four abstraction layers following AUTOSAR
   principles for automotive embedded software:

   1. **Application Layer** – ABS control logic, slip calculation, speed estimation
   2. **Service Layer** – Fault management, diagnostics, NVM, OS abstraction
   3. **Driver Layer** – WSS driver, HCU driver, CAN driver
   4. **Hardware Abstraction Layer (HAL)** – ADC, GPIO, PWM, CAN hardware interfaces

   Each layer communicates only with the layer directly above or below it.
   No direct access from Application Layer to hardware registers is permitted.

**Software Component Diagram:**

.. uml::
   :caption: ABS Software Architecture - Layered Component View

   @startuml ABS_Software_Architecture
   skinparam packageStyle rectangle
   skinparam backgroundColor #FAFAFA
   skinparam component {
     BackgroundColor #C8E6C9
     BorderColor #2E7D32
     ArrowColor #1B5E20
   }
   skinparam note {
     BackgroundColor #FFFDE7
   }

   title ABS ECU Software Architecture (SWE.2)

   package "Application Layer" as APP {
     [ABS Control\nAlgorithm] as ABS_CTRL
     [Slip Ratio\nCalculator] as SLIP_CALC
     [Vehicle Speed\nEstimator] as VSE
   }

   package "Service Layer" as SVC {
     [Fault Manager] as FAULT_MGR
     [Diagnostic Service\n(UDS/OBD-II)] as DIAG
     [NVM Manager] as NVM
     [OS / RTOS\nAbstraction] as RTOS
   }

   package "Driver Layer" as DRV {
     [WSS Driver\n(4 channels)] as WSS_DRV
     [HCU Driver\n(valves + pump)] as HCU_DRV
     [CAN Driver\n(Tx/Rx/Diag)] as CAN_DRV
   }

   package "Hardware Abstraction Layer" as HAL {
     [HAL ADC\n(sensor current)] as HAL_ADC
     [HAL GPIO\n(valve control)] as HAL_GPIO
     [HAL PWM\n(pump control)] as HAL_PWM
     [HAL CAN\n(CAN controller)] as HAL_CAN
     [HAL NVM\n(EEPROM/Flash)] as HAL_NVM
     [HAL Timer\n(capture/PWM)] as HAL_TIMER
   }

   ' Application Layer data flow
   WSS_DRV --> VSE : wheel speeds (4ch, 1ms)
   WSS_DRV --> SLIP_CALC : wheel speeds (4ch)
   VSE --> SLIP_CALC : reference speed
   SLIP_CALC --> ABS_CTRL : slip ratios (4ch)
   ABS_CTRL --> HCU_DRV : valve commands (BUILD/HOLD/RELEASE)

   ' Service Layer interfaces
   FAULT_MGR <-- WSS_DRV : sensor fault status
   FAULT_MGR <-- HCU_DRV : actuator fault status
   FAULT_MGR <-- CAN_DRV : bus error status
   FAULT_MGR --> DIAG : active DTC list
   FAULT_MGR --> NVM : store DTCs
   DIAG <--> CAN_DRV : UDS request/response
   RTOS --> ABS_CTRL : 5ms task trigger
   RTOS --> FAULT_MGR : 5ms task trigger
   RTOS --> CAN_DRV : 10ms tx task trigger

   ' Driver to HAL interfaces
   WSS_DRV --> HAL_TIMER : pulse capture (4ch)
   WSS_DRV --> HAL_ADC : sensor supply current
   HCU_DRV --> HAL_GPIO : inlet/outlet valve control
   HCU_DRV --> HAL_PWM : pump motor PWM
   HCU_DRV --> HAL_ADC : valve current monitoring
   CAN_DRV --> HAL_CAN : TX/RX CAN frames
   NVM --> HAL_NVM : read/write DTC data

   note right of ABS_CTRL
     Cycle: 5ms (200 Hz)
     4 independent state machines
     Select-low: rear axle
   end note

   note left of FAULT_MGR
     Severity: CRITICAL/MAJOR/MINOR
     Debounce: 5 cycles (25ms)
     Stores up to 20 DTCs in NVM
   end note
   @enduml

----

WSS Driver Module Architecture
--------------------------------

.. sw_arch:: WSS Driver Module Architecture
   :id: SW_ARCH_002
   :status: approved
   :refines: SYS_ARCH_003
   :tags: architecture; wss-driver; module; interface
   :aspice_process: SWE.2
   :safety_class: ASIL-D
   :verification_method: inspection

   The WSS Driver module is structured into three sub-components:

   1. **WSSCapture** – ISR-based pulse capture from 4 timer input channels (1 ms ISR)
   2. **WSSFilter** – Digital low-pass filtering (4th-order moving average, 50 Hz cutoff)
   3. **WSSFaultDetector** – Open/short circuit and plausibility monitoring

   **Module Interface (API):**

   .. code-block:: c

      /* WSS Driver Public API */
      void    WSS_Init(void);
      void    WSS_1msTask(void);          /* Called from 1ms ISR */
      float   WSS_GetWheelSpeed_kmh(WSS_Channel_t ch);
      float   WSS_GetWheelSpeed_rads(WSS_Channel_t ch);
      WSS_Status_t WSS_GetChannelStatus(WSS_Channel_t ch);
      bool    WSS_IsDataValid(WSS_Channel_t ch);

      typedef enum {
        WSS_CH_FL = 0, WSS_CH_FR = 1, WSS_CH_RL = 2, WSS_CH_RR = 3
      } WSS_Channel_t;

      typedef enum {
        WSS_OK, WSS_FAULT_OPEN, WSS_FAULT_SHORT,
        WSS_FAULT_PLAUSIBILITY, WSS_DEGRADED
      } WSS_Status_t;

----

ABS Control Module Architecture
---------------------------------

.. sw_arch:: ABS Control Module Architecture
   :id: SW_ARCH_003
   :status: approved
   :refines: SYS_ARCH_002
   :tags: architecture; abs-control; state-machine; module
   :aspice_process: SWE.2
   :safety_class: ASIL-D
   :verification_method: inspection

   The ABS Control module implements four independent per-channel state machines
   with a shared coordination layer for select-low rear axle logic.

   Sub-components:

   1. **VehicleSpeedEstimator** – Reference speed computation (max-select + deceleration model)
   2. **SlipRatioCalculator** – Per-channel slip ratio computation (λ = (v_ref - v_w) / v_ref)
   3. **ABSStateMachine** × 4 – One per wheel channel (INACTIVE → BUILD → HOLD → RELEASE)
   4. **SelectLowCoordinator** – Applies select-low logic to RL/RR channel pair

   **Module Interface (API):**

   .. code-block:: c

      /* ABS Control Module Public API */
      void      ABSCTRL_Init(void);
      void      ABSCTRL_5msTask(void);    /* Main 5ms control cycle */
      HCU_Cmd_t ABSCTRL_GetChannelCmd(ABS_Channel_t ch);
      bool      ABSCTRL_IsActive(void);
      float     ABSCTRL_GetSlipRatio(ABS_Channel_t ch);
      float     ABSCTRL_GetRefSpeed_kmh(void);

      typedef enum {
        ABS_INACTIVE, ABS_PRESSURE_BUILD, ABS_PRESSURE_HOLD, ABS_PRESSURE_RELEASE
      } ABS_State_t;

      typedef enum {
        HCU_CMD_NORMAL, HCU_CMD_BUILD, HCU_CMD_HOLD, HCU_CMD_RELEASE
      } HCU_Cmd_t;

----

Fault Management Module Architecture
--------------------------------------

.. sw_arch:: Fault Management Module Architecture
   :id: SW_ARCH_004
   :status: approved
   :refines: SYS_ARCH_002
   :tags: architecture; fault-manager; dtc; safe-state
   :aspice_process: SWE.2
   :safety_class: ASIL-D
   :verification_method: inspection

   The Fault Management module handles all runtime fault detection, qualification,
   DTC storage, and safe state coordination.

   Sub-components:

   1. **FaultCollector** – Aggregates fault flags from all modules at 5 ms rate
   2. **FaultQualifier** – Applies debounce (5 cycles) and severity classification
   3. **DTCManager** – Manages DTC write/read from NVM via NVM Manager API
   4. **SafeStateController** – Executes safe state transitions on CRITICAL faults
   5. **WarningLampController** – Controls ABS warning lamp GPIO based on fault severity

   **Fault Catalog (excerpt):**

   +-------------------+------------------+-------------+----------------------------------+
   | DTC Code          | Fault ID         | Severity    | Description                      |
   +===================+==================+=============+==================================+
   | 0xC0035           | WSS_FL_OPEN      | CRITICAL    | WSS FL open circuit              |
   +-------------------+------------------+-------------+----------------------------------+
   | 0xC0040           | WSS_FR_OPEN      | CRITICAL    | WSS FR open circuit              |
   +-------------------+------------------+-------------+----------------------------------+
   | 0xC0045           | WSS_RL_OPEN      | CRITICAL    | WSS RL open circuit              |
   +-------------------+------------------+-------------+----------------------------------+
   | 0xC0050           | WSS_RR_OPEN      | CRITICAL    | WSS RR open circuit              |
   +-------------------+------------------+-------------+----------------------------------+
   | 0xC1010           | HCU_VALVE_SHORT  | CRITICAL    | Solenoid over-current            |
   +-------------------+------------------+-------------+----------------------------------+
   | 0xC1020           | HCU_PUMP_STALL   | MAJOR       | Pump motor stall detected        |
   +-------------------+------------------+-------------+----------------------------------+
   | 0xU0100           | CAN_BUS_OFF      | MAJOR       | CAN bus-off condition            |
   +-------------------+------------------+-------------+----------------------------------+
   | 0xU0101           | CAN_RX_TIMEOUT   | MINOR       | CAN Rx message timeout           |
   +-------------------+------------------+-------------+----------------------------------+

----

Communication Module Architecture
------------------------------------

.. sw_arch:: CAN Communication Module Architecture
   :id: SW_ARCH_005
   :status: approved
   :refines: SYS_ARCH_005
   :tags: architecture; can-driver; communication; uds
   :aspice_process: SWE.2
   :safety_class: ASIL-B
   :verification_method: inspection

   The CAN Communication module handles all vehicle network communication:

   Sub-components:

   1. **CANTxScheduler** – Periodic transmission of WheelSpeeds (10 ms) and ABSStatus (20 ms)
   2. **CANRxDispatcher** – Reception and routing of incoming CAN messages
   3. **CANErrorMonitor** – CAN controller error counter monitoring and bus-off recovery
   4. **UDSHandler** – Handles UDS service requests (0x22, 0x19, 0x14, 0x27)
   5. **ISO15765Transport** – ISO 15765-4 multi-frame transport layer (for UDS segmentation)

   **CAN Message Database Summary:**

   .. uml::
      :caption: CAN Communication Message Flow

      @startuml CAN_Messages
      skinparam backgroundColor #FAFAFA

      title ABS ECU CAN Communication

      participant "Vehicle Network\n(Other ECUs)" as NET
      participant "ABS ECU\nCAN Driver" as ABS

      loop Every 10ms
        ABS -> NET : WheelSpeeds [0x3A0] (8 bytes)\nFL|FR|RL|RR speeds
      end

      loop Every 20ms
        ABS -> NET : ABSStatus [0x3A2] (4 bytes)\nABS flags + fault flags
      end

      NET -> ABS : VehicleStatus [0x1A0] (4 bytes)\nIgnition + battery voltage

      == Diagnostic Session ==

      NET -> ABS : UDS Request [0x7B0]\nReadDTCs / ClearDTCs / ReadData
      ABS -> NET : UDS Response [0x7B8]\nDTC data / live data
      @enduml

----

Summary
-------

.. needtable::
   :filter: type == "sw_arch"
   :columns: id, title, status, refines
   :style: table
   :sort: id
