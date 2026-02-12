.. _swe1_software_requirements:

SWE.1 - Software Requirements Specification
============================================

.. contents::
   :local:
   :depth: 1

**Document:** SW-REQ-SPEC-001
**Version:** 1.0
**Status:** Approved
**Domain:** ABS ECU Software

----

WSS Driver Requirements
------------------------

.. sw_req:: WSS driver shall read all four wheel speed sensors at 1 ms interrupt cycle
   :id: SW_REQ_001
   :status: approved
   :derives_from: SYS_REQ_001
   :traces_to: SYS_ARCH_003
   :tags: wss-driver; interrupt; sampling; timing
   :aspice_process: SWE.1
   :safety_class: ASIL-D
   :verification_method: test
   :priority: high

   The WSS driver software shall service all four wheel speed sensor input channels
   within a single **1 ms interrupt service routine (ISR)**. The ISR shall capture the
   pulse counter values for all four channels before returning. Interrupt latency shall
   not exceed 50 µs.

.. sw_req:: WSS driver shall apply digital low-pass filter to raw sensor signals
   :id: SW_REQ_002
   :status: approved
   :derives_from: SYS_REQ_001
   :traces_to: SYS_ARCH_003
   :tags: wss-driver; filter; signal-processing
   :aspice_process: SWE.1
   :safety_class: ASIL-C
   :verification_method: test
   :priority: medium

   The WSS driver shall apply a 4th-order digital low-pass filter (moving average or
   Butterworth) to the raw wheel speed signals before passing them to the application layer.
   Filter cutoff frequency: 50 Hz. Purpose: removal of high-frequency noise and tooth
   harmonic disturbances from the sensor.

.. sw_req:: WSS driver shall calculate wheel angular velocity in rad/s from pulse count
   :id: SW_REQ_003
   :status: approved
   :derives_from: SYS_REQ_001
   :traces_to: SYS_ARCH_003
   :tags: wss-driver; calculation; angular-velocity
   :aspice_process: SWE.1
   :safety_class: ASIL-D
   :verification_method: test
   :priority: high

   The WSS driver shall convert raw pulse counter increments to wheel angular velocity
   using:

   ``ω [rad/s] = (ΔPulseCount × 2π) / (N_teeth × Δt)``

   where ``N_teeth`` = 48 (number of encoder teeth, configurable), and ``Δt`` = 1 ms
   (ISR period). Output range: 0 to 300 rad/s. Resolution: 0.1 rad/s.

.. sw_req:: WSS driver shall detect open circuit sensor fault
   :id: SW_REQ_004
   :status: approved
   :derives_from: SYS_REQ_017
   :traces_to: SYS_ARCH_003
   :tags: wss-driver; fault-detection; open-circuit; diagnostics
   :aspice_process: SWE.1
   :safety_class: ASIL-D
   :verification_method: test
   :priority: high

   The WSS driver shall detect an open circuit condition for each sensor channel.
   Fault condition: no pulse received for **> 50 ms** while estimated vehicle speed
   > 5 km/h. Upon detection, the driver shall set the WSS_FAULT_OPEN bit for the
   affected channel and report to the Fault Manager within the same 5 ms task cycle.

.. sw_req:: WSS driver shall detect short circuit sensor fault
   :id: SW_REQ_005
   :status: approved
   :derives_from: SYS_REQ_017
   :traces_to: SYS_ARCH_003
   :tags: wss-driver; fault-detection; short-circuit; diagnostics
   :aspice_process: SWE.1
   :safety_class: ASIL-D
   :verification_method: test
   :priority: high

   The WSS driver shall detect a short-circuit condition by monitoring the sensor
   supply current. Fault condition: supply current > 500 mA (short to ground) or
   < 20 mA (open/short to supply) on any channel. Detection latency: within 10 ms.

.. sw_req:: WSS driver shall perform plausibility check on all four wheel speeds
   :id: SW_REQ_006
   :status: approved
   :derives_from: SYS_REQ_017
   :traces_to: SYS_ARCH_003
   :tags: wss-driver; plausibility; cross-check
   :aspice_process: SWE.1
   :safety_class: ASIL-D
   :verification_method: test
   :priority: high

   The WSS driver shall compare each wheel speed against adjacent wheel speeds at every
   5 ms task cycle. A plausibility error is flagged when a wheel speed deviates by more
   than **50%** from the average of the other three wheels while vehicle speed > 10 km/h
   and no ABS activation is in progress.

