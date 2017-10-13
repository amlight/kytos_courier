Introduction
============

.. image:: images/kytos_courier.png
   :align: center

kytos_courier is a NApp for generating network event notifications either via Slack or email (SMTP) that runs on top of Kytos SDN Platform. You have the option to use both backends, Slack and/or email, or just one of them. For each backend kytos_courier exposes both a REST API and also a KytosEvent interface. Consequently, this facilitates the integration with external systems/third party APIs and also other Kytos NApps that generate events.

Use Cases
---------

kytos_courier is designed to be a generic notification abstraction that leverages multiple notification backends for generating networking events. Some of the potential use cases include:

- Informational notifications about new network circuits. For example, a specific circuit was just provisioned for a certain customer.
- Critical notifications about some OpenFlow messages such as port stats events.
- Integration with event-driven automation (Roadmap).

Contact
-------

If you have any questions, or suggestion about features, you can reach AmLight development team at dev@amlight.net

.. image:: images/amlight_logo.png
   :align: center
