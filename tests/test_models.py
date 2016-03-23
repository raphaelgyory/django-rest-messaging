# coding=utf8
# -*- coding: utf8 -*-
# vim: set fileencoding=utf8 :

from __future__ import unicode_literals
from django.db import IntegrityError
from django.utils.timezone import now, timedelta
from django.test import RequestFactory, TestCase
from django.test.utils import override_settings
from rest_messaging.models import Message, Participant, Participation, Thread
from .utils import TestScenario


# callback to check override_settings
def allow_all(request, participant, *args, **kwargs):
    return True


class TestParticipant(TestCase):
    """ We just ensure we can add participants """

    def test_can_add(self):
        Participant.objects.create(id=1)
        self.assertTrue(Participant.objects.get(id=1))
        self.assertRaises(IntegrityError, Participant.objects.create, id=1)


class TestParticipation(TestCase):
    """ We just ensure the object works as expected, no other logic here. """

    def test_can_add(self):
        participant1 = Participant.objects.create(id=1)
        participant2 = Participant.objects.create(id=2)
        thread = Thread.objects.create(name="Title of the thread")
        # we must create the through instance ourself, Django provides no add method
        participation = Participation.objects.create(participant=participant1, thread=thread)
        # we ensure we have defaults values for the dates
        self.assertNotEqual(None, participation.date_joined)
        self.assertEqual(None, participation.date_left)
        Participation.objects.create(participant=participant2, thread=thread)
        # we get it back
        self.assertTrue(all(participant in Thread.objects.get(id=thread.id).participants.all() for participant in [participant1, participant2]))