.. sw_req:: WSS driver shall report sensor status to fault manager
   :id: SW_REQ_007
   :status: approved
   :derives_from: SYS_REQ_017
   :traces_to: SYS_ARCH_003
   :tags: wss-driver; fault-reporting; interface
   :aspice_process: SWE.1
   :safety_class: ASIL-D
   :verification_method: test
   :priority: high

   The WSS driver shall report the health status of each sensor channel to the Fault
   Manager at every 5 ms cycle. Status values: ``WSS_OK``, ``WSS_FAULT_OPEN``,
   ``WSS_FAULT_SHORT``, ``WSS_FAULT_PLAUSIBILITY``, ``WSS_DEGRADED``.

.. sw_req:: WSS driver shall provide calibrated wheel speed to application layer
   :id: SW_REQ_008
   :status: approved
   :derives_from: SYS_REQ_001
   :traces_to: SYS_ARCH_003
   :tags: wss-driver; interface; output; calibration
   :aspice_process: SWE.1
   :safety_class: ASIL-D
   :verification_method: test
   :priority: high

   The WSS driver shall provide filtered and calibrated wheel speed values (in km/h)
   to the application layer via a shared data structure updated at every 1 ms ISR cycle.
   On a faulty channel, the driver shall set the corresponding speed value to 0.0 km/h
   and mark the validity flag as INVALID.

----

Vehicle Reference Speed Requirements
--------------------------------------

.. sw_req:: Software shall calculate vehicle reference speed during non-ABS braking
   :id: SW_REQ_009
   :status: approved
   :derives_from: SYS_REQ_005
   :traces_to: SYS_ARCH_002
   :tags: reference-speed; algorithm; vehicle-speed
   :aspice_process: SWE.1
   :safety_class: ASIL-D
   :verification_method: test
   :priority: high

   During non-ABS braking, the software shall estimate vehicle reference speed as
   the **maximum** of the four filtered wheel speeds:

   ``v_ref = max(v_FL, v_FR, v_RL, v_RR)``

   Only wheel speed channels with valid status (WSS_OK or WSS_DEGRADED) shall be
   included in the maximum computation. If fewer than two valid channels remain,
   the reference speed shall be flagged as INVALID.

.. sw_req:: Software shall maintain reference speed using deceleration model during ABS
   :id: SW_REQ_010
   :status: approved
   :derives_from: SYS_REQ_005
   :traces_to: SYS_ARCH_002
   :tags: reference-speed; deceleration-model; abs-active
   :aspice_process: SWE.1
   :safety_class: ASIL-D
   :verification_method: test
   :priority: high

   When ABS is active and wheel speeds are unreliable (due to lock), the software
   shall maintain the vehicle reference speed using a kinematic deceleration model:

   ``v_ref(t) = v_ref(t-1) - a_max × Δt``

   where ``a_max`` = 11.77 m/s² (1.2g, maximum road deceleration).
   Reference speed is re-synchronized when a non-locked wheel is detected.

.. sw_req:: Software shall update reference speed at 1 ms cycle
   :id: SW_REQ_011
   :status: approved
   :derives_from: SYS_REQ_005
   :traces_to: SYS_ARCH_002
   :tags: reference-speed; timing; cycle-time
   :aspice_process: SWE.1
   :safety_class: ASIL-D
   :verification_method: test
   :priority: high

   The vehicle reference speed estimation function shall execute within the 1 ms
   WSS interrupt task to ensure maximum freshness for the slip ratio calculator.
   Output shall be available within 0.5 ms of WSS data capture.

.. sw_req:: Software shall validate reference speed change rate
   :id: SW_REQ_012
   :status: approved
   :derives_from: SYS_REQ_005
   :traces_to: SYS_ARCH_002
   :tags: reference-speed; validation; plausibility
   :aspice_process: SWE.1
   :safety_class: ASIL-D
   :verification_method: test
   :priority: high

   The software shall validate the computed reference speed by checking that the
   change between consecutive cycles does not exceed physically possible deceleration:
   maximum change = **5.0 km/h per 10 ms** (equivalent to ~1.4g deceleration).
   If exceeded, the previous valid value is held and a plausibility fault is flagged.

.. sw_req:: Software shall provide filtered reference speed output
   :id: SW_REQ_013
   :status: approved
   :derives_from: SYS_REQ_005
   :traces_to: SYS_ARCH_002
   :tags: reference-speed; filter; output
   :aspice_process: SWE.1
   :safety_class: ASIL-C
   :verification_method: test
   :priority: medium

   The reference speed output provided to the slip ratio calculator shall be
   smoothed using a first-order IIR filter with time constant τ = 5 ms to remove
   transient spikes. Filter coefficient α = 0.5 (50% of new value, 50% of previous).

