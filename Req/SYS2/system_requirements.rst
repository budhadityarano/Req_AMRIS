.. _sys2_system_requirements:

SYS.2 - System Requirements Specification
==========================================

.. contents::
   :local:
   :depth: 1

**Document:** SYS-REQ-SPEC-001
**Version:** 1.0
**Status:** Approved
**Domain:** Anti-Lock Braking System (ABS)

----

Wheel Speed Sensing Requirements
---------------------------------

.. sys_req:: System shall monitor wheel speed at all four wheels
   :id: SYS_REQ_001
   :status: approved
   :satisfies: STKH_REQ_002
   :tags: sensing; wheel-speed; sampling
   :aspice_process: SYS.2
   :safety_class: ASIL-D
   :verification_method: test
   :priority: high

   The ABS system shall independently monitor the rotational speed of all four wheels.
   Wheel speed sensors shall provide a sampling rate of at least **1000 Hz** (1 ms period)
   per channel. Minimum measurable speed: 1 km/h. Maximum measurable speed: 250 km/h.

   **Derived from:** STKH_REQ_002 (wheel lockup prevention requires continuous speed monitoring)

.. sys_req:: System shall detect wheel lock condition within 10 ms
   :id: SYS_REQ_002
   :status: approved
   :satisfies: STKH_REQ_002, STKH_REQ_004
   :tags: sensing; wheel-lock; detection; timing
   :aspice_process: SYS.2
   :safety_class: ASIL-D
   :verification_method: test
   :priority: high

   The system shall detect a wheel lock condition (wheel slip > 80%) within **10 ms**
   of the lock event onset. Detection latency is measured from the physical wheel deceleration
   exceeding the lock threshold to the ECU registering the fault condition.

   **Derived from:** STKH_REQ_002, STKH_REQ_004 (intervention transparency requires fast detection)

----

Processing & Control Requirements
-----------------------------------

.. sys_req:: ECU shall complete ABS control cycle within 5 ms
   :id: SYS_REQ_003
   :status: approved
   :satisfies: STKH_REQ_004
   :tags: processing; cycle-time; real-time
   :aspice_process: SYS.2
   :safety_class: ASIL-D
   :verification_method: test
   :priority: high

   The ABS ECU shall complete one full control cycle — including sensor data acquisition,
   slip ratio computation, control decision, and actuator command output — within **5 ms**
   (200 Hz cycle rate). Worst-case execution time shall not exceed 4 ms, leaving 1 ms margin.

   **Derived from:** STKH_REQ_004 (transparent intervention requires fast control loop)

.. sys_req:: System shall calculate wheel slip ratio for each wheel independently
   :id: SYS_REQ_004
   :status: approved
   :satisfies: STKH_REQ_001, STKH_REQ_002
   :tags: algorithm; slip-ratio; calculation
   :aspice_process: SYS.2
   :safety_class: ASIL-D
   :verification_method: test
   :priority: high

   The system shall compute the individual slip ratio λ for each of the four wheels using:

   .. math::

      \lambda = \frac{v_{ref} - v_{wheel}}{v_{ref}}

   where ``v_ref`` is the estimated vehicle reference speed. Slip ratio range: 0.0 (free rolling)
   to 1.0 (locked wheel). Resolution: 0.01 (1%).

   **Derived from:** STKH_REQ_001, STKH_REQ_002

.. sys_req:: System shall compute vehicle reference speed from wheel speed data
   :id: SYS_REQ_005
   :status: approved
   :satisfies: STKH_REQ_001
   :tags: algorithm; reference-speed; vehicle-speed
   :aspice_process: SYS.2
   :safety_class: ASIL-D
   :verification_method: test
   :priority: high

   The system shall estimate the true vehicle speed (reference speed) from the four
   wheel speed inputs. During non-ABS braking, reference speed = maximum of four wheel speeds.
   During ABS intervention, reference speed is maintained using a deceleration model
   (max deceleration: 1.2g = 11.77 m/s²).

   **Derived from:** STKH_REQ_001 (steerability requires accurate speed estimation)

.. sys_req:: System shall adapt slip threshold based on detected road surface
   :id: SYS_REQ_006
   :status: approved
   :satisfies: STKH_REQ_005
   :tags: algorithm; adaptive-control; road-surface
   :aspice_process: SYS.2
   :safety_class: ASIL-C
   :verification_method: test
   :priority: medium

   The system shall estimate the road surface friction coefficient (µ) and adapt the
   ABS slip threshold accordingly:

   - High µ (> 0.6): ABS activation threshold = 20-25% slip
   - Medium µ (0.3–0.6): ABS activation threshold = 15-20% slip
   - Low µ (< 0.3): ABS activation threshold = 10-15% slip

   **Derived from:** STKH_REQ_005 (multi-surface operation requires adaptive thresholds)

----

Hydraulic Actuation Requirements
----------------------------------

