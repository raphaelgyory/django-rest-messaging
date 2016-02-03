<div class="badges">
    <a href="http://travis-ci.org/raphaelgyory/django-rest-messaging">
        <img src="https://travis-ci.org/raphaelgyory/django-rest-messaging.svg?branch=master">
    </a>
    <a href="https://pypi.python.org/pypi/django-rest-messaging">
        <img src="https://img.shields.io/pypi/v/django-rest-messaging.svg">
    </a>
</div>

---

# Django rest messaging

The project provides a pluggable Facebook-like messaging API for Django Rest Framework.

This is a first release (you know, "Release Early, Release Often"...). The backend is fully tested - and working - and the javascript frontend is under way.
I coded this in a lean perspective and want to see if the project sparks some interest. Any comments and suggestions are therefore very welcome!

---

## Overview

The project provides a Facebook-like messaging backend for django rest framework. It is composed of three parts: 

* [django-rest-messaging](http://tox.readthedocs.org/en/latest/) (rest messaging backend built with DRF),
* [django-rest-messaging-centrifugo](http://tox.readthedocs.org/en/latest/) (allows you to build a real-time messaging service using websockets, by integrating django-rest-messaging and [centrifugo](https://github.com/centrifugal/centrifugo)), and 
* their javascript consumer (under development).

## Environment

Tested with

* Python (2.7, 3.3, 3.4, 3.5)
* Django (1.6, 1.7, 1.8, 1.9)
* DRF (2.4, 3.0, 3.1, 3.2, 3.3, 3.4)

## Installation, testing and documentation

Please start by installating the [REST backend](/django-rest-messaging/). Then you can optinally add the [real-time](/django-rest-messaging-centrifugo/) module and the javascript consumer. 

## TODO

Finish the javascript consumer.
Add file upload.
