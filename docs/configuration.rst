Configuration
=============

For all backends you have to set certain parameters in the settins.py file in order to configure them. Optionally, in the settings.py also there are some global fallback variables that you can leverage if that suits your use case. Otherwise, if you prefer a more granular approach, there is always a way to specify specific parameters either via a REST call or KytosEvent for each event.

Slack backend
-------------

Slack backend is just a wrapper around the slacker package. You have to configure the Slack API authentication token in the settings.py:

.. code:: python

   slack_token = "xo..."

.. note::
   If you don't have a Slack bot yet, you should visit `Slack Bot documentation <https://my.slack.com/services/new/bot>`_ and create a authentication token.

Optionally, you can set a global fallback slack channel:

.. code:: python

   slack_channel = "my_slack_channel..."


SMTP backend
------------

To configure the SMTP backend you need to specify both the FQDN (hostname) and the SMTP port in the settings.py:

.. code:: python

   m_server_fqdn = "your_SMTP_server_fqdn"
   m_server_port = 25

.. note::
   The SMTP server is supposed to authorize relay from the server where this NApps is running. There's no specific credentials supported at the moment. You should adjust this configuration accordingly in your mail domain. If you don't run a SMTP server it is recommended that you stick with only the Slack backend instead.

These are the global fallback parameters available in the settins.py:

.. code:: python

   m_from = "from@domain.com"  # str
   m_to = "to@domain.com"  # str
   m_subject = "Critical networking event"  # subject str
   m_body = "Look, bad news.."  # body str

.. note::
   It's possible to add multiple email recipients, you just have to separate each address by a comma a space. It should be a single str, for an example of this configuration, look in the API endpoints section of this documentation.