.. sys_req:: Hydraulic Control Unit shall modulate brake pressure in three phases
   :id: SYS_REQ_007
   :status: approved
   :satisfies: STKH_REQ_001, STKH_REQ_002
   :tags: actuation; hcu; pressure-modulation; phases
   :aspice_process: SYS.2
   :safety_class: ASIL-D
   :verification_method: test
   :priority: high

   The Hydraulic Control Unit (HCU) shall implement three-phase brake pressure modulation:

   1. **BUILD phase:** Inlet valve OPEN, outlet valve CLOSED — pressure increases
   2. **HOLD phase:** Inlet valve CLOSED, outlet valve CLOSED — pressure constant
   3. **RELEASE phase:** Inlet valve CLOSED, outlet valve OPEN, pump active — pressure decreases

   **Derived from:** STKH_REQ_001, STKH_REQ_002

.. sys_req:: HCU solenoid valves shall respond within 2 ms of ECU command
   :id: SYS_REQ_008
   :status: approved
   :satisfies: STKH_REQ_004
   :tags: actuation; solenoid; response-time; hcu
   :aspice_process: SYS.2
   :safety_class: ASIL-D
   :verification_method: test
   :priority: high

   The HCU inlet and outlet solenoid valves shall transition from de-energized to
   energized state (or vice versa) within **2 ms** of receiving the ECU control signal.
   This includes ECU output driver switching time + electromagnetic actuation delay.

   **Derived from:** STKH_REQ_004

.. sys_req:: ABS pressure modulation cycle shall operate at 5 to 20 Hz
   :id: SYS_REQ_009
   :status: approved
   :satisfies: STKH_REQ_003
   :tags: actuation; pressure-cycle; frequency
   :aspice_process: SYS.2
   :safety_class: ASIL-C
   :verification_method: test
   :priority: medium

   The ABS pressure modulation cycle (build → hold → release → build) shall operate
   at a frequency between **5 Hz and 20 Hz** depending on road surface conditions.
   Lower frequency on low-µ surfaces; higher frequency on high-µ surfaces.

   **Derived from:** STKH_REQ_003 (optimal braking distance requires proper cycle frequency)

.. sys_req:: System shall control each wheel channel independently
   :id: SYS_REQ_010
   :status: approved
   :satisfies: STKH_REQ_001, STKH_REQ_002
   :tags: actuation; independent-control; four-channel
   :aspice_process: SYS.2
   :safety_class: ASIL-D
   :verification_method: test
   :priority: high

   The ABS system shall independently control brake pressure on all four wheel
   channels. Individual wheel lockup shall be resolved without affecting other
   non-locked wheels. Exception: rear axle uses select-low logic (channel with
   lower wheel speed governs both rear wheels).

   **Derived from:** STKH_REQ_001, STKH_REQ_002

----

Communication Requirements
----------------------------

.. sys_req:: System shall transmit wheel speed data on vehicle CAN bus
   :id: SYS_REQ_011
   :status: approved
   :satisfies: STKH_REQ_010
   :tags: communication; can; wheel-speed; data-output
   :aspice_process: SYS.2
   :safety_class: ASIL-B
   :verification_method: test
   :priority: medium

   The ABS ECU shall transmit individual wheel speed values for all four wheels on the
   vehicle CAN bus at a **10 ms (100 Hz) cycle rate**. CAN message ID: 0x3A0.
   Data format: unsigned 16-bit, resolution 0.01 km/h, range 0–327 km/h.

   **Derived from:** STKH_REQ_010 (serviceability requires data availability on bus)

.. sys_req:: System shall support OBD-II diagnostic communication
   :id: SYS_REQ_012
   :status: approved
   :satisfies: STKH_REQ_010
   :tags: communication; obd-ii; uds; diagnostics
   :aspice_process: SYS.2
   :safety_class: QM
   :verification_method: test
   :priority: medium

   The ABS ECU shall implement OBD-II compatible diagnostics via the ISO 15765-4
   (CAN-based) transport layer. Supported UDS services:

   - 0x22 (Read Data by Identifier)
   - 0x19 (Read DTC Information)
   - 0x14 (Clear Diagnostic Information)
   - 0x27 (Security Access) for calibration

   **Derived from:** STKH_REQ_010

.. sys_req:: System shall transmit ABS active status on CAN bus
   :id: SYS_REQ_013
   :status: approved
   :satisfies: STKH_REQ_008
   :tags: communication; can; abs-status
   :aspice_process: SYS.2
   :safety_class: ASIL-B
   :verification_method: test
   :priority: medium

   The ABS ECU shall broadcast the ABS activation status (active/inactive per channel)
   on the vehicle CAN bus at a **20 ms cycle rate**. CAN message ID: 0x3A2.
   This signal shall be used by the instrument cluster for warning lamp control.

   **Derived from:** STKH_REQ_008 (driver warning requires status broadcast)

----

Power Supply & Environmental Requirements
------------------------------------------

