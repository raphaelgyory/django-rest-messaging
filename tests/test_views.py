# coding=utf8
# -*- coding: utf8 -*-
# vim: set fileencoding=utf8 :

from __future__ import unicode_literals

from django.test.utils import override_settings
from django.utils.timezone import now, timedelta

from rest_framework.reverse import reverse

from rest_messaging.models import Message, NotificationCheck, Participation, Thread

from .utils import TestScenario, parse_json_response


class ThreadViewTests(TestScenario):

    def setUp(self):
        super(ThreadViewTests, self).setUp()
        self.url = reverse('rest_messaging:threads-list')

    def test_retrieve(self):
        # no authentication
        response = self.client_unauthenticated.get("{0}{1}/".format(self.url, self.thread1.id))
        self.assertEqual(403, response.status_code)
        # no permission
        response = self.client_authenticated.get("{0}{1}/".format(self.url, self.thread_unrelated.id))
        self.assertEqual(403, response.status_code)
        # ok
        response = self.client_authenticated.get("{0}{1}/".format(self.url, self.thread1.id))
        self.assertEqual(200, response.status_code)
        self.assertEqual(set(parse_json_response(response.data)["participants"]), set([self.participant1.id, self.participant2.id, self.participant3.id]))  # we do not care about ordering

    @override_settings(REST_MESSAGING_SERIALIZE_PARTICIPANTS_CALLBACK=lambda *args, **kwargs: ["a", "b", "c"])
    def test_retrieve_callback(self):
        # we try with a callback (full callback is tested in TestThreadSerializer, here we only test override_settings)
        response = self.client_authenticated.get("{0}{1}/".format(self.url, self.thread1.id))
        self.assertEqual(parse_json_response(response.data)["participants"], ["a", "b", "c"])

    def test_list(self):
        # not implemented
        response = self.client_unauthenticated.get(self.url)
        self.assertEqual(403, response.status_code)
        response = self.client_authenticated.get(self.url)
        self.assertEqual(405, response.status_code)

    def test_create(self):
        data = {"name": "Thread name", "participants": [self.participant3.id, self.participant5.id]}  # self.participant1.id  will be added automatically since he is requets.user
        response = self.client_unauthenticated.post(self.url)
        self.assertEqual(403, response.status_code)
        # we ensure a new thread is created
        last_thread = Thread.objects.latest('id')
        response = self.client_authenticated.post(self.url, data=data)
        self.assertEqual(201, response.status_code)
        # the users have been added to the serializer
        expected = dict({"name": "Thread name", "participants": [self.participant1.id, self.participant3.id, self.participant5.id], "id": Thread.objects.latest('id').id})
        self.assertEqual(parse_json_response(response.data)["name"], expected["name"])
        self.assertEqual(parse_json_response(response.data)["id"], expected["id"])
        self.assertEqual(set(parse_json_response(response.data)["participants"]), set(expected["participants"]))  # we do not acre about the order
        # the thread has been created
        new_thread = Thread.objects.latest('id')
        self.assertNotEqual(last_thread.id, new_thread.id)
        # we repost with the same participants
        # this time a new thread should not be created
        response = self.client_authenticated.post(self.url, data=data)
        self.assertEqual(201, response.status_code)
        self.assertEqual(new_thread.id, Thread.objects.latest('id').id)

    def test_update(self):
        # no authentication
        response = self.client_unauthenticated.delete(self.url)
        self.assertEqual(403, response.status_code)
        # no permission
        response = self.client_authenticated.put("{0}{1}/".format(self.url, self.thread_unrelated.id), data={})
        self.assertEqual(403, response.status_code)
        # only the name can be updated directly, not the participants (ManyToMany)
        data = {"name": "New thread name"}
        response = self.client_authenticated.put("{0}{1}/".format(self.url, self.thread1.id), data=data)
        self.assertEqual(200, response.status_code)
        # the name has been updated
        self.assertEqual(data["name"], Thread.objects.get(id=self.thread1.id).name)
        # posting participants is not allowed
        data = {"name": "Another thread name", "participants": [self.participant1.id, self.participant3.id, self.participant5.id]}
        response = self.client_authenticated.put("{0}{1}/".format(self.url, self.thread1.id), data=data)
        self.assertEqual(400, response.status_code)

    def test_delete(self):
        response = self.client_unauthenticated.delete(self.url)
        self.assertEqual(403, response.status_code)
        response = self.client_authenticated.delete(self.url)
        self.assertEqual(405, response.status_code)

    def test_add_participants(self):
        # no authentication
        response = self.client_unauthenticated.post("{0}{1}/add_participants/".format(self.url, self.thread1.id), data={})
        self.assertEqual(403, response.status_code)
        # no permission
        response = self.client_authenticated.post("{0}{1}/add_participants/".format(self.url, self.thread_unrelated.id), data={})
        self.assertEqual(403, response.status_code)
        # ok
        data = {"participants": [self.participant1.id, self.participant3.id, self.participant5.id]}
        response = self.client_authenticated.post("{0}{1}/add_participants/".format(self.url, self.thread1.id), data=data)
        self.assertEqual(200, response.status_code)
        parsed = parse_json_response(response.data)
        self.assertEqual(set(parsed["participants"]), set([self.participant1.id, self.participant2.id, self.participant3.id, self.participant5.id]))
        self.assertEqual(parsed["name"], self.thread1.name)

    def test_remove_participant(self):
        # no authentication
        response = self.client_unauthenticated.post("{0}{1}/remove_participant/".format(self.url, self.thread1.id), data={})
        self.assertEqual(403, response.status_code)
        # no permission
        response = self.client_authenticated.post("{0}{1}/remove_participant/".format(self.url, self.thread_unrelated.id), data={})
        self.assertEqual(403, response.status_code)
        # may not remove another one excepted if the callback says so
        response = self.client_authenticated.post("{0}{1}/remove_participant/".format(self.url, self.thread1.id), data={"participant": self.participant2.id})
        self.assertEqual(400, response.status_code)
        # ok
        # we fisrt ensure participant 1 is active
        p = Participation.objects.get(participant=self.participant1, thread=self.thread1)
        self.assertEqual(p.date_left, None)
        # we will remove him
        response = self.client_authenticated.post("{0}{1}/remove_participant/".format(self.url, self.thread1.id), data={"participant": self.participant1.id})
        self.assertEqual(200, response.status_code)
        parsed = parse_json_response(response.data)
        # we get the Thread
        self.assertEqual(parsed["name"], self.thread1.name)
        # participant 1 is still there ...
        self.assertEqual(set(parsed["participants"]), set([self.participant1.id, self.participant2.id, self.participant3.id]))
        # ... but he has left
        p = Participation.objects.get(participant=self.participant1, thread=self.thread1)
        self.assertNotEqual(p.date_left, None)