----

Slip Ratio Calculator Requirements
------------------------------------

.. sw_req:: Software shall calculate wheel slip ratio for each channel
   :id: SW_REQ_014
   :status: approved
   :derives_from: SYS_REQ_004
   :traces_to: SYS_ARCH_002
   :tags: slip-ratio; calculation; algorithm
   :aspice_process: SWE.1
   :safety_class: ASIL-D
   :verification_method: test
   :priority: high

   The software shall compute the slip ratio λ for each wheel channel:

   ``λ = (v_ref - v_wheel) / max(v_ref, ε)``

   where ``ε`` = 0.278 m/s (= 1 km/h) to prevent division by zero.
   Output range: 0.0 (free rolling) to 1.0 (locked). Update rate: 1 ms.

.. sw_req:: Software shall apply configurable slip threshold for ABS activation
   :id: SW_REQ_015
   :status: approved
   :derives_from: SYS_REQ_004, SYS_REQ_006
   :traces_to: SYS_ARCH_002
   :tags: slip-ratio; threshold; abs-activation; adaptive
   :aspice_process: SWE.1
   :safety_class: ASIL-D
   :verification_method: test
   :priority: high

   The ABS activation slip threshold shall be configurable via calibration parameters.
   Default thresholds: lower = 15% slip (pressure build to hold transition),
   upper = 25% slip (ABS activation / hold to release transition).
   Thresholds shall be adaptable based on detected road surface condition (SW_REQ_006).

.. sw_req:: Software shall provide slip ratio per channel to ABS controller
   :id: SW_REQ_016
   :status: approved
   :derives_from: SYS_REQ_004
   :traces_to: SYS_ARCH_002
   :tags: slip-ratio; interface; output
   :aspice_process: SWE.1
   :safety_class: ASIL-D
   :verification_method: test
   :priority: high

   The slip ratio calculator shall output slip ratio values for all four wheel channels
   to the ABS control algorithm via a zero-copy shared data interface. Data shall be
   marked with a validity timestamp and channel status (VALID/INVALID/FAULT).

.. sw_req:: Software shall detect wheel lock condition from slip ratio
   :id: SW_REQ_017
   :status: approved
   :derives_from: SYS_REQ_002, SYS_REQ_004
   :traces_to: SYS_ARCH_002
   :tags: slip-ratio; wheel-lock; detection
   :aspice_process: SWE.1
   :safety_class: ASIL-D
   :verification_method: test
   :priority: high

   The software shall declare a wheel lock condition for a channel when its slip ratio
   exceeds **0.80 (80%)** for more than **5 consecutive 1 ms cycles** (5 ms persistence).
   The WHEEL_LOCKED flag for the affected channel shall be set immediately in the
   ABS control algorithm's input data structure.

.. sw_req:: Software shall handle divide-by-zero in slip ratio calculation
   :id: SW_REQ_018
   :status: approved
   :derives_from: SYS_REQ_004
   :traces_to: SYS_ARCH_002
   :tags: slip-ratio; safety; division; edge-case
   :aspice_process: SWE.1
   :safety_class: ASIL-D
   :verification_method: test
   :priority: high

   When vehicle reference speed falls below 1 km/h (v_ref < 0.278 m/s), the slip
   ratio shall be computed using ``ε = 0.278 m/s`` as denominator. The ABS controller
   shall be commanded to deactivate below 3 km/h (SW_REQ_027), avoiding undefined
   slip ratio behavior at standstill.

----

ABS Control Algorithm Requirements
-------------------------------------

.. sw_req:: ABS controller shall activate when slip ratio exceeds activation threshold
   :id: SW_REQ_019
   :status: approved
   :derives_from: SYS_REQ_003, SYS_REQ_010
   :traces_to: SYS_ARCH_002
   :tags: abs-control; activation; threshold
   :aspice_process: SWE.1
   :safety_class: ASIL-D
   :verification_method: test
   :priority: high

   The ABS controller shall transition a wheel channel from NORMAL_BRAKING to
   PRESSURE_HOLD state when that channel's slip ratio exceeds the configurable upper
   threshold (default 25%). ABS activation shall be independent per channel.
   ABS activation is inhibited below 5 km/h vehicle speed.

