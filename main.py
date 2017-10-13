#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import requests
import smtplib
from email.mime.text import MIMEText
from flask import request, Response
from kytos.core import KytosNApp, log, rest
from kytos.core.helpers import listen_to
from napps.amlight.kytos_courier import settings


class Main(KytosNApp):
    """Kytos NApp"""

    def setup(self):
        """ Init

        """
        self.has_failed = False
        try:
            from slacker import Slacker, Error
            self.slack = Slacker(settings.slack_token)
            self.slack_error = Error
        except ImportError:
            self.has_failed = True
            log.error(
                "Package slacker inst't installed. Please, pip install slacker"
            )

    def execute(self):
        """This NApp is event-oriented"""

        # Token settings, auto shutdown.
        if self.has_failed:
            log.error("kytos courier will shut down! Fix the dependency first")
            self.controller.unload_napp(self.username, self.name)

    def _parse_str(self, str1, msg):
        """ Check if msg is a string and concatenate to str1

        :str1: base string
        :msg: string to be concatenated
        :returns: str1 + msg

        """
        if isinstance(msg, str):
            return str1 + " " + msg
        # Otherwise just return the base string
        return str1

    @rest('slack_send', methods=['POST'])
    def rest_slack_send(self, **kwargs):
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
        try:
            content = request.get_json()
            self._slack_send(**content)
            return Response(response=json.dumps(content), status=200)
        except ValueError:
            return Response(
                response=json.dumps({
                    "error": "Missing the 'm_body' argument"
                }),
                status=406)
        except self.slack_error as e:
            return Response(response=json.dumps({"error": str(e)}), status=400)
        except requests.exceptions.ConnectionError:
            return Response(
                response=json.dumps({
                    "error": "ConnectionError to Slack API"
                }),
                status=400)

    @rest('email_send', methods=['POST'])
    def rest_email_send(self):
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
        try:
            content = request.get_json()
            self._email_send(**content)
            return Response(response=json.dumps(content), status=200)
        except smtplib.SMTPException as e:
            log.error(str(e))
            return Response(str(e), status=400)

    @rest('notify', methods=['POST'])
    def rest_notify(self):
        """REST POST /api/amlight/kytos_courier/notify

        This generic endpoint will attempt to use either of the
        two configured backends (slacker) or (email). It
        assumes that at least either one of them is configured
        and you just pass the 'm_body' argument.

        kwargs = {
            'm_body': 'Notification content'
        }

        """
        if settings.slack_token:
            resp = self.rest_slack_send()
            if resp.status_code == 200:
                # request was successful return immediately.
                return resp
        # fallback to the next backend
        if settings.m_server_fqdn:
            return self.rest_email_send()

    def _slack_send(self, **kwargs):
        """
        Send some key value pairs via slacker
        """
        try:
            # if settings wasn't properly setup in the first place
            if not self.has_failed:
                if not kwargs.get('m_body'):
                    err = "Missing the 'm_body' argument"
                    log.error(err)
                    raise ValueError(err)
                slack_msg = ""
                for k in ['source', 'm_body']:
                    slack_msg = self._parse_str(slack_msg, kwargs.get(k))
                # fallback to #general
                ch = ''
                if kwargs.get('channel'):
                    ch = kwargs.get('channel')
                elif settings.slack_channel:
                    ch = settings.slack_channel
                else:
                    ch = 'general'

                log.info('channel:{0} msg:{1}'.format(ch, slack_msg))
                self.slack.chat.post_message(ch, slack_msg)
        except requests.exceptions.ConnectionError:
            err = "ConnectionError to Slack API."
            log.error(err)
            raise
        except self.slack_error as e:
            log.error(str(e))
            raise

    def _email_send(self, **kwargs):
        """
        Send an email through SMTP
        """
        try:

            d = {
                'm_from': settings.m_from,
                'm_to': settings.m_to,
                'm_subject': settings.m_subject,
                'm_body': settings.m_body,
                'm_server_fqdn': settings.m_server_fqdn,
                'm_server_port': settings.m_server_port
            }

            # overrides global setting values
            for k, v in kwargs.items():
                d[k] = v

            msg = MIMEText(d['m_body'])
            msg['Subject'] = d['m_subject']
            msg['From'] = d['m_from']
            msg['To'] = d['m_to']

            s = smtplib.SMTP(host=d['m_server_fqdn'], port=d['m_server_port'])
            # m_to has to be a list in case of multiple destinations
            s.sendmail(d['m_from'], d['m_to'].split(", "), msg.as_string())
            s.quit()
            log.info('An email was sent to: {0}'.format(d['m_to']))

        except smtplib.SMTPException as e:
            log.error(str(e))
            raise

    @listen_to('amlight/kytos_courier.slack_send')
    def kytos_event_slack_send(self, event):
        """Listen to KytosEvent 'amlight/kytos_courier.slack_send' parse it
        and send it via slacker

        :event: KytosEvent

        Here's a simple snippet to send a event and the expected dict keys:
        The 'm_body' is mandatory

        event = KytosEvent(name='amlight/kytos_courier.slack_send')
        d = {
            'channel': 'general',
            'source': '{0}/{1}'.format(self.username, self.name),
            'm_body': 'Notification content'
        }
        event.content['message'] = d
        self.controller.buffers.app.put(event)

        # 'channel' is the slack channel, by default it's #general
        # 'source' is the NApp username/name that fired the event
        # 'm_body' is the str message that will be sent

        """
        self._slack_send(event.content.get('message'))

    @listen_to('amlight/kytos_courier.mail_send')
    def kytos_event_email_send(self, event):
        """Listen to KytosEvent 'amlight/kytos_courier.mail_send' parse it
        and send it via SMTP

        :event: KytosEvent

        Snippet:

        event = KytosEvent(name='amlight/kytos_courier.mail_send')
        d = {
            'm_from': 'you@domain.com',
            'm_to': 'to@domain.com, to2@domain2.com, to3@domain3.com',
            'm_subject': 'Notification subject',
            'm_body': 'Notification content',
        }
        event.content['message'] = d
        self.controller.buffers.app.put(event)

        """
        self._email_send(event.content.get('message'))

    def shutdown(self):
        log.info("amlight/kytos_courier is gone!")
