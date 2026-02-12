.. _sys1_stakeholder_requirements:

SYS.1 - Stakeholder Requirements Specification
===============================================

.. contents::
   :local:
   :depth: 1

**Document:** STKH-REQ-SPEC-001
**Version:** 1.0
**Status:** Approved
**Domain:** Anti-Lock Braking System (ABS)

These requirements represent the top-level needs of the OEM, end customer, and regulatory
bodies. All system and software requirements shall be traceable to at least one stakeholder
requirement below.

----

Safety Requirements
-------------------

.. stkh_req:: Vehicle shall remain steerable during emergency braking
   :id: STKH_REQ_001
   :status: approved
   :tags: safety; steerability; emergency-braking
   :aspice_process: SYS.1
   :safety_class: ASIL-D
   :verification_method: test
   :priority: high

   The vehicle shall remain steerable and maintain directional stability during
   maximum-effort braking on all road surface conditions. The driver shall be able to
   steer around obstacles even when maximum braking force is applied.

   **Source:** OEM Safety Specification v3.2, Section 4.1.1

.. stkh_req:: ABS shall prevent sustained wheel lockup during braking
   :id: STKH_REQ_002
   :status: approved
   :tags: safety; wheel-lockup; braking
   :aspice_process: SYS.1
   :safety_class: ASIL-D
   :verification_method: test
   :priority: high

   The ABS system shall detect and prevent sustained wheel lockup during any braking
   maneuver. Wheel lockup shall be resolved within the system reaction time defined in
   the performance requirements.

   **Source:** ECE R13 Regulation, Annex 6

.. stkh_req:: ABS shall not degrade braking distance on high-friction surfaces
   :id: STKH_REQ_003
   :status: approved
   :tags: performance; braking-distance; high-friction
   :aspice_process: SYS.1
   :safety_class: ASIL-C
   :verification_method: test
   :priority: high

   On high-friction surfaces (µ > 0.8), the ABS system shall not increase the total
   braking distance by more than 5% compared to a vehicle without ABS under the same
   braking conditions.

   **Source:** ECE R13 Annex 4, Section 2.3; FMVSS 135 §571.135

----

Performance Requirements
------------------------

.. stkh_req:: ABS intervention shall be transparent to the driver
   :id: STKH_REQ_004
   :status: approved
   :tags: performance; response-time; hmi
   :aspice_process: SYS.1
   :safety_class: ASIL-B
   :verification_method: test
   :priority: high

   ABS intervention shall commence within 150 ms of wheel lock onset. The pedal
   feedback (pulsation) during ABS activation shall be within acceptable limits as
   defined in OEM NVH specification (max 3 Hz pedal vibration amplitude < 30 N).

   **Source:** OEM NVH Specification, Section 7.2

.. stkh_req:: ABS shall operate effectively on all road surface types
   :id: STKH_REQ_005
   :status: approved
   :tags: performance; multi-surface; adaptability
   :aspice_process: SYS.1
   :safety_class: ASIL-C
   :verification_method: test
   :priority: high

   The ABS system shall provide effective wheel lockup prevention on all road surface
   types including: dry asphalt (µ ≥ 0.8), wet asphalt (µ ≥ 0.5), gravel (µ ≈ 0.4),
   snow (µ ≈ 0.2), and ice (µ ≈ 0.1).

   **Source:** OEM All-Season Performance Requirements, Rev 2

----

Regulatory & Compliance Requirements
-------------------------------------

.. stkh_req:: ABS shall comply with applicable regulations and standards
   :id: STKH_REQ_006
   :status: approved
   :tags: compliance; regulatory; ece-r13; fmvss
   :aspice_process: SYS.1
   :safety_class: ASIL-D
   :verification_method: inspection
   :priority: high

   The ABS system shall comply with all applicable regulations and standards including:

   - ECE Regulation No. 13 (Uniform provisions concerning braking)
   - FMVSS 135 (Light vehicle brake systems)
   - ISO 26262 (Functional Safety) for ASIL-D components
   - CISPR 25 (EMC requirements for vehicles)

   **Source:** Legal requirements, OEM homologation requirements

----

Reliability & Availability Requirements
-----------------------------------------

.. stkh_req:: ABS shall achieve defined reliability targets
   :id: STKH_REQ_007
   :status: approved
   :tags: reliability; availability; mtbf
   :aspice_process: SYS.1
   :safety_class: ASIL-C
   :verification_method: analysis
   :priority: medium

   The ABS system shall achieve:

   - System availability > 99.9% during vehicle operational lifetime (10 years / 200,000 km)
   - Mean Time Between Failures (MTBF) > 100,000 operating hours
   - No single-point failures that cause loss of normal braking function

   **Source:** OEM Reliability Specification, Section 3.4

----

Fault Indication Requirements
-------------------------------

.. stkh_req:: ABS shall provide fault indication to the driver
   :id: STKH_REQ_008
   :status: approved
   :tags: hmi; warning-lamp; fault-indication
   :aspice_process: SYS.1
   :safety_class: ASIL-B
   :verification_method: test
   :priority: medium

   When an ABS fault is detected, the driver shall be notified via the instrument cluster
   ABS warning lamp. The warning lamp shall illuminate within 2 seconds of fault detection
   and remain on for the duration of the fault condition.

   **Source:** ECE R13 Annex 13, Section 5.2.1

----

Fail-Safe Requirements
-----------------------

.. stkh_req:: Normal braking shall be preserved on ABS failure
   :id: STKH_REQ_009
   :status: approved
   :tags: safety; fail-safe; normal-braking
   :aspice_process: SYS.1
   :safety_class: ASIL-D
   :verification_method: test
   :priority: high

   Upon detection of any ABS critical fault, the system shall revert to normal
   (non-ABS) braking operation. The normal braking function shall be fully preserved and
   unaffected by any ABS component failure. The driver shall retain full braking capability.

   **Source:** ISO 26262-4, Clause 6; OEM Fail-Safe Requirements

----

Serviceability Requirements
-----------------------------

.. stkh_req:: ABS shall support diagnostic access via OBD-II
   :id: STKH_REQ_010
   :status: approved
   :tags: diagnostics; obd-ii; serviceability
   :aspice_process: SYS.1
   :safety_class: QM
   :verification_method: test
   :priority: medium

   The ABS system shall support vehicle diagnostic access via the OBD-II interface.
   Authorized service tools shall be able to:

   - Read Diagnostic Trouble Codes (DTCs) stored by the ABS ECU
   - Clear DTCs after fault rectification
   - Read live ABS data (wheel speeds, ABS active status)
   - Perform ABS system initialization/calibration procedures

   **Source:** OBD-II Standard (SAE J1979), OEM Service Requirements

----

Summary
-------

.. needtable::
   :filter: type == "stkh_req"
   :columns: id, title, status, safety_class, priority
   :style: table
   :sort: id