class MessageViewTests(TestScenario):

    def setUp(self):
        super(MessageViewTests, self).setUp()
        self.url = reverse('rest_messaging:messages-list')

    def test_get_queryset(self):
        # no authentication
        response = self.client_unauthenticated.get(self.url)
        self.assertEqual(403, response.status_code)
        # ok
        # participant 3 has read the 2 last messages, 1 only the first
        p1 = Participation.objects.create(participant=self.participant3, thread=self.thread3)
        p1.date_last_check = now() - timedelta(days=1)
        p1.save()
        p2 = Participation.objects.create(participant=self.participant1, thread=self.thread3)
        p2.date_last_check = now() - timedelta(days=2)
        p2.save()
        response = self.client_authenticated.get(self.url)
        self.assertEqual(200, response.status_code)
        messages_dct = parse_json_response(response.data)
        messages = messages_dct["results"]
        self.assertEqual(3, len(messages))
        self.assertEqual(messages[0]["id"], self.m33.id)
        self.assertEqual(messages[1]["id"], self.m22.id)
        self.assertEqual(messages[2]["id"], self.m11.id)
        self.assertEqual([], messages[0]["readers"])
        self.assertEqual(messages[0]["is_notification"], True)  # not read
        self.assertEqual(messages[1]["is_notification"], False)  # because written by the user himself
        self.assertEqual(messages[2]["is_notification"], False)  # because written by the user himself

    def test_post_message(self):
        # no authentication
        response = self.client_unauthenticated.post("{0}{1}/post_message/".format(self.url, self.thread1.id), data={})
        self.assertEqual(403, response.status_code)
        # no permission
        response = self.client_authenticated.post("{0}{1}/post_message/".format(self.url, self.thread_unrelated.id), data={})
        self.assertEqual(403, response.status_code)
        # ok
        body = "New message!"
        response = self.client_authenticated.post("{0}{1}/post_message/".format(self.url, self.thread1.id), data={"body": body})
        self.assertEqual(201, response.status_code)
        parsed = parse_json_response(response.data)
        last_message = Message.objects.latest('id')
        self.assertEqual(parsed["id"], last_message.id)
        self.assertTrue(parsed["body"] == last_message.body == body)
        self.assertEqual(parsed["sender"], self.participant1.id)

    def test_list_messages_in_thread(self):
        # no authentication
        response = self.client_unauthenticated.get("{0}{1}/list_messages_in_thread/".format(self.url, self.thread1.id))
        self.assertEqual(403, response.status_code)
        # no permission
        response = self.client_authenticated.get("{0}{1}/list_messages_in_thread/".format(self.url, self.thread_unrelated.id))
        self.assertEqual(403, response.status_code)
        # ok
        # participant 3 has read the 2 last messages, 1 only the first
        p1 = Participation.objects.create(participant=self.participant3, thread=self.thread3)
        p1.date_last_check = now() - timedelta(days=1)
        p1.save()
        p2 = Participation.objects.create(participant=self.participant1, thread=self.thread3)
        p2.date_last_check = now() - timedelta(days=2)
        p2.save()
        # we change the date of the messages
        self.m31.sent_at = p1.date_last_check = now() - timedelta(days=3)
        self.m31.save()
        self.m32.sent_at = p1.date_last_check = now() - timedelta(days=1, hours=12)
        self.m32.save()
        response = self.client_authenticated.get("{0}{1}/list_messages_in_thread/".format(self.url, self.thread3.id))
        messages_dct = parse_json_response(response.data)
        messages = messages_dct["results"]
        self.assertEqual([self.m33.id, self.m32.id, self.m31.id], [m["id"] for m in messages])
        self.assertEqual([set([]), set([self.participant3.id]), set([self.participant1.id, self.participant3.id])], [set(m["readers"]) for m in messages])


class TestMessageNotificationCheckView(TestScenario):

    def setUp(self):
        super(TestMessageNotificationCheckView, self).setUp()
        self.url = reverse('rest_messaging:notifications-list')

    def test_check(self):
        # no authentication
        response = self.client_unauthenticated.post("{0}check/".format(self.url), data={})
        self.assertEqual(403, response.status_code)
        # participant 1 already has a check, it will be updated
        response = self.client_authenticated.post("{0}check/".format(self.url), data={})
        self.assertEqual(200, response.status_code)
        reload_notification_check = NotificationCheck.objects.get(participant=self.participant1)
        self.assertEqual(reload_notification_check.id, self.notification_check.id)
        self.assertTrue(reload_notification_check.date_check > self.notification_check.date_check)
