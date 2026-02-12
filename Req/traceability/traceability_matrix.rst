.. _traceability_matrix:

Requirements Traceability Matrix
==================================

.. contents::
   :local:
   :depth: 1

This document provides the complete requirements traceability from Stakeholder
Requirements (SYS.1) through System and Software levels (SYS.2/3, SWE.1/2/3).

----

Stakeholder Requirements (SYS.1)
----------------------------------

All 10 stakeholder requirements — source of the entire requirement chain:

.. needtable::
   :filter: type == "stkh_req"
   :columns: id, title, status, safety_class, verification_method
   :style: table
   :sort: id

----

System Requirements (SYS.2)
------------------------------

20 system requirements, each satisfying at least one stakeholder requirement:

.. needtable::
   :filter: type == "sys_req"
   :columns: id, title, status, satisfies, safety_class
   :style: table
   :sort: id

----

System Architecture (SYS.3)
------------------------------

5 system architecture elements, each deriving from system requirements:

.. needtable::
   :filter: type == "sys_arch"
   :columns: id, title, status, derives_from, safety_class
   :style: table
   :sort: id

----

Software Requirements (SWE.1)
--------------------------------

50 software requirements derived from system requirements:

.. needtable::
   :filter: type == "sw_req"
   :columns: id, title, status, derives_from, traces_to, safety_class
   :style: table
   :sort: id

----

Software Architecture (SWE.2)
--------------------------------

5 software architecture elements refining system architecture:

.. needtable::
   :filter: type == "sw_arch"
   :columns: id, title, status, refines, safety_class
   :style: table
   :sort: id

----

Software Detailed Design (SWE.3)
-----------------------------------

5 detailed design specs refining software architecture:

.. needtable::
   :filter: type == "sw_design"
   :columns: id, title, status, refines, traces_to
   :style: table
   :sort: id

----

Safety-Critical Requirements (ASIL-D)
----------------------------------------

All ASIL-D classified requirements (highest safety level):

.. needtable::
   :filter: safety_class == "ASIL-D"
   :columns: id, title, type, status, verification_method
   :style: table
   :sort: id

----

Requirements by Verification Method
--------------------------------------

Requirements requiring test-based verification:

.. needtable::
   :filter: verification_method == "test"
   :columns: id, title, type, status, safety_class
   :style: table
   :sort: type

Requirements requiring analysis-based verification:

.. needtable::
   :filter: verification_method == "analysis"
   :columns: id, title, type, status, safety_class
   :style: table
   :sort: id

----

Requirement Status Overview
-----------------------------

Approved requirements:

.. needtable::
   :filter: status == "approved"
   :columns: id, title, type, safety_class
   :style: table
   :sort: type

----

Full Requirement Count
-----------------------

+--------------------+-------+
| Requirement Type   | Count |
+====================+=======+
| STKH_REQ           | 10    |
+--------------------+-------+
| SYS_REQ            | 20    |
+--------------------+-------+
| SYS_ARCH           | 5     |
+--------------------+-------+
| SW_REQ             | 50    |
+--------------------+-------+
| SW_ARCH            | 5     |
+--------------------+-------+
| SW_DESIGN          | 5     |
+--------------------+-------+
| **Total**          | **95**|
+--------------------+-------+
