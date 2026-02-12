.. _swe3_software_detailed_design:

SWE.3 - Software Detailed Design Specification
================================================

.. contents::
   :local:
   :depth: 1

**Document:** SW-DESIGN-SPEC-001
**Version:** 1.0
**Status:** Approved
**Domain:** ABS ECU Software

----

WSS Driver Detailed Design
---------------------------

.. sw_design:: WSS Driver Module - Data Structures and Algorithm Design
   :id: SW_DESIGN_001
   :status: approved
   :refines: SW_ARCH_002
   :traces_to: SW_REQ_001, SW_REQ_002, SW_REQ_003
   :tags: design; wss-driver; data-structures; algorithm
   :aspice_process: SWE.3
   :safety_class: ASIL-D
   :verification_method: inspection

   **Data Structures:**

   .. code-block:: c

      /* WSS Driver - Internal Data Structures */

      /* Per-channel raw capture data (ISR context) */
      typedef struct {
        volatile uint32_t pulseCount;       /* Hardware timer capture counter */
        volatile uint32_t lastCapture_us;   /* Last valid pulse timestamp */
        volatile uint32_t currentCapture_us;/* Current pulse timestamp */
        volatile uint16_t supplyCurrentADC; /* ADC raw value (12-bit) for fault detect */
      } WSS_RawData_t;

      /* Per-channel processed output (task context) */
      typedef struct {
        float   speed_kmh;         /* Filtered wheel speed [km/h] */
        float   speed_rads;        /* Angular velocity [rad/s] */
        float   filterBuffer[4];   /* MA filter history buffer (4th order) */
        uint8_t filterIdx;         /* Circular buffer index */
        WSS_Status_t  status;      /* Channel health status */
        bool    dataValid;         /* Data validity flag */
        uint8_t openFaultCounter;  /* Consecutive cycles without pulse */
        uint8_t shortFaultCounter; /* Consecutive cycles with over-current */
      } WSS_ChannelData_t;

      /* Module-level data */
      typedef struct {
        WSS_RawData_t    raw[4];         /* Raw ISR data */
        WSS_ChannelData_t channel[4];    /* Processed channel data */
        bool             initDone;        /* Module initialized flag */
        uint32_t         cycleCount;      /* Total ISR execution count */
      } WSS_DriverData_t;

   **Angular Velocity Calculation Algorithm:**

   .. code-block:: c

      /* Called every 1ms from ISR */
      void WSS_1msTask(void) {
        for (int ch = 0; ch < 4; ch++) {
          uint32_t delta_pulses = WSS_raw[ch].pulseCount - WSS_raw[ch].prevCount;
          float    omega_rads   = (delta_pulses * 2.0f * M_PI) / (WSS_N_TEETH * WSS_DT_S);
          float    speed_kmh    = omega_rads * WSS_WHEEL_RADIUS_M * 3.6f;

          /* Apply 4th-order moving average filter */
          WSS_channel[ch].filterBuffer[WSS_channel[ch].filterIdx] = speed_kmh;
          WSS_channel[ch].filterIdx = (WSS_channel[ch].filterIdx + 1) % 4;
          float sum = 0.0f;
          for (int i = 0; i < 4; i++) sum += WSS_channel[ch].filterBuffer[i];
          WSS_channel[ch].speed_kmh = sum / 4.0f;

          WSS_DetectFaults(ch);
        }
      }

   **Configuration Parameters:**

   +---------------------+----------+----------+---------------------------------+
   | Parameter           | Value    | Unit     | Description                     |
   +=====================+==========+==========+=================================+
   | WSS_N_TEETH         | 48       | –        | Encoder wheel tooth count       |
   +---------------------+----------+----------+---------------------------------+
   | WSS_DT_S            | 0.001    | s        | ISR period                      |
   +---------------------+----------+----------+---------------------------------+
   | WSS_WHEEL_RADIUS_M  | 0.317    | m        | Nominal wheel rolling radius    |
   +---------------------+----------+----------+---------------------------------+
   | WSS_OPEN_THRESH_MS  | 50       | ms       | Open circuit detection timeout  |
   +---------------------+----------+----------+---------------------------------+
   | WSS_SHORT_CURR_MA   | 500      | mA       | Short circuit current threshold |
   +---------------------+----------+----------+---------------------------------+