.. sw_req:: ABS controller shall command PRESSURE_BUILD when slip is below lower threshold
   :id: SW_REQ_020
   :status: approved
   :derives_from: SYS_REQ_007
   :traces_to: SYS_ARCH_002
   :tags: abs-control; pressure-build; phase
   :aspice_process: SWE.1
   :safety_class: ASIL-D
   :verification_method: test
   :priority: high

   The ABS controller shall command the PRESSURE_BUILD phase (inlet valve open,
   outlet valve closed) for a channel when that channel's slip ratio falls below the
   lower threshold (default 10%) and no wheel lock is detected.
   Transition condition: λ < λ_lower AND NOT WHEEL_LOCKED.

.. sw_req:: ABS controller shall command PRESSURE_HOLD when slip approaches upper threshold
   :id: SW_REQ_021
   :status: approved
   :derives_from: SYS_REQ_007
   :traces_to: SYS_ARCH_002
   :tags: abs-control; pressure-hold; phase
   :aspice_process: SWE.1
   :safety_class: ASIL-D
   :verification_method: test
   :priority: high

   The ABS controller shall command the PRESSURE_HOLD phase (inlet valve closed,
   outlet valve closed) for a channel when the slip ratio is within the control band
   (λ_lower ≤ λ ≤ λ_upper) and the wheel is not locked.
   Transition condition: λ_lower ≤ λ ≤ λ_upper AND NOT WHEEL_LOCKED.

.. sw_req:: ABS controller shall command PRESSURE_RELEASE on wheel lock detection
   :id: SW_REQ_022
   :status: approved
   :derives_from: SYS_REQ_007
   :traces_to: SYS_ARCH_002
   :tags: abs-control; pressure-release; phase; wheel-lock
   :aspice_process: SWE.1
   :safety_class: ASIL-D
   :verification_method: test
   :priority: high

   The ABS controller shall command the PRESSURE_RELEASE phase (inlet valve closed,
   outlet valve open, pump active) for a channel immediately upon detecting a wheel
   lock condition (WHEEL_LOCKED flag set, λ > 0.80).
   Maximum PRESSURE_RELEASE duration per cycle: 50 ms (configurable).

.. sw_req:: ABS controller shall operate all four channels independently
   :id: SW_REQ_023
   :status: approved
   :derives_from: SYS_REQ_010
   :traces_to: SYS_ARCH_002
   :tags: abs-control; independent-channels; four-channel
   :aspice_process: SWE.1
   :safety_class: ASIL-D
   :verification_method: test
   :priority: high

   The ABS control algorithm shall maintain an independent state machine for each of
   the four wheel channels (FL, FR, RL, RR). State transitions for one channel shall
   not directly affect other channels, with the exception of the select-low logic
   applied to the rear axle (SW_REQ_026).

.. sw_req:: ABS controller shall complete control decision within 2 ms
   :id: SW_REQ_024
   :status: approved
   :derives_from: SYS_REQ_003
   :traces_to: SYS_ARCH_002
   :tags: abs-control; timing; cycle-time; performance
   :aspice_process: SWE.1
   :safety_class: ASIL-D
   :verification_method: test
   :priority: high

   The ABS control algorithm shall complete all four channel state evaluations and
   generate actuator commands within **2 ms** of receiving input slip ratio data.
   This budget is part of the overall 5 ms ECU cycle time allocation (SYS_REQ_003).

.. sw_req:: ABS controller shall limit pressure release duration per cycle
   :id: SW_REQ_025
   :status: approved
   :derives_from: SYS_REQ_007
   :traces_to: SYS_ARCH_002
   :tags: abs-control; pressure-release; duration-limit; timing
   :aspice_process: SWE.1
   :safety_class: ASIL-C
   :verification_method: test
   :priority: medium

   The software shall limit the maximum duration of a single PRESSURE_RELEASE phase
   to **50 ms** (configurable parameter). After 50 ms, the controller shall transition
   to PRESSURE_BUILD regardless of wheel slip state, to prevent excessive pressure drop
   that could reduce braking performance.

.. sw_req:: ABS controller shall implement select-low logic for rear axle
   :id: SW_REQ_026
   :status: approved
   :derives_from: SYS_REQ_010
   :traces_to: SYS_ARCH_002
   :tags: abs-control; select-low; rear-axle; stability
   :aspice_process: SWE.1
   :safety_class: ASIL-C
   :verification_method: test
   :priority: medium

   For the rear axle, the software shall implement **select-low** channel control logic:
   the rear wheel with the **lower wheel speed** (higher slip) shall govern the hydraulic
   pressure command applied to both rear wheels simultaneously. This prevents rear axle
   instability caused by excessive rear-wheel pressure differential.

