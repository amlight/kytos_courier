API Docs/Usage
==============

The following REST endpoints are available:

1. POST /api/amlight/kytos_courier/slack_send
2. POST /api/amlight/kytos_courier/email_send
3. POST /api/amlight/kytos_courier/notify

The first and second endpoint are from the Slack backend and SMTP, respectively. The third one is meant to be a generic notification REST POST endpoint, which will handle whichever backend is configured and available at the moment.

The following parameters are supported for each of them:

Slack backend
-------------

REST Endpoint
^^^^^^^^^^^^^

.. code:: python

    """REST POST /api/amlight/kytos_courier/slack_send

    The following keys can be used in the json content.
    The 'm_body' is mandatory

    kwargs = {
        'channel': 'general',
        'source': 'source API/NApp',
        'm_body': 'Notification content'
    }

    # 'channel' is the slack channel, by default it's #general
    # 'source' is the NApp username/name or API that fired the event
    # 'm_body' is the str message that will be sent

    """

REST call:

slack_msg.json:

.. code:: json

    {
      "channel": "of_notifications",
      "m_body": "A L2circuit beteewn X and Y was provisioned for customer B"
    }

curl:

.. code:: shell

    curl -X POST -d@slack_msg.json -H "Content-Type: application/json" localhost:8181/api/amlight/kytos_courier/slack_send

.. note::
    localhost is where kytosd is actually running.

KytosEvent
^^^^^^^^^^

If you'd like to use a KytosEvent, this is a simple snippet that you can use on your NApp client:

.. code:: python

    from kytos.core import KytosEvent, KytosNApp
    event = KytosEvent(name='amlight/kytos_courier.slack_send')
    d = {
        'channel': 'general',
        'source': '{0}/{1}'.format(self.username, self.name),
        'm_body': 'Notification content'
    }
    event.content['message'] = d
    self.controller.buffers.app.put(event)


SMTP backend
-------------

REST Endpoint
^^^^^^^^^^^^^

.. code:: python

    """REST POST /api/amlight/kytos_courier/email_send

    The following keys can be used in the json content.
    All of these parameters are mandatory, optionally
    you can set them in the setting.py file as a fallback.

    Your mailserver should be able to relay emails from the
    server where this application is running.

    # 'm_from' sender's email
    # 'm_to' destination's email
    # 'm_subject' email subject
    # 'm_body' email message body

    kwargs = {
        'm_from': 'you@domain.com',
        'm_to': 'to@domain.com',
        'm_subject': 'Notification subject',
        'm_body': 'Notification content'
    }

    """

REST call:

email_msg.json:

.. code:: json

    {
      "m_from": "you@domain.com",
      "m_to": "to@domain.com, to2@domain2.com, to3@domain3.com",
      "m_subject": "Notification subject",
      "m_body": "Notification content"
    }

curl:

.. code:: shell

    curl -X POST -d@slack_msg.json -H "Content-Type: application/json" localhost:8181/api/amlight/kytos_courier/email_send


KytosEvent
^^^^^^^^^^

In the manner, if you'd like to leverage KytosEvent:

.. code:: python

    from kytos.core import KytosEvent, KytosNApp
    event = KytosEvent(name='amlight/kytos_courier.mail_send')
    d = {
        'm_from': 'you@domain.com',
        'm_to': 'to@domain.com, to2@domain2.com, to3@domain3.com',
        'm_subject': 'Notification subject',
        'm_body': 'Notification content',
    }
    event.content['message'] = d
    self.controller.buffers.app.put(event)


Generic backend
---------------

.. code:: python

    """REST POST /api/amlight/kytos_courier/notify

    This generic endpoint will attempt to use either of the
    two configured backends (slacker) or (SMTP). It
    assumes that at least either one of them is configured
    and you just pass the 'm_body' argument.

    kwargs = {
        'm_body': 'Notification content'
    }

    """

The generic backend is only available via a REST request:

generic_msg.json:

.. code:: json

    {
      "m_body": "Notification centent"
    }

curl:

.. code:: shell

    curl -X POST -d@slack_msg.json -H "Content-Type: application/json" localhost:8181/api/amlight/kytos_courier/notify
