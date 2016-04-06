<div class="badges">
    <a href="http://travis-ci.org/raphaelgyory/django-rest-messaging">
        <img src="https://travis-ci.org/raphaelgyory/django-rest-messaging.svg?branch=master">
    </a>
    <a href="https://pypi.python.org/pypi/django-rest-messaging">
        <img src="https://img.shields.io/pypi/v/django-rest-messaging.svg">
    </a>
    <a href="https://coveralls.io/github/raphaelgyory/django-rest-messaging?branch=master">
        <img src="https://coveralls.io/repos/github/raphaelgyory/django-rest-messaging/badge.svg?branch=master">
    </a>
</div>


# REST: django-rest-messaging

The django-rest-messaging module is the base of the project. It provides all the logic and entry points for the messaging service. 

## Requirements

* Python (2.7, 3.3, 3.4, 3.5)
* Django (1.6, 1.7, 1.8, 1.9)
* DRF (2.4, 3.0, 3.1, 3.2, 3.3, 3.4)

## Installation

Install using `pip`...

```bash
$ pip install django-rest-messaging
```

Add the module to the installed apps.

```python

# settings.py

INSTALLED_APPS=(
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # ...
    'rest_messaging',
)

```

Add the django-rest-messaging middleware to your application.

```python

# settings.py

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # (...) your other middlewares
    'rest_messaging.middleware.MessagingMiddleware'
)

```

Add the project's urls.

```python

# urls.py

urlpatterns = [
	# (...) your other urls
    url(r'^messaging/', include('rest_messaging.urls', namespace='rest_messaging')),
]

```

Migrate

```python
$ manage.py migrate
```

This is it. There are however a few settings you might want to change.

## Settings

A few settings can be configured in your project's settings.py file:

### Daily messages limit

By default, django-rest-messaging does not limit the number of messages a participant can send. You can modify this behaviour by setting settings.REST_MESSAGING_DAILY_LIMIT_CALLBACK to a function that returns the max number of messages a user can send daily. For example:

```python

# my_module.my_file.py
max_daily_messages(message_instance, *args, **kwargs):
    """ 
    Your function will receive as arguments the Message (Django model) instance, 
    and the args and kwargs passed to the save method.
    It must return an integer defining the daily limit, or None if there is no limitation. 
    """
    # so for instance, if you whish to limit the number of messages to 50 every day
    return 50


# settings.py
from my_module.my_file import max_daily_messages
REST_MESSAGING_DAILY_LIMIT_CALLBACK = max_daily_messages

```

### Filtering participants

You can filter the participants that can be added to a thread. 
By default, django-rest-messaging limits the number of participants to 10. You can modify this behaviour by setting settings.REST_MESSAGING_ADD_PARTICIPANTS_CALLBACK to a function that returns the acceptable participants ids. For example:

```python

# my_module.my_file.py
add_participants_filter(request, *participants_ids):
    """ 
    The function will receive as arguments 
    1. the request and 
    2. the ids of the participants that we try to add. 
    It must return a list containing the ids of the participants
    that can be added in the thread. 
    """
    # so for instance, if you whish to allow messaging only between staff members you could do
    valid_ids = []
    staff_ids = User.objects.filter(is_staff=True).values_list('id', flat=True)
    for id in participants_ids:
        if id in staff_ids:
            valid_ids.append(id)
    return valid_ids


# settings.py
from my_module.my_file import add_paricipants_filter
REST_MESSAGING_ADD_PARTICIPANTS_CALLBACK = add_participants_filter

```

### Removing participants

By default, django-rest-messaging allow participants to quit a thread. It does not allow a participant to remove another participant. You can modify this behaviour by setting settings.REST_MESSAGING_REMOVE_PARTICIPANTS_CALLBACK to a function that returns a list containing the ids of the participant who may be removed. For example:

```python

# my_module.my_file.py
remove_participant_filter(request, participant, thread):
    """ 
    The function will receive as arguments 
    1. the request and 
    2. the participant instance we want to remove. 
    It must return the ids of the participants that can be removed 
    (or an empty list if no participant can be removed). 
    """
    # so for instance, if the admin only should be allowed to remove a user, we could do
    if request.user.is_superuser:
    	return [participant.id]
	return []

# settings.py
from my_module.my_file import remove_participant_filter
REST_MESSAGING_REMOVE_PARTICIPANTS_CALLBACK = remove_participant_filter

```

### Allowing duplicate threads

By default, django-rest-messaging will group messages involing the same participants. If one tries to create a thread involving participants that have already started a discussion, the message will be rattached to the existing thread. You can modify this behaviour by setting settings.REST_MESSAGING_THREAD_UNIQUE_FOR_ACTIVE_RECIPIENTS to False

```python

# settings.py
REST_MESSAGING_THREAD_UNIQUE_FOR_ACTIVE_RECIPIENTS = False

```

### Add information about participants

When serializing messages, django-rest-messaging will by default return them with a list containing the id of their readers. No additionnal information about these readers will be provided, because it might not be available (ie, because the information about the User instance is saved in another database). You might want to change this behaviour, for instance by providing their username too. This can be done by setting settings.REST_MESSAGING_SERIALIZE_PARTICIPANTS_CALLBACK to a function that returns the desired serialized User object. The callback will be automatically called by the thread serializer, which will use it to render the information about the thread's participants. The tests.test_serializers module provides such an example:

```python

# this example is taken from tests.test_serializers.py
# my_module.my_file.py

class UserProfileSerializer(serializers.ModelSerializer):
    """ Serializer for testing purpose only (for the ThreadSerializer callback). """

    image = compat_serializer_method_field('get_image')
    contact = compat_serializer_method_field('get_contact')

    class Meta:
        model = User
        fields = ('id', 'username', 'image', 'contact')

    def get_image(self, obj):
        return obj.profile.image

    def get_contact(self, obj):
        return obj.profile.contact

def _thread_serializer_callback(thread_instance):
    """ 
    Shows how ThreadSerializer can get access to data about the users, beyond their simple ids. 
    """
    # we get all the participants' ids
    participants_ids = [participant.id for participant in thread_instance.participants.all()]
    # we can run the query we want using these ids
    # here we want the users and related information
    users = User.objects.filter(id__in=participants_ids).select_related('profile')
    # we call our custom serializer
    serialized = UserProfileSerializer(users, many=True)
    return serialized.data
    

# settings.py
from my_module.my_file import _thread_serializer_callback
REST_MESSAGING_SERIALIZE_PARTICIPANTS_CALLBACK = _thread_serializer_callback

```

## Testing

Install testing requirements.

```bash
$ pip install -r requirements.txt
```

Run with runtests.

```bash
$ ./runtests.py
```

You can also use the excellent [tox](http://tox.readthedocs.org/en/latest/) testing tool to run the tests against all supported versions of Python and Django. Install tox globally, and then simply run:

```bash
$ tox
```

## Documentation

To build the documentation, you'll need to install `mkdocs`.

```bash
$ pip install mkdocs
```

To preview the documentation:

```bash
$ mkdocs serve
Running at: http://127.0.0.1:8000/
```

To build the documentation:

```bash
$ mkdocs build
```
