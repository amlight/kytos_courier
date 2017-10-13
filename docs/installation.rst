Installation
============

First, you need kytos SDN platform up and running:

.. code:: shell

   kytosd -f

1. Install kytos_courier:

.. code:: shell

   kytos napps install amlight/kytos_courier

2. Install slacker dependency (make sure pip points to pip3.6, i.e., you are working in a Python 3.6 virtualenv):

.. code:: shell

   pip install slacker

3. Enable kytos_courier:

.. code:: shell

   kytos napps enable amlight/kytos_courier