.. sw_req:: ABS controller shall deactivate when vehicle speed falls below 3 km/h
   :id: SW_REQ_027
   :status: approved
   :derives_from: SYS_REQ_003, SYS_REQ_010
   :traces_to: SYS_ARCH_002
   :tags: abs-control; deactivation; low-speed; standstill
   :aspice_process: SWE.1
   :safety_class: ASIL-C
   :verification_method: test
   :priority: medium

   The ABS controller shall deactivate all channels (transition to NORMAL_BRAKING) and
   de-energize all HCU solenoid valves when the vehicle reference speed falls below
   **3 km/h**. This prevents erratic ABS behavior at very low speeds and avoids
   slip ratio computation singularities near standstill.

----

HCU Driver Requirements
--------------------------

.. sw_req:: HCU driver shall control inlet solenoid valves per ABS controller command
   :id: SW_REQ_028
   :status: approved
   :derives_from: SYS_REQ_007, SYS_REQ_008
   :traces_to: SYS_ARCH_004
   :tags: hcu-driver; inlet-valve; solenoid-control
   :aspice_process: SWE.1
   :safety_class: ASIL-D
   :verification_method: test
   :priority: high

   The HCU driver shall control each of the four inlet solenoid valves via dedicated
   GPIO high-side switch outputs. Energized = valve CLOSED (isolating master cylinder).
   De-energized = valve OPEN (normal brake pressure pathway).
   Command-to-output latency: ≤ 500 µs from receiving ABS controller command.

.. sw_req:: HCU driver shall control outlet solenoid valves per ABS controller command
   :id: SW_REQ_029
   :status: approved
   :derives_from: SYS_REQ_007, SYS_REQ_008
   :traces_to: SYS_ARCH_004
   :tags: hcu-driver; outlet-valve; solenoid-control
   :aspice_process: SWE.1
   :safety_class: ASIL-D
   :verification_method: test
   :priority: high

   The HCU driver shall control each of the four outlet solenoid valves via dedicated
   GPIO high-side switch outputs. Energized = valve OPEN (releasing pressure to accumulator).
   De-energized = valve CLOSED (normal state).
   Default safe state (ABS inactive or system fault): all outlet valves de-energized (CLOSED).

.. sw_req:: HCU driver shall control pump motor via PWM during ABS active
   :id: SW_REQ_030
   :status: approved
   :derives_from: SYS_REQ_007
   :traces_to: SYS_ARCH_004
   :tags: hcu-driver; pump-motor; pwm-control
   :aspice_process: SWE.1
   :safety_class: ASIL-C
   :verification_method: test
   :priority: medium

   The HCU driver shall activate the hydraulic pump motor via a PWM output (carrier
   frequency: 400 Hz) whenever at least one channel is in PRESSURE_RELEASE phase.
   Default duty cycle: **70%** (configurable). Pump shall be de-activated within 100 ms
   after all channels exit PRESSURE_RELEASE.

.. sw_req:: HCU driver shall detect solenoid valve faults
   :id: SW_REQ_031
   :status: approved
   :derives_from: SYS_REQ_017
   :traces_to: SYS_ARCH_004
   :tags: hcu-driver; fault-detection; solenoid; over-current
   :aspice_process: SWE.1
   :safety_class: ASIL-D
   :verification_method: test
   :priority: high

   The HCU driver shall monitor each solenoid valve current via ADC channels. Fault
   conditions:

   - **Over-current:** measured current > 3 A (winding short circuit)
   - **Open circuit:** measured current < 50 mA when valve commanded energized
   - **Stuck valve:** valve not responding to command (via back-EMF monitoring)

   Fault detection latency: ≤ 10 ms.

.. sw_req:: HCU driver shall apply minimum valve energization debounce
   :id: SW_REQ_032
   :status: approved
   :derives_from: SYS_REQ_008
   :traces_to: SYS_ARCH_004
   :tags: hcu-driver; debounce; valve-timing
   :aspice_process: SWE.1
   :safety_class: ASIL-C
   :verification_method: test
   :priority: medium

   The HCU driver shall enforce a minimum solenoid valve state duration of **1 ms**
   before allowing any state change. Rapid state transitions shorter than 1 ms shall
   be suppressed to protect valve hardware from excessive switching cycles and to
   ensure full mechanical valve travel.

