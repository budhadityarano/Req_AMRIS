.. _abs_requirements_home:

ABS Requirements Specification - ASPICE
=========================================

Welcome to the **Anti-Lock Braking System (ABS)** requirements specification, structured
according to the **ASPICE (Automotive SPICE)** process model.

This documentation covers the **left side of the V-model**: from Stakeholder Requirements
through System Architecture down to Software Detailed Design.

.. toctree::
   :maxdepth: 2
   :caption: System Engineering (SYS)
   :numbered:

   SYS1/index
   SYS2/index
   SYS3/index

.. toctree::
   :maxdepth: 2
   :caption: Software Engineering (SWE)
   :numbered:

   SWE1/index
   SWE2/index
   SWE3/index

.. toctree::
   :maxdepth: 1
   :caption: Traceability & Reports

   traceability/index

.. toctree::
   :maxdepth: 1
   :caption: Future Scope

   future_scope/index

----

ASPICE V-Model Coverage
------------------------

+----------------+-----------------------------------+----------------------------+--------+
| Process Area   | Description                       | Work Products              | Count  |
+================+===================================+============================+========+
| **SYS.1**      | Stakeholder Requirements Analysis | Stakeholder Requirements   | 10     |
+----------------+-----------------------------------+----------------------------+--------+
| **SYS.2**      | System Requirements Analysis      | System Requirements (SRS)  | 20     |
+----------------+-----------------------------------+----------------------------+--------+
| **SYS.3**      | System Architectural Design       | System Architecture Spec   | 5      |
+----------------+-----------------------------------+----------------------------+--------+
| **SWE.1**      | Software Requirements Analysis    | Software Requirements (SRS)| 50     |
+----------------+-----------------------------------+----------------------------+--------+
| **SWE.2**      | Software Architectural Design     | SW Architecture Spec       | 5      |
+----------------+-----------------------------------+----------------------------+--------+
| **SWE.3**      | Software Detailed Design          | Detailed Design Spec       | 5      |
+----------------+-----------------------------------+----------------------------+--------+

Requirement Traceability Chain
--------------------------------

.. code-block:: text

   [SYS.1] STKH_REQ
       │
       └──[satisfies]──► [SYS.2] SYS_REQ
                              │
                              ├──[derives_from]──► [SYS.3] SYS_ARCH
                              │
                              └──[derives_from]──► [SWE.1] SW_REQ
                                                        │
                                                        └──[traces_to]──► [SWE.2] SW_ARCH
                                                                               │
                                                                               └──[refines]──► [SWE.3] SW_DESIGN

All Needs Overview
-------------------

.. needtable::
   :columns: id, title, type, status
   :style: datatables
   :sort: type
