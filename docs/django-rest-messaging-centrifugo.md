<div class="badges">
    <a href="http://travis-ci.org/raphaelgyory/django-rest-messaging-centrifugo">
        <img src="https://travis-ci.org/raphaelgyory/django-rest-messaging-centrifugo.svg?branch=master">
    </a>
    <a href="https://pypi.python.org/pypi/django-rest-messaging-centrifugo">
        <img src="https://img.shields.io/pypi/v/django-rest-messaging-centrifugo.svg">
    </a>
</div>


# Real-time: django-rest-messaging-centrifugo

The django-rest-messaging-centrifugo module extends the django-rest-messaging module. It adds real-time messaging capabilities, by integrating django-rest-messaging and [centrifugo](https://github.com/centrifugal/centrifugo).


## Requirements

* Python (2.7, 3.3, 3.4, 3.5)
* Django (1.7, 1.8, 1.9)
* DRF (2.4, 3.0, 3.1, 3.2, 3.3, 3.4)

## Installation

### Install centrifugo

Download centrifugo as expplained [here](https://fzambia.gitbooks.io/centrifugal/content/server/start.html), and move it to /usr/bin/. You shuold have a /usr/bin/centrifugo executable. You can now check the installation is successfull by running

```bash
$ cd /usr/bin
$ ./centrifugo -h
```

### Create a config.json file

Create a config.json file. You can copy the following one (just change the "secret" key, the other elements may be left as is). The file should be placed in a directory you have access to when launching centrifugo.

```json
# /path/to/config.json
{
  "secret": "secret", # change this to an unguessable string
  "anonymous": false,
  "publish": false,
  "watch": false,
  "presence": true,
  "join_leave": false,
  "history_size": 0,
  "history_lifetime": 0,
  "namespaces": [
    {
      "name": "messages",
      "anonymous": false
    },
    {
      "name": "threads",
      "anonymous": false
    }
  ]
}
```

### Launch centrifugo

Download centrifugo as expplained [here](https://fzambia.gitbooks.io/centrifugal/content/server/start.html), and move it to /usr/bin/. You should have a /usr/bin/centrifugo executable. You can now check the installation is successfull by running 

```bash
# /usr/bin
# port 8802 is for example purpose only. Note that centrifugo runs by default on port 8000, which can compete with your regular Django port
$ ./centrifugo --config=/path/to/config.json --port=8802 
```

There are other command line options (address, engine etc.). See [here](https://fzambia.gitbooks.io/centrifugal/content/server/configuration.html).

For information, you can see an additionnal example of how we launched centrifugo for the tests in django-rest-messaging-centrifugo/tests/test_integration.py (in setUpClass).

### Install django-rest-messaging-centrifugo

```bash
$ pip install django-rest-messaging-centrifugo
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
    'rest_messaging_centrifugo',
)

```

Add additionnal configuration.

```python

# settings.py

# django-rest-messaging-centrifugo config
CENTRIFUGO_PORT = 8802 # the port on which centrifugo shall run, as set in config.json (see above)
CENTRIFUGO_MESSAGE_NAMESPACE = "messages" # the centrifugo message channel, do not change this value
CENTRIFUGO_THREAD_NAMESPACE = "threads" # the centrifugo thread channel, do not change this value
# centrifugo config
# note that the following settings refer to centrifugE_... 
# because it is the old name of the project
CENTRIFUGE_ADDRESS = 'http://localhost:{0}/'.format(CENTRIFUGO_PORT) # change this to your domain/your port in production
CENTRIFUGE_SECRET = 'secret' # change this to the key you put in config.json (see above)
CENTRIFUGE_TIMEOUT = 5 

```

Add the project's urls.

```python

# urls.py

urlpatterns = [
	# (...) your other urls
	# do not forget to include django-rest-messaging
    url(r'^messaging/', include('rest_messaging.urls', namespace='rest_messaging')),
    url(r'^messaging/centrifugo/', include('rest_messaging_centrifugo.urls', namespace='rest_messaging_centrifugo')),
]

```

## Examples

A full example will be available when the javascript consumer will be available. In the meantime, you can refer to the tests: django-rest-messaging-centrifugo/tests/test_integration.py and django-rest-messaging-centrifugo/tests/templates/tests/index.html go through the whole process of starting connections, identifying available channels and publishing new messages. 


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

The documentation of the whole project has been included in django-rest-messaging, on which the other modules rely.