.. sw_req:: HCU driver shall execute initialization sequence on system startup
   :id: SW_REQ_033
   :status: approved
   :derives_from: SYS_REQ_020
   :traces_to: SYS_ARCH_004
   :tags: hcu-driver; initialization; startup; self-test
   :aspice_process: SWE.1
   :safety_class: ASIL-D
   :verification_method: test
   :priority: high

   During system startup (as part of power-on self-test), the HCU driver shall execute:

   1. Briefly energize each inlet valve (50 ms) and verify current response
   2. Briefly energize each outlet valve (50 ms) and verify current response
   3. Run pump motor for 100 ms and verify current consumption (1–5 A expected)
   4. Report any initialization failures to Fault Manager

   Total initialization time: ≤ 300 ms.

.. sw_req:: HCU driver shall detect pump motor stall condition
   :id: SW_REQ_034
   :status: approved
   :derives_from: SYS_REQ_017
   :traces_to: SYS_ARCH_004
   :tags: hcu-driver; pump-motor; stall; fault-detection
   :aspice_process: SWE.1
   :safety_class: ASIL-C
   :verification_method: test
   :priority: medium

   The HCU driver shall detect a pump motor stall condition when: pump commanded active
   AND measured motor current > **8 A** for > **100 ms**. Upon stall detection, the
   driver shall de-activate the pump and report HCU_FAULT_PUMP_STALL to the Fault Manager.

----

CAN Communication Requirements
---------------------------------

.. sw_req:: CAN driver shall transmit WheelSpeeds message at 10 ms period
   :id: SW_REQ_035
   :status: approved
   :derives_from: SYS_REQ_011
   :traces_to: SYS_ARCH_005
   :tags: can-driver; tx; wheel-speeds; periodic
   :aspice_process: SWE.1
   :safety_class: ASIL-B
   :verification_method: test
   :priority: medium

   The CAN driver shall transmit the ``WheelSpeeds`` message (CAN ID: 0x3A0, DLC: 8)
   at a **10 ms** periodic rate. Message payload: FL speed (16-bit), FR speed (16-bit),
   RL speed (16-bit), RR speed (16-bit). Resolution: 0.01 km/h, range: 0–655.35 km/h.
   Jitter tolerance: ±1 ms.

.. sw_req:: CAN driver shall transmit ABSStatus message at 20 ms period
   :id: SW_REQ_036
   :status: approved
   :derives_from: SYS_REQ_013
   :traces_to: SYS_ARCH_005
   :tags: can-driver; tx; abs-status; periodic
   :aspice_process: SWE.1
   :safety_class: ASIL-B
   :verification_method: test
   :priority: medium

   The CAN driver shall transmit the ``ABSStatus`` message (CAN ID: 0x3A2, DLC: 4)
   at a **20 ms** periodic rate. Message payload: ABS active flags (1 bit/channel × 4),
   fault status flags (1 bit/channel × 4), ECU status (8-bit). Jitter tolerance: ±2 ms.

.. sw_req:: CAN driver shall receive VehicleStatus message with timeout detection
   :id: SW_REQ_037
   :status: approved
   :derives_from: SYS_REQ_011
   :traces_to: SYS_ARCH_005
   :tags: can-driver; rx; vehicle-status; timeout
   :aspice_process: SWE.1
   :safety_class: ASIL-B
   :verification_method: test
   :priority: medium

   The CAN driver shall receive the ``VehicleStatus`` message (CAN ID: 0x1A0) with
   a reception timeout monitor of **100 ms**. If no message is received within 100 ms,
   the driver shall set the CAN_RX_TIMEOUT flag and report to the Fault Manager.
   Timeout shall not immediately disable ABS but shall degrade to reduced-performance mode.

.. sw_req:: CAN driver shall implement bus-off recovery per ISO 11898
   :id: SW_REQ_038
   :status: approved
   :derives_from: SYS_REQ_011
   :traces_to: SYS_ARCH_005
   :tags: can-driver; bus-off; error-recovery; iso11898
   :aspice_process: SWE.1
   :safety_class: ASIL-B
   :verification_method: test
   :priority: medium

   The CAN driver shall implement automatic bus-off recovery per ISO 11898-1.
   Upon entering bus-off state (TEC > 255), the driver shall initiate the hardware
   recovery sequence (128 occurrences of 11 recessive bits). Maximum recovery attempts:
   3 before logging a permanent CAN_BUS_OFF DTC.