----

Slip Ratio Calculator Detailed Design
--------------------------------------

.. sw_design:: Slip Ratio Calculator - Algorithm and Interface Design
   :id: SW_DESIGN_002
   :status: approved
   :refines: SW_ARCH_003
   :traces_to: SW_REQ_014, SW_REQ_015, SW_REQ_017, SW_REQ_018
   :tags: design; slip-ratio; algorithm; divide-by-zero
   :aspice_process: SWE.3
   :safety_class: ASIL-D
   :verification_method: inspection

   **Data Structures:**

   .. code-block:: c

      /* Slip Ratio Calculator - Data Structures */

      typedef struct {
        float slipRatio;           /* λ in range [0.0, 1.0] */
        bool  wheelLocked;         /* True if λ > LOCK_THRESHOLD for N cycles */
        bool  dataValid;           /* False if WSS data invalid */
        uint8_t lockCounter;       /* Consecutive cycles with λ > LOCK_THRESHOLD */
      } SlipData_t;

      typedef struct {
        float refSpeed_kmh;        /* Vehicle reference speed estimate */
        bool  refSpeedValid;       /* False if < 2 valid WSS channels */
        float prevRefSpeed_kmh;    /* Previous cycle value for rate limiting */
      } VehicleRefSpeed_t;

   **Slip Ratio Algorithm:**

   .. code-block:: c

      #define EPSILON_KMH     1.0f    /* Minimum denominator to avoid div/0 */
      #define LOCK_THRESHOLD  0.80f   /* 80% slip = locked wheel */
      #define LOCK_CYCLES     5u      /* Debounce for lock detection */

      void SlipCalc_Update(void) {
        /* Step 1: Compute vehicle reference speed */
        float v_ref = 0.0f;
        uint8_t validCount = 0;
        for (int ch = 0; ch < 4; ch++) {
          if (WSS_IsDataValid((WSS_Channel_t)ch)) {
            v_ref = fmaxf(v_ref, WSS_GetWheelSpeed_kmh((WSS_Channel_t)ch));
            validCount++;
          }
        }
        g_refSpeed.refSpeedValid = (validCount >= 2);

        /* Step 2: Rate-limit reference speed (max 5 km/h per 10ms cycle) */
        float delta = v_ref - g_refSpeed.prevRefSpeed_kmh;
        if (fabsf(delta) > MAX_REF_SPEED_CHANGE_KMH)
          v_ref = g_refSpeed.prevRefSpeed_kmh + copysignf(MAX_REF_SPEED_CHANGE_KMH, delta);
        g_refSpeed.refSpeed_kmh = v_ref;
        g_refSpeed.prevRefSpeed_kmh = v_ref;

        /* Step 3: Compute per-channel slip ratio */
        float v_denom = fmaxf(v_ref, EPSILON_KMH);
        for (int ch = 0; ch < 4; ch++) {
          float v_wheel = WSS_GetWheelSpeed_kmh((WSS_Channel_t)ch);
          g_slipData[ch].slipRatio = (v_ref - v_wheel) / v_denom;
          g_slipData[ch].slipRatio = CLAMP(g_slipData[ch].slipRatio, 0.0f, 1.0f);

          /* Step 4: Wheel lock detection with debounce */
          if (g_slipData[ch].slipRatio > LOCK_THRESHOLD)
            g_slipData[ch].lockCounter = MIN(g_slipData[ch].lockCounter + 1, LOCK_CYCLES);
          else
            g_slipData[ch].lockCounter = 0;
          g_slipData[ch].wheelLocked = (g_slipData[ch].lockCounter >= LOCK_CYCLES);
        }
      }

----

ABS Control State Machine Detailed Design
-------------------------------------------