class TestThread(TestScenario):

    def test_get_threads_for_participant(self):
        # participant 1 participates to all discussions
        with self.assertNumQueries(1):
            threads = Thread.managers.get_threads_for_participant(self.participant1.id)
            threads[0]  # we must unpack the result because query is lazy
        self.assertTrue(all(thread in threads for thread in [self.thread1, self.thread2, self.thread3]))
        # participant 2 participates to 2 discussions
        with self.assertNumQueries(1):
            threads = Thread.managers.get_threads_for_participant(self.participant2.id)
            threads[0]  # we must unpack the result because query is lazy
        self.assertTrue(all(thread in threads for thread in [self.thread1, self.thread2]))
        # participant 3 participates to all the discussions, even if he left one
        with self.assertNumQueries(1):
            threads = Thread.managers.get_threads_for_participant(self.participant3.id)
            threads[0]  # we must unpack the result because query is lazy
        self.assertTrue(all(thread in threads for thread in [self.thread1, self.thread2, self.thread3]))

    def test_get_threads_where_participant_is_active(self):
        # participant 1 is active in thread 1, 2 and 3
        with self.assertNumQueries(2):
            threads = Thread.managers.get_threads_where_participant_is_active(self.participant1.id)
            self.assertEqual(set([self.thread1, self.thread2, self.thread3]), set(threads))  # ordering is indifferent
            self.assertEqual(3, len(threads))
        # participant 1 leave thread 1
        self.participation1.date_left = now()
        self.participation1.save()
        with self.assertNumQueries(2):
            threads = Thread.managers.get_threads_where_participant_is_active(self.participant1.id)
            self.assertEqual(set([self.thread2, self.thread3]), set(threads))  # ordering is indifferent
            self.assertEqual(2, len(threads))

    def test_get_active_threads_involving_all_participants(self):
        # there is an active thread with participants 1, 2 and 3
        with self.assertNumQueries(1):
            threads1 = Thread.managers.get_active_threads_involving_all_participants(self.participant1.id, self.participant2.id, self.participant3.id)
            self.assertEqual(1, threads1.count())
        # there is NO active thread with ONLY participants 1 and 2 (3 left)
        with self.assertNumQueries(1):
            threads2 = Thread.managers.get_active_threads_involving_all_participants(self.participant1.id, self.participant2.id)
            self.assertEqual(0, threads2.count())
        # there is an active thread with participants 1 and 3
        with self.assertNumQueries(1):
            threads3 = Thread.managers.get_active_threads_involving_all_participants(self.participant1.id, self.participant3.id)
            self.assertEqual(1, threads3.count())
        # we create another thread with all users in
        thread4 = Thread.objects.create(name="All in nr 2!")
        Participation.objects.create(participant=self.participant1, thread=thread4)
        Participation.objects.create(participant=self.participant2, thread=thread4)
        Participation.objects.create(participant=self.participant3, thread=thread4)
        with self.assertNumQueries(1):
            threads4 = Thread.managers.get_active_threads_involving_all_participants(self.participant1.id, self.participant2.id, self.participant3.id)
            self.assertEqual(2, threads4.count())

    def test_get_or_create_thread_unique(self):
        # we set rest_messaging_participant, which is normally done in the middleware
        setattr(self.request_authenticated, "rest_messaging_participant", self.participant1)
        # by default, threads are unique
        # if we ask the Thread for Participant 1, 2 and 3, we get self.thread1
        with self.assertNumQueries(1):
            thread = Thread.managers.get_or_create_thread(self.request_authenticated, None, self.participant1.id, self.participant2.id, self.participant3.id)
        self.assertEqual(thread.id, self.thread1.id)
        # if we ask the Thread for Participant 1 and 2, we get a new Thread because user 3 was in self.thread2
        with self.assertNumQueries(4):
            thread_new = Thread.managers.get_or_create_thread(self.request_authenticated, None, self.participant1.id, self.participant2.id)
        self.assertNotEqual(thread_new.id, self.thread2.id)
        self.assertEqual(thread_new.id, Thread.objects.latest('id').id)
        # if we open a Thread for Participant 1 and 4 (not existing yet, we simply get a new one)
        with self.assertNumQueries(4):
            thread_new2 = Thread.managers.get_or_create_thread(self.request_authenticated, None, self.participant1.id, self.participant4.id)
        self.assertEqual(thread_new2.id, Thread.objects.latest('id').id)

    @override_settings(REST_MESSAGING_THREAD_UNIQUE_FOR_ACTIVE_RECIPIENTS=False)
    def test_get_or_create_thread_multiple(self):
        # we set rest_messaging_participant, which is normally done in the middleware
        setattr(self.request_authenticated, "rest_messaging_participant", self.participant1)
        # we get the same as above but do not re-attach to older Thread instances
        with self.assertNumQueries(3):
            thread = Thread.managers.get_or_create_thread(self.request_authenticated, None, self.participant1.id, self.participant2.id, self.participant3.id)
        self.assertNotEqual(thread.id, self.thread1.id)
        self.assertEqual(thread.id, Thread.objects.latest('id').id)

    def test_get_or_create_thread_one_participant(self):
        # we set rest_messaging_participant, which is normally done in the middleware
        setattr(self.request_authenticated, "rest_messaging_participant", self.participant1)
        # more than one participant is required, we raise an error
        self.assertRaises(Exception, Thread.managers.get_or_create_thread, self.request_authenticated, None, self.participant1.id)

    def test_add_participants(self):
        # by default, a user will be authorized to add a participant if they are not yet in the thread
        # we add new and existing participants
        request = RequestFactory()
        request.user = self.user
        request.rest_messaging_participant = Participant.objects.get(id=self.user.id)
        self.assertTrue(all(participant in [self.participant1, self.participant2, self.participant3] for participant in self.thread1.participants.all()))
        self.assertEqual(3, len(self.thread1.participants.all()))
        with self.assertNumQueries(2):
            self.thread1.add_participants(request, self.participant4.id, self.participant5.id)
        self.assertTrue(all(participant in [self.participant1, self.participant2, self.participant3, self.participant4, self.participant5] for participant in self.thread1.participants.all()))
        self.assertEqual(5, len(self.thread1.participants.all()))
        # by default, the number of participants is limited to 10
        l = []
        for i in range(7, 16):  # setUp ends at 6
            l.append(Participant(id=i))
        Participant.objects.bulk_create(l)
        self.thread1.add_participants(request, *[p.id for p in l])
        self.assertEqual(10, len(self.thread1.participants.all()))

    @override_settings(REST_MESSAGING_ADD_PARTICIPANTS_CALLBACK=lambda *args: [])
    def test_add_participants_callback(self):
        # this can be overriden
        request = RequestFactory()
        request.user = self.user
        request.rest_messaging_participant = Participant.objects.get(id=self.user.id)
        self.assertTrue(all(participant in [self.participant1, self.participant2, self.participant3] for participant in self.thread1.participants.all()))
        self.assertEqual(3, len(self.thread1.participants.all()))
        self.thread1.add_participants(request, self.participant4, self.participant5)
        # the count did not change
        self.assertEqual(3, len(self.thread1.participants.all()))

    def remove_participant(self):
        # we need a request to use request.user
        # by default, a user will be authorized to add a participant if he himself is a participant
        request = RequestFactory()
        request.user = self.user
        # user 1 cannot remove another participant
        self.assertRaises(Exception, self.thread1.remove_participant, request, self.participant2)
        # he can remove himself
        self.assertTrue(self.participant1 in self.thread1.participants.all())
        self.assertTrue(self.thread1.remove_participant(request, self.participant1))
        self.assertFalse(self.participant1 in self.thread1.participants.all())

    @override_settings(REST_MESSAGING_REMOVE_PARTICIPANTS_CALLBACK=lambda *args: True)
    def remove_participant_callback(self):
        # this can be overriden by the settings
        request = RequestFactory()
        request.user = self.participant1
        self.assertTrue(self.participant2 in self.thread1.participants.all())
        self.assertTrue(self.thread1.remove_participant(request, self.participant2))
        self.assertFalse(self.participant2 in self.thread1.participants.all())


