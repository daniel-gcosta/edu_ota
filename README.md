# edu_ota
An Secure OTA Approach For Flexible Operation of Emergency Detection Units in Smart Cities

The growth of the urban population in recent decades has revealed increasingly serious structural problems in urban environments. These problems may ultimately lead to emergency events associated with danger and negative impacts on life, health, city structures, and the environment. In order to effectively manage various emergency situations, technological strategies are required to address the challenges posed by the heterogeneity and dynamism of urban centers. This repository presents an Over-the-Air (OTA) approach for the flexible operation of emergency detection units in Smart Cities through remote updates. The proposed approach focuses on ensuring security, reliability, and adaptability in the software updates of IoT-based emergency detection units.

This repository is divided in two files for two distinct proposed elements: an EDU and an Update Server. These Python 3 files allow secure update of an EDU, adapting it to a new configuration setting. Actually, although the proposed architecture is more complex and define operation details for multiple situations, the code here is an initial proof-of-concept implementation that attest that the proposed approach works as expected.

In order to allow flexible reconfiguration procedures, a user can specify the intended new configuration through a builtin functionality in the developed Update Server. This way, the path of a file containing the desired update of the EDU is requested through a specific input present in the server.

Additional information can be requested through the email gustavo.falcao@ifba.edu.br.