.. sw_design:: ABS Control Algorithm - State Machine Design
   :id: SW_DESIGN_003
   :status: approved
   :refines: SW_ARCH_003
   :traces_to: SW_REQ_019, SW_REQ_020, SW_REQ_021, SW_REQ_022, SW_REQ_026, SW_REQ_027
   :tags: design; abs-control; state-machine; per-channel
   :aspice_process: SWE.3
   :safety_class: ASIL-D
   :verification_method: inspection

   **ABS Channel State Machine:**

   Each of the four wheel channels has an independent state machine:

   .. uml::
      :caption: ABS Channel State Machine (per wheel)

      @startuml ABS_State_Machine
      skinparam backgroundColor #FAFAFA

      title ABS Control State Machine (Per Channel)

      [*] --> INACTIVE : system init

      INACTIVE --> PRESSURE_HOLD : slip > UPPER_THRESH\nAND speed > 5 km/h

      PRESSURE_HOLD --> PRESSURE_BUILD : slip < LOWER_THRESH\nAND NOT locked
      PRESSURE_HOLD --> PRESSURE_RELEASE : wheelLocked == true

      PRESSURE_BUILD --> PRESSURE_HOLD : slip > UPPER_THRESH
      PRESSURE_BUILD --> INACTIVE : ABS_DISABLE flag\nOR speed < 3 km/h

      PRESSURE_RELEASE --> PRESSURE_BUILD : NOT wheelLocked\nOR release_timer > 50ms
      PRESSURE_RELEASE --> INACTIVE : ABS_DISABLE flag

      INACTIVE --> INACTIVE : speed < 3 km/h

      INACTIVE : inlet_valve = OPEN (de-energized)
      INACTIVE : outlet_valve = CLOSED (de-energized)
      INACTIVE : pump = OFF

      PRESSURE_BUILD : inlet_valve = OPEN (de-energized)
      PRESSURE_BUILD : outlet_valve = CLOSED (de-energized)
      PRESSURE_BUILD : pump = OFF

      PRESSURE_HOLD : inlet_valve = CLOSED (energized)
      PRESSURE_HOLD : outlet_valve = CLOSED (de-energized)
      PRESSURE_HOLD : pump = OFF

      PRESSURE_RELEASE : inlet_valve = CLOSED (energized)
      PRESSURE_RELEASE : outlet_valve = OPEN (energized)
      PRESSURE_RELEASE : pump = ON (70% PWM)
      @enduml

   **State Machine Data Structures:**

   .. code-block:: c

      typedef struct {
        ABS_State_t  state;            /* Current state */
        ABS_State_t  prevState;        /* Previous state (for edge detection) */
        uint32_t     releaseTimer_ms;  /* PRESSURE_RELEASE duration counter */
        HCU_Cmd_t    outputCmd;        /* Current actuator command */
      } ABS_Channel_t;

      /* Select-low coordinator for rear axle */
      typedef struct {
        float  rl_slip;  /* Rear-left slip ratio */
        float  rr_slip;  /* Rear-right slip ratio */
        uint8_t governingChannel; /* RL=2, RR=3 (lower speed channel) */
      } SelectLow_t;

   **Calibration Parameters:**

   +-------------------------+------------+----------+-----------------------------------+
   | Parameter               | Default    | Unit     | Description                       |
   +=========================+============+==========+===================================+
   | ABS_UPPER_THRESH        | 0.25       | –        | ABS activation slip threshold     |
   +-------------------------+------------+----------+-----------------------------------+
   | ABS_LOWER_THRESH        | 0.10       | –        | Pressure build slip threshold     |
   +-------------------------+------------+----------+-----------------------------------+
   | ABS_DEACT_SPEED_KMH     | 3.0        | km/h     | Deactivation vehicle speed        |
   +-------------------------+------------+----------+-----------------------------------+
   | ABS_ACT_SPEED_KMH       | 5.0        | km/h     | Activation minimum vehicle speed  |
   +-------------------------+------------+----------+-----------------------------------+
   | ABS_MAX_RELEASE_MS      | 50         | ms       | Max PRESSURE_RELEASE duration     |
   +-------------------------+------------+----------+-----------------------------------+