class TestMessage(TestScenario):

    def test_no_daily_messages_limit(self):
        count_already_created = Message.objects.filter(sender=self.participant1).count()
        r = 100
        for i in range(r):
            Message.objects.create(sender=self.participant1, thread=self.thread1, body="hi")
        # we have more than 50 messages (more in setUp)
        self.assertEqual(r + count_already_created, Message.objects.filter(sender=self.participant1).count())

    @override_settings(REST_MESSAGING_DAILY_LIMIT_CALLBACK=lambda *args, **kwargs: 50)
    def test_check_callback_and_save(self):
        # we ensure a user may by default not send more than 50 messages a day
        Message.objects.filter(sender=self.participant1).count()
        r = 100
        for i in range(r):
            try:
                m = Message(sender=self.participant1, thread=self.thread1, body="hi")
                m.save()
            except Exception:
                pass
        # we have more than 50 messages (more in setUp)
        self.assertEqual(50, Message.objects.filter(sender=self.participant1).count())
        # the limit is only in the last 24 hours
        Message.objects.filter(sender=self.participant1).update(sent_at=now() - timedelta(days=1, seconds=1))
        last = Message.objects.filter(sender=self.participant1).latest('id')
        new = Message.objects.create(sender=self.participant1, thread=self.thread1, body="hi")
        self.assertEqual(new.id, last.id + 1)

    def test_get_lasts_messages_of_threads(self):
        with self.assertNumQueries(4):
            messages = Message.managers.get_lasts_messages_of_threads(self.participant1.id, check_who_read=False, check_is_notification=False)
            # the messages are ordered from most recent to older
            self.assertEqual([self.m33.id, self.m22.id, self.m11.id], [m.id for m in messages])
            # we ensure we get the related information without triggering more queries
            messages[0].thread.name
            messages[0].thread.participants.all()
            for participant in messages[0].thread.participants.all():
                participant.id
            messages[1].thread.participants.all()
            messages[2].thread.participants.all()

    def test_get_lasts_messages_of_threads_check_who_read(self):
        # participant 1 and 2 have read the messages, 3 no
        self.participation1.date_last_check = now() + timedelta(days=1)
        self.participation1.save()
        self.participation2.date_last_check = now() + timedelta(days=1)
        self.participation2.save()
        # we do not modify self.participation3.date_last_check
        # this means participant 1 and 2 have read the message, not 3
        with self.assertNumQueries(5):
            messages = Message.managers.get_lasts_messages_of_threads(self.participant1.id, check_who_read=True, check_is_notification=False)
            # the ordering has not been modified
            self.assertEqual([self.m33.id, self.m22.id, self.m11.id], [m.id for m in messages])
            # participant 1 and 2 have read Thread 1
            self.assertTrue(self.participant1.id in messages[2].readers)
            self.assertTrue(self.participant2.id in messages[2].readers)
            self.assertFalse(self.participant3.id in messages[0].readers)

    def test_get_lasts_messages_of_threads_check_is_notification(self):
        with self.assertNumQueries(5):
            messages = Message.managers.get_lasts_messages_of_threads(self.participant1.id, check_who_read=False, check_is_notification=True)
            # the ordering has not been modified
            self.assertEqual([self.m33.id, self.m22.id, self.m11.id], [m.id for m in messages])
            # the second conversation has no notification because last reply comes from the current participant
            self.assertEqual(messages[1].is_notification, False)
            # the third (first in ordering) conversation has new messages
            self.assertEqual(messages[0].is_notification, True)

    def test_get_lasts_messages_of_threads_check_is_notification_check_who_read(self):
        # participant 1 and 2 have read the messages, 3 no
        self.participation1.date_last_check = now() + timedelta(days=1)
        self.participation1.save()
        self.participation2.date_last_check = now() + timedelta(days=1)
        self.participation2.save()
        # we create a notification check
        with self.assertNumQueries(6):
            messages = Message.managers.get_lasts_messages_of_threads(self.participant1.id, check_who_read=True, check_is_notification=True)
            # the ordering has not been modified
            self.assertEqual([self.m33.id, self.m22.id, self.m11.id], [m.id for m in messages])
            # the second conversation has no notification because last reply comes from the current participant
            self.assertEqual(messages[1].is_notification, False)
            # the third (first in ordering) conversation has new messages
            self.assertEqual(messages[0].is_notification, True)
            # participant 1 and 2 have read Thread 1
            self.assertTrue(self.participant1.id in messages[2].readers)

    def test_get_all_messages_in_thread(self):
        # we change the date of the messages
        self.m31.sent_at = self.p2.date_last_check = now() - timedelta(days=3)
        self.m31.save()
        self.m32.sent_at = self.p2.date_last_check = now() - timedelta(days=1, hours=12)
        self.m32.save()
        # we get all the messages
        with self.assertNumQueries(3):
            messages = Message.managers.get_all_messages_in_thread(self.participant1.id, self.thread3.id)
            self.assertEqual([self.m33.id, self.m32.id, self.m31.id], [m.id for m in messages])
            self.assertEqual(set(messages[2].readers), set([self.participant1.id, self.participant3.id]))  # we do not care about the order of the readers
            self.assertEqual(messages[1].readers, [self.participant3.id])
            self.assertEqual(messages[0].readers, [])
