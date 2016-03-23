
# React: django-rest-messaging-js

The django-rest-messaging-js module provides the javascript backend for the two other modules.

## Requirements

Django-rest-messaging. Django-rest-messaging-centrifugo is optional.

## Installation

The are two ways to integrate django-rest-messaging-js: using npm or simply loading from cdn ().

In both cases, React, jQuery and Babel will be required. Centrifuge and sockjs are required if you want to use django-rest-messaging-centrifugo.


### Using npm

```bash
$ npm install django-rest-messaging-js --save
```

### Using the CDN file

No installation is required, your view's template can load the file directly from . 

```html
<head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/babel-core/5.8.23/browser.min.js"></script>
	<script src="https://fb.me/react-0.14.0.js" type="text/javascript"></script>
	<script src="https://fb.me/react-dom-0.14.0.js" type="text/javascript"></script>
	<script src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.3/jquery.min.js"></script>
	<script src="//cdn.jsdelivr.net/sockjs/1.0/sockjs.min.js" type="text/javascript"></script>
	<script src="//rawgit.com/centrifugal/centrifuge-js/master/centrifuge.js"></script>
	<!-- This is the js module -->
	<script src='{% static "demo/django-rest-messaging-1.0.1.js" %}' type="text/javascript"></script>
  	<!-- This is the example app you will have to build yourself (see next step), 
  	with its associated css file -->
  	<script src='{% static "demo/exampleApp.jsx" %}' type="text/babel"></script>
	<link href='{% static "demo/django-rest-messaging-css.css" %}' rel="stylesheet" type="text/css" >
</head>
```

## Creating an application


You have two possibilities to create your application: create the whole application as a React object, or simply load the application's components separately into your html files. The first option is best if you create a React app. The other should be used if you integrate the the module to an existing app not using React. 

In both cases, Django-rest-messaging-js can be used more or less out of the box. Before digging into the application code, a quick tour of it's components will help you start.

### Intro: django-rest-messaging-js components

This is a quick tour since theses components are likely to evolve (a bit) in the next version of the django-rest-messaging-js.

The components you can include without any modification:

* MessagesForm: the form to post a message.
* MessagesList: the messages in the selected thread.
* MessagesLoadMore: the button allowing to load more messages in the selected thread.
* MessagesManager: the manager of the whole application. It initialize data and connects to the sockets, allowing real-time messaging.
* NotificationsCounter: returns the count of notifications.
* ThreadsForm: the form handling threads creation. This form is coordinated with MessagesForm to prevent creation of empty threads.
* ThreadsCreateLink: link to trigger the ThreadsForm to allow threads creation (example below).
* ThreadsList: all the threads involving the user.
* ThreadsLoadMore: the button allowing to load more threads.
* ThreadsQuit: the link for quitting the selected thread.

The listeners you should act upon:

* loginListener: this listener should be called after the user logged in (with the user id) or out (with null). Django-rest-messaging-js will not query any information as long as the user is not logged in. (see example of use below). 
* recipientsListener: this listener allows the display of user information along with the messages. It expects an array of objects containing the users' id, username and image (this behavior can be modified).


### Option 1: React

Once django-rest-messaging-js installed, it's components are available as properties of the DjangoRestMessaging object. Including the components can be done as follows:

```javascript
# exampleApp.jsx
var React = require('react');
var ReactDOM = require('react-dom');
var DjangoRestMessaging = require('DjangoRestMessaging');
var MessagesManager = DjangoRestMessaging.MessagesManager;

var App = React.createClass({
   render: function(){
       return (
    		<div>
    			<MessagesManager />
    			<!-- The rest of your code -->   
   		    </div>
       );
   }
});
```

If you want more information on how to build an application using react, you can find a quick example [in the demo app](http://tox.readthedocs.org/en/latest/) (this is a simplistic example for use in an html app) or [in django-rest-messaging-js testing app](http://tox.readthedocs.org/en/latest/) (build entirely with react and webpack, with serveside loading example).


### Option 2: regular javascript

You do not need advanced React.js skills to use the module this way, but you need basic javascript understanding.

React uses the .jsx language. Practically, this means you will wrap your javascript within a 'text/babel' script.



```html
# the regular django template .html
<div id="theIdOfTheHtmlTag"></div>
<script type="text/babel">
	ReactDOM.render(<TheNameOfTheComponent/>, document.getElementById('theIdOfTheHtmlTag'));
</script>
```

Alternatively, you can write the javascript in a .jsx file, and load it in your html template.

```html
# the regular django template .html
<div id="theIdOfTheHtmlTag"></div>
<script src='{% static "demo/exampleApp.jsx" %}' type="text/babel"></script>
```
```html
# exampleApp.jsx
ReactDOM.render(<TheNameOfTheComponent/>, document.getElementById('theIdOfTheHtmlTag'));
```

You can see a full example in the source code implementing django-rest-messaging-js in a html file in the [django-rest-messaging-js testing app](http://tox.readthedocs.org/en/latest/).


## CSS

Django-rest-messaging-js provides no styling, except for html tags. An example of styling can be found [in the css file of the testing app](http://tox.readthedocs.org/en/latest/)

## TODO

Django-rest-messaging-js is an early release. The follwong realeases will focus on 3 points:

* implementing the django SETTING options defined in django-rest-messaging;

* use SASS (for now, some classes use bootstrap, which is not optimal);

* do some js performance enhancements.
