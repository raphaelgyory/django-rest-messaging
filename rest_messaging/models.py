# coding=utf8
# -*- coding: utf8 -*-
# vim: set fileencoding=utf8 :

from __future__ import unicode_literals
from django.conf import settings
from django.db import models
from django.db.models import Count, Max
from django.db.models.signals import post_save, pre_save
from django.utils.encoding import python_2_unicode_compatible
from django.utils.timezone import now, timedelta


@python_2_unicode_compatible
class Participant(models.Model):
    """
    The participant model holds a django.contrib.auth.models.User's id.
    This allows us to use rest_messaging without querying the main db.
    """
    id = models.PositiveIntegerField(primary_key=True)

    def __str__(self):
        return "{0}".format(self.id)


class ThreadManager(models.Manager):

    def get_threads_for_participant(self, participant_id):
        """ Gets all the threads in which the current participant is or was involved. The method does not exclude threads where the participant has left. """
        return Thread.objects.\
            filter(participants__id=participant_id).\
            distinct()

    def get_threads_where_participant_is_active(self, participant_id):
        """ Gets all the threads in which the current participant is involved. The method excludes threads where the participant has left. """
        participations = Participation.objects.\
            filter(participant__id=participant_id).\
            exclude(date_left__lte=now()).\
            distinct().\
            select_related('thread')

        return Thread.objects.\
            filter(id__in=[p.thread.id for p in participations]).\
            distinct()

    def get_active_threads_involving_all_participants(self, *participant_ids):
        """ Gets the threads where the specified participants are active and no one has left. """

        query = Thread.objects.\
            exclude(participation__date_left__lte=now()).\
            annotate(count_participants=Count('participants')).\
            filter(count_participants=len(participant_ids))

        for participant_id in participant_ids:
            query = query.filter(participants__id=participant_id)

        return query.distinct()

    def get_or_create_thread(self, request, name=None, *participant_ids):
        """
        When a Participant posts a message to other participants without specifying an existing Thread,
        we must
        1. Create a new Thread if they have not yet opened the discussion.
        2. If they have already opened the discussion and multiple Threads are not allowed for the same users, we must
            re-attach this message to the existing thread.
        3. If they have already opened the discussion and multiple Threads are allowed, we simply create a new one.
        """

        # we get the current participant
        # or create him if he does not exit

        participant_ids = list(participant_ids)
        if request.rest_messaging_participant.id not in participant_ids:
            participant_ids.append(request.rest_messaging_participant.id)

        # we need at least one other participant
        if len(participant_ids) < 2:
            raise Exception('At least two participants are required.')

        if getattr(settings, "REST_MESSAGING_THREAD_UNIQUE_FOR_ACTIVE_RECIPIENTS", True) is True:
            # if we limit the number of threads by active participants
            # we ensure a thread is not already running
            existing_threads = self.get_active_threads_involving_all_participants(*participant_ids)
            if len(list(existing_threads)) > 0:
                return existing_threads[0]

        # we have no existing Thread or multiple Thread instances are allowed
        thread = Thread.objects.create(name=name)

        # we add the participants
        thread.add_participants(request, *participant_ids)

        # we send a signal to say the thread with participants is created
        post_save.send(Thread, instance=thread, created=True, created_and_add_participants=True, request_participant_id=request.rest_messaging_participant.id)

        return thread


@python_2_unicode_compatible
class Thread(models.Model):
    """
    A Thread groups messages using their recipients.
    """
    name = models.CharField(max_length=255, null=True, blank=True)
    participants = models.ManyToManyField(Participant, through='Participation')
    objects = models.Manager()
    managers = ThreadManager()

    def __str__(self):
        return self.name if self.name else "Thread {0}".format(self.id)

    def is_participant(self, request, *args, **kwargs):
        """ We ensure request.user is a participant to the thread. """
        participants = self.participants.all()
        try:
            current = Participant.objects.get(id=request.user.id)
            if current in participants:
                return current
        except:
            pass
        return False

    def add_participants(self, request, *participants_ids):
        """
        Ensures the current user has the authorization to add the participants.
        By default, a user can add a participant if he himself is a participant.
        A callback can be added in the settings here.
        """
        participants_ids_returned_by_callback = getattr(settings, 'REST_MESSAGING_ADD_PARTICIPANTS_CALLBACK', self._limit_participants)(request, *participants_ids)
        participations = []
        ids = []
        for participant_id in participants_ids_returned_by_callback:
            participations.append(Participation(participant_id=participant_id, thread=self))
            ids.append(participant_id)

        Participation.objects.bulk_create(participations)
        post_save.send(Thread, instance=self, created=True, created_and_add_participants=True, request_participant_id=request.rest_messaging_participant.id)

        return ids

    def _limit_participants(self, request, *participants_ids):
        """ By default, we ensure we do not have more than 10 participants. """
        participants_all = self.participants.all().values_list('id', flat=True)

        max = 10 - len(participants_all)
        lst = []
        for index, participant_id in enumerate(participants_ids):
            if index >= max:
                break
            if participant_id not in participants_all:
                lst.append(participant_id)
        return lst

    def remove_participant(self, request, participant):
        removable_participants_ids = self.get_removable_participants_ids(request)
        if participant.id in removable_participants_ids:
            participation = Participation.objects.get(participant=participant, thread=self, date_left=None)
            participation.date_left = now()
            participation.save()
            post_save.send(Thread, instance=self, created=False, remove_participant=True, removed_participant=participant, request_participant_id=request.rest_messaging_participant.id)
            return participation
        else:
            raise Exception('The participant may not be removed.')

    def get_removable_participants_ids(self, request):
        removable_participants_ids = getattr(settings, 'REST_MESSAGING_REMOVE_PARTICIPANTS_CALLBACK', self._can_remove_oneself_only)(request, self)
        return removable_participants_ids

    def _can_remove_oneself_only(self, request, participant):
        """ By default, we ensure request.user can only remove oneself. """
        try:
            return [self.is_participant(request).id]
        except:
            return []


