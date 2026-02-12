.. _swe1_index:

SWE.1 - Software Requirements Analysis
========================================

.. toctree::
   :maxdepth: 2

   software_requirements

**Purpose:** Define the software requirements for the ABS ECU, derived from the system
requirements (SYS.2) and system architecture (SYS.3).

**Work Products:**

- Software Requirements Specification (SW_REQ_001 – SW_REQ_050)

**Subsystem breakdown:**

+-------------------------------+-------------+--------------------+
| Subsystem                     | IDs         | Count              |
+===============================+=============+====================+
| WSS Driver                    | 001 – 008   | 8 requirements     |
+-------------------------------+-------------+--------------------+
| Vehicle Reference Speed       | 009 – 013   | 5 requirements     |
+-------------------------------+-------------+--------------------+
| Slip Ratio Calculator         | 014 – 018   | 5 requirements     |
+-------------------------------+-------------+--------------------+
| ABS Control Algorithm         | 019 – 027   | 9 requirements     |
+-------------------------------+-------------+--------------------+
| HCU Driver                    | 028 – 034   | 7 requirements     |
+-------------------------------+-------------+--------------------+
| CAN Communication             | 035 – 041   | 7 requirements     |
+-------------------------------+-------------+--------------------+
| Fault Management              | 042 – 047   | 6 requirements     |
+-------------------------------+-------------+--------------------+
| Safety & Fail-Safe            | 048 – 050   | 3 requirements     |
+-------------------------------+-------------+--------------------+
| Total                         |             | 50 requirements    |
+-------------------------------+-------------+--------------------+

**Traceability:** All software requirements derive from system requirements in
:ref:`sys2_system_requirements` and trace to architecture in :ref:`sys3_system_architecture`.

**ASPICE Base Practice Reference:** SWE.1.BP1 – Establish software requirements