.. sys_req:: System shall operate within supply voltage range 9 V to 16 V
   :id: SYS_REQ_014
   :status: approved
   :satisfies: STKH_REQ_007
   :tags: power; voltage; environment
   :aspice_process: SYS.2
   :safety_class: ASIL-B
   :verification_method: test
   :priority: medium

   The ABS ECU shall operate correctly within a supply voltage range of **9 V to 16 V DC**.
   Below 9 V: system shall enter low-voltage fault mode and disable ABS.
   Above 16 V: system shall enter over-voltage fault mode.
   Nominal voltage: 12 V (battery) to 14.4 V (alternator charging).

   **Derived from:** STKH_REQ_007 (reliability requires operation across battery states)

.. sys_req:: System shall operate within ambient temperature range -40°C to +105°C
   :id: SYS_REQ_015
   :status: approved
   :satisfies: STKH_REQ_007
   :tags: environment; temperature; operating-range
   :aspice_process: SYS.2
   :safety_class: ASIL-B
   :verification_method: test
   :priority: medium

   The ABS ECU, including all active components, shall operate correctly within an
   ambient temperature range of **-40°C to +105°C**. Storage temperature: -40°C to +125°C.
   Temperature monitoring shall trigger warnings if ECU temperature exceeds 110°C.

   **Derived from:** STKH_REQ_007

.. sys_req:: System shall comply with EMC requirements per ISO 11452 and CISPR 25
   :id: SYS_REQ_016
   :status: approved
   :satisfies: STKH_REQ_006
   :tags: emc; electromagnetic; compliance; cispr
   :aspice_process: SYS.2
   :safety_class: ASIL-B
   :verification_method: test
   :priority: medium

   The ABS system shall comply with electromagnetic compatibility requirements:

   - Radiated emissions: CISPR 25, Class 3 limits
   - Conducted emissions: ISO 7637-2
   - RF immunity: ISO 11452-2 (antenna port), ISO 11452-4 (bulk current injection)
   - ESD immunity: IEC 61000-4-2, Level 4

   **Derived from:** STKH_REQ_006

----

Safety & Diagnostic Requirements
----------------------------------

.. sys_req:: System shall detect wheel speed sensor faults within 100 ms
   :id: SYS_REQ_017
   :status: approved
   :satisfies: STKH_REQ_008, STKH_REQ_009
   :tags: diagnostics; fault-detection; wss; safety
   :aspice_process: SYS.2
   :safety_class: ASIL-D
   :verification_method: test
   :priority: high

   The system shall detect the following wheel speed sensor fault conditions within
   **100 ms** of fault onset:

   - Open circuit: no signal for > 50 ms while vehicle moving
   - Short circuit to ground or supply: signal out of valid range
   - Plausibility error: wheel speed deviates > 50% from adjacent wheel

   **Derived from:** STKH_REQ_008, STKH_REQ_009

.. sys_req:: System shall enter fail-safe mode on critical fault detection
   :id: SYS_REQ_018
   :status: approved
   :satisfies: STKH_REQ_009
   :tags: safety; fail-safe; fault-handling
   :aspice_process: SYS.2
   :safety_class: ASIL-D
   :verification_method: test
   :priority: high

   Upon detection of a CRITICAL fault (e.g., ECU internal fault, all wheel speed sensors
   failed, HCU valve driver fault), the system shall:

   1. Immediately disable ABS actuation
   2. De-energize all HCU solenoid valves (default = non-ABS braking mode)
   3. Illuminate the ABS warning lamp
   4. Log a DTC to NVM
   5. Maintain normal braking function unaffected

   **Derived from:** STKH_REQ_009

.. sys_req:: System shall store Diagnostic Trouble Codes in non-volatile memory
   :id: SYS_REQ_019
   :status: approved
   :satisfies: STKH_REQ_010
   :tags: diagnostics; dtc; nvm; obd-ii
   :aspice_process: SYS.2
   :safety_class: QM
   :verification_method: test
   :priority: medium

   The ABS ECU shall store Diagnostic Trouble Codes (DTCs) in non-volatile memory (NVM/EEPROM).
   DTC storage shall include: fault code, occurrence counter, first-occurrence timestamp,
   last-occurrence timestamp, and fault status byte (active/stored/pending).
   Minimum capacity: **20 DTC entries**. DTCs shall persist through power cycles.

   **Derived from:** STKH_REQ_010

.. sys_req:: System shall complete power-on self-test within 500 ms
   :id: SYS_REQ_020
   :status: approved
   :satisfies: STKH_REQ_007, STKH_REQ_009
   :tags: diagnostics; self-test; startup; initialization
   :aspice_process: SYS.2
   :safety_class: ASIL-D
   :verification_method: test
   :priority: high

   On power-on, the ABS ECU shall perform a self-test within **500 ms** of power-up including:

   - ROM integrity check (CRC32 of program memory)
   - RAM write/read pattern test
   - Watchdog timer test
   - HCU solenoid valve functional check (brief energization)
   - Wheel speed sensor signal presence check

   ABS activation shall be inhibited until self-test passes.

   **Derived from:** STKH_REQ_007, STKH_REQ_009

----

Summary
-------

.. needtable::
   :filter: type == "sys_req"
   :columns: id, title, status, satisfies, safety_class
   :style: table
   :sort: id