----

HCU Driver Detailed Design
----------------------------

.. sw_design:: HCU Driver - Solenoid Valve and PWM Control Design
   :id: SW_DESIGN_004
   :status: approved
   :refines: SW_ARCH_001
   :traces_to: SW_REQ_028, SW_REQ_029, SW_REQ_030, SW_REQ_031, SW_REQ_032
   :tags: design; hcu-driver; solenoid; pwm; data-structures
   :aspice_process: SWE.3
   :safety_class: ASIL-D
   :verification_method: inspection

   **Data Structures:**

   .. code-block:: c

      /* HCU Driver - Data Structures */

      /* Per-valve state tracking */
      typedef struct {
        bool      commanded;       /* Desired valve state from ABS controller */
        bool      actual;          /* Current output state (after debounce) */
        bool      faultOpen;       /* Open circuit fault flag */
        bool      faultShort;      /* Over-current fault flag */
        uint16_t  currentADC;      /* ADC value of valve current sense */
        uint8_t   debounceCounter; /* Min-duration counter in 1ms units */
      } HCU_ValveState_t;

      /* Module-level HCU data */
      typedef struct {
        HCU_ValveState_t inletValve[4];   /* Inlet valves: FL, FR, RL, RR */
        HCU_ValveState_t outletValve[4];  /* Outlet valves: FL, FR, RL, RR */
        bool             pumpActive;       /* Pump motor commanded state */
        uint8_t          pumpPWM_pct;     /* Pump PWM duty cycle (0-100%) */
        uint32_t         pumpCurrentADC;  /* ADC value for pump current */
        bool             faultPumpStall;  /* Pump stall detected flag */
        bool             initPassed;      /* Startup self-test result */
      } HCU_DriverData_t;

   **Valve Control Algorithm (with debounce):**

   .. code-block:: c

      /* Called every 1ms from main task */
      void HCU_SetValveCommand(uint8_t valveIdx, bool commanded, bool isInlet) {
        HCU_ValveState_t *v = isInlet ? &hcu.inletValve[valveIdx]
                                       : &hcu.outletValve[valveIdx];
        if (commanded != v->actual) {
          if (v->debounceCounter == 0) {
            v->debounceCounter = HCU_MIN_VALVE_DWELL_MS; /* 1ms minimum */
          }
        }
        if (v->debounceCounter > 0) {
          v->debounceCounter--;
          if (v->debounceCounter == 0) {
            v->actual = commanded;
            HAL_GPIO_Write(HCU_GetValvePin(valveIdx, isInlet), commanded);
          }
        }
      }

   **GPIO Pin Assignment:**

   +--------------------+----------+----------+------------------------------+
   | Signal             | GPIO Pin | Active   | Description                  |
   +====================+==========+==========+==============================+
   | Inlet Valve FL     | PA4      | High     | 12V high-side switch         |
   +--------------------+----------+----------+------------------------------+
   | Inlet Valve FR     | PA5      | High     | 12V high-side switch         |
   +--------------------+----------+----------+------------------------------+
   | Inlet Valve RL     | PA6      | High     | 12V high-side switch         |
   +--------------------+----------+----------+------------------------------+
   | Inlet Valve RR     | PA7      | High     | 12V high-side switch         |
   +--------------------+----------+----------+------------------------------+
   | Outlet Valve FL    | PB0      | High     | 12V high-side switch         |
   +--------------------+----------+----------+------------------------------+
   | Outlet Valve FR    | PB1      | High     | 12V high-side switch         |
   +--------------------+----------+----------+------------------------------+
   | Outlet Valve RL    | PB2      | High     | 12V high-side switch         |
   +--------------------+----------+----------+------------------------------+
   | Outlet Valve RR    | PB3      | High     | 12V high-side switch         |
   +--------------------+----------+----------+------------------------------+
   | Pump Motor PWM     | PC6      | PWM TIM8 | 400 Hz, 0–100% duty cycle    |
   +--------------------+----------+----------+------------------------------+

----