class Participation(models.Model):
    """
    Links Participant to threads.
    Tells us when a participant has joined a Thread and when he left.
    """
    participant = models.ForeignKey(Participant)
    thread = models.ForeignKey(Thread)
    date_joined = models.DateTimeField(auto_now_add=True)
    date_left = models.DateTimeField(null=True, blank=True)
    date_last_check = models.DateTimeField(null=True, blank=True)  # a timestamp to be set when a participant reads a thread


class MessageManager(models.Manager):

    def return_daily_messages_count(self, sender):
        """ Returns the number of messages sent in the last 24 hours so we can ensure the user does not exceed his messaging limits """
        h24 = now() - timedelta(days=1)
        return Message.objects.filter(sender=sender, sent_at__gte=h24).count()

    def check_who_read(self, messages):
        """ Check who read each message. """
        # we get the corresponding Participation objects
        for m in messages:
            readers = []
            for p in m.thread.participation_set.all():
                if p.date_last_check is None:
                    pass
                elif p.date_last_check > m.sent_at:
                    # the message has been read
                    readers.append(p.participant.id)
            setattr(m, "readers", readers)

        return messages

    def check_is_notification(self, participant_id, messages):
        """ Check if each message requires a notification for the specified participant. """
        try:
            # we get the last check
            last_check = NotificationCheck.objects.filter(participant__id=participant_id).latest('id').date_check
        except Exception:
            # we have no notification check
            # all the messages are considered as new
            for m in messages:
                m.is_notification = True
            return messages

        for m in messages:
            if m.sent_at > last_check and m.sender.id != participant_id:
                setattr(m, "is_notification", True)
            else:
                setattr(m, "is_notification", False)
        return messages

    def get_lasts_messages_of_threads(self, participant_id, check_who_read=True, check_is_notification=True):
        """ Returns the last message in each thread """
        # we get the last message for each thread
        # we must query the messages using two queries because only Postgres supports .order_by('thread', '-sent_at').distinct('thread')
        threads = Thread.managers.\
            get_threads_where_participant_is_active(participant_id).\
            annotate(last_message_id=Max('message__id'))
        messages = Message.objects.filter(id__in=[thread.last_message_id for thread in threads]).\
            order_by('-id').\
            distinct().\
            select_related('thread', 'sender')

        if check_who_read is True:
            messages = messages.prefetch_related('thread__participation_set', 'thread__participation_set__participant')
            messages = self.check_who_read(messages)
        else:
            messages = messages.prefetch_related('thread__participants')

        if check_is_notification is True:
            messages = self.check_is_notification(participant_id, messages)
        return messages

    def get_all_messages_in_thread(self, participant_id, thread_id, check_who_read=True):
        """ Returns all the messages in a thread. """
        try:
            messages = Message.objects.filter(thread__id=thread_id).\
                order_by('-id').\
                select_related('thread').\
                prefetch_related('thread__participation_set', 'thread__participation_set__participant')
        except Exception:
            return Message.objects.none()

        messages = self.check_who_read(messages)
        return messages


@python_2_unicode_compatible
class Message(models.Model):
    """
    A message between a User and another User or an AnonymousUser.
    """

    body = models.TextField(null=False)
    sender = models.ForeignKey(Participant, null=False)
    thread = models.ForeignKey(Thread)
    sent_at = models.DateTimeField(auto_now_add=True, blank=True)
    objects = models.Manager()
    managers = MessageManager()

    def __str__(self):
        return "{0}: {1}".format(self.sender, "{0}".format(self.body[:15]))

    def save(self, *args, **kwargs):
        """ Checks if there is a daily limit to the number of messages that can be sent. """
        max_messages = getattr(settings, 'REST_MESSAGING_DAILY_LIMIT_CALLBACK', lambda message_instance, *args, **kwargs: None)(self, *args, **kwargs)
        if max_messages is None or Message.managers.return_daily_messages_count(self.sender) < max_messages:
            super(Message, self).save(*args, **kwargs)
        else:
            # participant cannot write anymore today
            raise Exception('The daily messaging limit has been reached for this sender')


@python_2_unicode_compatible
class NotificationCheck(models.Model):
    """
    A timestamp everytime a user checks his notifications
    """
    participant = models.OneToOneField(Participant)
    date_check = models.DateTimeField()

    def __str__(self):
        return "{0}: {1}".format(self.participant, self.date_check)