.. sw_req:: CAN driver shall validate received message DLC
   :id: SW_REQ_039
   :status: approved
   :derives_from: SYS_REQ_011
   :traces_to: SYS_ARCH_005
   :tags: can-driver; rx; validation; dlc
   :aspice_process: SWE.1
   :safety_class: ASIL-B
   :verification_method: test
   :priority: medium

   The CAN driver shall validate the Data Length Code (DLC) of all received messages
   before forwarding payload data to upper layers. If the received DLC does not match
   the expected DLC for that message ID, the message shall be discarded and a
   CAN_DLC_MISMATCH error shall be logged.

.. sw_req:: CAN driver shall support UDS diagnostic services
   :id: SW_REQ_040
   :status: approved
   :derives_from: SYS_REQ_012
   :traces_to: SYS_ARCH_005
   :tags: can-driver; uds; diagnostics; obd-ii
   :aspice_process: SWE.1
   :safety_class: QM
   :verification_method: test
   :priority: medium

   The CAN driver shall support Unified Diagnostic Services (UDS) over ISO 15765-4.
   Required service implementations:

   - ``0x22`` – Read Data by Identifier (live wheel speed data, ECU status)
   - ``0x19`` – Read DTC Information (subfunction 0x02, 0x06)
   - ``0x14`` – Clear Diagnostic Information (all DTCs)
   - ``0x27`` – Security Access (Level 01/02 for calibration write access)

.. sw_req:: CAN driver shall report CAN bus error status to fault manager
   :id: SW_REQ_041
   :status: approved
   :derives_from: SYS_REQ_011
   :traces_to: SYS_ARCH_005
   :tags: can-driver; error-reporting; fault-manager; interface
   :aspice_process: SWE.1
   :safety_class: ASIL-B
   :verification_method: test
   :priority: medium

   The CAN driver shall report the CAN controller error counters (TEC, REC) and bus
   state (BUS_ACTIVE, BUS_WARNING, BUS_ERROR_PASSIVE, BUS_OFF) to the Fault Manager
   at every 10 ms cycle. Error thresholds: TEC > 96 = WARNING, TEC > 127 = ERROR_PASSIVE.

----

Fault Management Requirements
--------------------------------

.. sw_req:: Fault manager shall collect fault status from all modules every 5 ms
   :id: SW_REQ_042
   :status: approved
   :derives_from: SYS_REQ_017, SYS_REQ_019
   :traces_to: SYS_ARCH_002
   :tags: fault-manager; polling; monitoring; cycle-time
   :aspice_process: SWE.1
   :safety_class: ASIL-D
   :verification_method: test
   :priority: high

   The Fault Manager shall poll the fault status registers of all software modules
   (WSS Driver, HCU Driver, CAN Driver, ABS Controller) at every **5 ms task cycle**.
   All fault information shall be consolidated into a single fault status word per module.

.. sw_req:: Fault manager shall apply debounce before activating a fault
   :id: SW_REQ_043
   :status: approved
   :derives_from: SYS_REQ_017
   :traces_to: SYS_ARCH_002
   :tags: fault-manager; debounce; fault-qualification
   :aspice_process: SWE.1
   :safety_class: ASIL-D
   :verification_method: test
   :priority: high

   The Fault Manager shall apply a **debounce counter** of 5 consecutive positive
   detection cycles (= 25 ms at 5 ms cycle) before classifying a fault as ACTIVE.
   Exception: CRITICAL faults (e.g., RAM error, watchdog miss) shall be activated
   immediately without debounce.

.. sw_req:: Fault manager shall store confirmed DTCs to NVM
   :id: SW_REQ_044
   :status: approved
   :derives_from: SYS_REQ_019
   :traces_to: SYS_ARCH_002
   :tags: fault-manager; dtc; nvm; storage
   :aspice_process: SWE.1
   :safety_class: QM
   :verification_method: test
   :priority: medium

   When a fault transitions to ACTIVE state, the Fault Manager shall write a DTC entry
   to NVM containing: DTC code (16-bit), first occurrence timestamp (ms since power-on),
   last occurrence timestamp, occurrence counter (max 255), status byte (ACTIVE/STORED/PENDING).
   Writes to NVM shall complete within 10 ms using the NVM manager API.

.. sw_req:: Fault manager shall control ABS warning lamp based on fault status
   :id: SW_REQ_045
   :status: approved
   :derives_from: SYS_REQ_018
   :traces_to: SYS_ARCH_002
   :tags: fault-manager; warning-lamp; hmi; indicator
   :aspice_process: SWE.1
   :safety_class: ASIL-B
   :verification_method: test
   :priority: high

   The Fault Manager shall control the ABS warning lamp output signal based on
   current fault status:

   - **CRITICAL fault active:** Lamp ON (continuous)
   - **MAJOR fault active:** Lamp ON (continuous)
   - **MINOR fault only:** Lamp BLINK (1 Hz, 50% duty cycle)
   - **No active faults:** Lamp OFF

   Warning lamp state shall be updated within 500 ms of fault status change.