Fault Manager Detailed Design
-------------------------------

.. sw_design:: Fault Manager - DTC Storage and Safe State Design
   :id: SW_DESIGN_005
   :status: approved
   :refines: SW_ARCH_004
   :traces_to: SW_REQ_042, SW_REQ_043, SW_REQ_044, SW_REQ_045, SW_REQ_047
   :tags: design; fault-manager; dtc; nvm; safe-state
   :aspice_process: SWE.3
   :safety_class: ASIL-D
   :verification_method: inspection

   **NVM DTC Storage Layout:**

   .. code-block:: c

      /* DTC Entry - 12 bytes per entry, 20 slots = 240 bytes NVM */
      typedef struct {
        uint32_t dtcCode;              /* 3-byte DTC + 1 byte severity */
        uint32_t firstOccurrence_ms;   /* System uptime at first occurrence */
        uint32_t lastOccurrence_ms;    /* System uptime at most recent occurrence */
        uint8_t  occurrenceCount;      /* Number of occurrences (max 255) */
        uint8_t  statusByte;           /* bit0=testFailed, bit1=confirmedDTC, */
                                       /* bit2=pendingDTC, bit3=warningIndicator */
        uint8_t  reserved[2];          /* Padding for alignment */
      } DTC_Entry_t;                   /* Total: 12 bytes per DTC */

      #define DTC_MAX_ENTRIES      20
      #define DTC_NVM_BASE_ADDR    0x0800  /* NVM byte address */

      typedef struct {
        DTC_Entry_t entries[DTC_MAX_ENTRIES];
        uint16_t    crc16;             /* CRC16 of entire DTC block */
        uint8_t     activeCount;       /* Number of active DTCs */
        uint8_t     storedCount;       /* Number of stored DTCs */
      } DTC_Store_t;

   **Safe State Transition Sequence:**

   .. code-block:: c

      /* CRITICAL fault handler - must complete in < 1ms */
      void FaultMgr_TriggerSafeState(uint32_t faultCode) {
        /* Step 1: Disable ABS controller output */
        ABSCTRL_SetDisableFlag(true);

        /* Step 2: Force all HCU valves to default (safe) state */
        for (int ch = 0; ch < 4; ch++) {
          HAL_GPIO_Write(HCU_INLET_PIN[ch],  GPIO_LOW);  /* Inlet OPEN */
          HAL_GPIO_Write(HCU_OUTLET_PIN[ch], GPIO_LOW);  /* Outlet CLOSED */
        }
        HAL_PWM_SetDutyCycle(HCU_PUMP_PWM_CH, 0);        /* Pump OFF */

        /* Step 3: Turn on ABS warning lamp */
        HAL_GPIO_Write(ABS_LAMP_PIN, GPIO_HIGH);

        /* Step 4: Store DTC */
        FaultMgr_StoreDTC(faultCode, SEVERITY_CRITICAL);

        /* Step 5: Inhibit ABS re-activation (flag in NVM, survives reset) */
        NVM_Write(NVM_ABS_INHIBIT_ADDR, 1u);
      }

   **Fault Debounce Logic:**

   .. code-block:: c

      #define FAULT_DEBOUNCE_CYCLES  5u    /* 5 × 5ms = 25ms to activate */

      void FaultMgr_Update(void) {
        for (int faultId = 0; faultId < FAULT_COUNT; faultId++) {
          if (FaultMgr_IsRawFaultActive(faultId)) {
            if (++g_faultDb[faultId].debounceCounter >= FAULT_DEBOUNCE_CYCLES) {
              if (!g_faultDb[faultId].active) {
                g_faultDb[faultId].active = true;
                FaultMgr_OnFaultActivated(faultId);  /* DTC store, safe state, lamp */
              }
            }
          } else {
            g_faultDb[faultId].debounceCounter = 0;
            /* Note: deactivation requires separate healing debounce */
          }
        }
      }

----

Summary
-------

.. needtable::
   :filter: type == "sw_design"
   :columns: id, title, status, refines, traces_to
   :style: table
   :sort: id