.. sw_req:: Fault manager shall classify faults by severity
   :id: SW_REQ_046
   :status: approved
   :derives_from: SYS_REQ_018
   :traces_to: SYS_ARCH_002
   :tags: fault-manager; classification; severity; dtc
   :aspice_process: SWE.1
   :safety_class: ASIL-D
   :verification_method: inspection
   :priority: high

   The Fault Manager shall classify all monitored faults into three severity levels:

   - **CRITICAL:** Immediately disables ABS (e.g., ECU internal fault, all WSS failed, HCU valve driver short)
   - **MAJOR:** Degrades ABS function (e.g., one WSS failed, pump motor fault)
   - **MINOR:** Logged only, no functional impact (e.g., CAN reception timeout, temperature warning)

.. sw_req:: Fault manager shall trigger safe state transition on critical fault
   :id: SW_REQ_047
   :status: approved
   :derives_from: SYS_REQ_018
   :traces_to: SYS_ARCH_002
   :tags: fault-manager; safe-state; critical-fault; fail-safe
   :aspice_process: SWE.1
   :safety_class: ASIL-D
   :verification_method: test
   :priority: high

   Upon detecting a CRITICAL fault, the Fault Manager shall immediately:

   1. Set the ABS_DISABLE flag (prevents ABS controller from issuing valve commands)
   2. Command the HCU driver to de-energize all solenoid valves (fail-safe default state)
   3. Set the WARNING_LAMP_ON command
   4. Store a DTC to NVM
   5. Inhibit re-activation of ABS until power cycle

----

Safety & Fail-Safe Requirements
---------------------------------

.. sw_req:: Software shall disable ABS actuation on critical fault
   :id: SW_REQ_048
   :status: approved
   :derives_from: SYS_REQ_018
   :traces_to: SYS_ARCH_001
   :tags: safety; fail-safe; abs-disable; safe-state
   :aspice_process: SWE.1
   :safety_class: ASIL-D
   :verification_method: test
   :priority: high

   On a critical fault condition, the software shall disable all ABS valve actuation
   and set all eight solenoid valve outputs to the **de-energized (safe default)** state:

   - All inlet valves: de-energized (OPEN — normal brake pressure passes through)
   - All outlet valves: de-energized (CLOSED — prevents pressure loss)
   - Pump motor: PWM duty cycle = 0% (OFF)

   This ensures normal (non-ABS) braking is preserved as required by STKH_REQ_009.

.. sw_req:: Software shall service watchdog timer every 2 ms
   :id: SW_REQ_049
   :status: approved
   :derives_from: SYS_REQ_020
   :traces_to: SYS_ARCH_001
   :tags: safety; watchdog; hardware-reset; integrity
   :aspice_process: SWE.1
   :safety_class: ASIL-D
   :verification_method: test
   :priority: high

   The software shall service (trigger) the hardware watchdog timer every **2 ms**.
   The watchdog timer window: 1 ms (min) to 3 ms (max). Servicing outside this window
   (too early or too late) shall trigger a hardware reset. The watchdog service call
   shall be located in the 1 ms base task to ensure deterministic execution.

.. sw_req:: Software shall perform ROM and RAM integrity checks at startup
   :id: SW_REQ_050
   :status: approved
   :derives_from: SYS_REQ_020
   :traces_to: SYS_ARCH_001
   :tags: safety; rom-check; ram-check; startup; integrity
   :aspice_process: SWE.1
   :safety_class: ASIL-D
   :verification_method: test
   :priority: high

   During power-on self-test, the software shall perform:

   1. **ROM integrity check:** CRC32 computed over program flash memory and compared
      against a stored reference CRC. Failure: store DTC ROM_CRC_FAIL and inhibit ABS.
   2. **RAM test:** Walking 1s/0s pattern test over all RAM sections used by ABS.
      Failure: store DTC RAM_PATTERN_FAIL and inhibit ABS activation.

   Both tests shall complete within **200 ms** as part of the 500 ms startup budget.

----

Summary
-------

.. needtable::
   :filter: type == "sw_req"
   :columns: id, title, status, derives_from, safety_class
   :style: table
   :sort: id
