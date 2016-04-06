<div class="badges">
    <a href="http://travis-ci.org/raphaelgyory/django-rest-messaging-js">
        <img src="https://travis-ci.org/raphaelgyory/django-rest-messaging-js.svg?branch=master">
    </a>
</div>

# React: django-rest-messaging-js

The django-rest-messaging-js module provides the javascript frontend for the two other modules.

## Requirements

Django-rest-messaging. Django-rest-messaging-centrifugo is optional.

## Installation

The are two ways to integrate django-rest-messaging-js: using npm or simply loading it from the [cdn](https://cdn.rawgit.com/raphaelgyory/django-rest-messaging-js/master/django-rest-messaging-js/dist/django-rest-messaging-1.0.2.js).

In both cases, React, jQuery, moment.js and Babel will be required. Centrifuge and sockjs are required if you want to use django-rest-messaging-centrifugo.


### Using npm

```bash
$ npm install django-rest-messaging-js --save
```

### Using the CDN file

No installation is required, your template can load the file directly from the [cdn](https://cdn.rawgit.com/raphaelgyory/django-rest-messaging-js/master/django-rest-messaging-js/dist/django-rest-messaging-1.0.2.js). 

```html
<!-- Head section example -->
<head>
	<!-- Babel is required to parse jsx -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/babel-core/5.8.23/browser.min.js"></script>
    <!-- React -->
	<script src="https://fb.me/react-0.14.0.js" type="text/javascript"></script>
	<script src="https://fb.me/react-dom-0.14.0.js" type="text/javascript"></script>
	<!-- Jquery -->
	<script src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.3/jquery.min.js"></script>
	<!-- Centrifugo js client and sockets -->
	<script src="//cdn.jsdelivr.net/sockjs/1.0/sockjs.min.js" type="text/javascript"></script>
	<script src="//rawgit.com/centrifugal/centrifuge-js/master/centrifuge.js"></script>
	<!-- Moment.js -->
	<script src="https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.12.0/moment.min.js"></script>
	<!-- Django rest messaging js client -->
	<script src="https://cdn.rawgit.com/raphaelgyory/django-rest-messaging-js/master/django-rest-messaging-js/dist/django-rest-messaging-1.0.2.js" type="text/javascript"></script>
  	<!-- This is the example app you will have to build yourself (see next step), 
  	with its associated css file -->
  	<script src='{% static "demo/exampleApp.jsx" %}' type="text/babel"></script>
	<link href='{% static "demo/django-rest-messaging-css.css" %}' rel="stylesheet" type="text/css" >
</head>
```

## Creating an application

Django-rest-messaging-js will work without requiring your whole frontend to use React. You can simply load the components separately into your html files. 

Django-rest-messaging-js can be used more or less out of the box. Before showing an example of integration, a quick tour of the components will help you get an idea of its possibilities.

### Intro: django-rest-messaging-js components

This is a quick tour since theses components are likely to evolve (a bit) in the next version of the django-rest-messaging-js.

The components you can include without any modification:

* MessagesForm: the form to post a message.
* MessagesList: the messages in the selected thread.
* MessagesLoadMore: the button allowing to load more messages in the selected thread.
* MessagesManager: the manager of the whole application. It initializes data and connects to the sockets, allowing real-time messaging.
* NotificationsCounter: returns the count of notifications.
* ThreadsForm: the form handling threads creation. This form is coordinated with MessagesForm to prevent creation of empty threads.
* ThreadsCreateLink: link to trigger the ThreadsForm to allow threads creation (example below).
* ThreadsList: all the threads involving the user.
* ThreadsLoadMore: the button allowing to load more threads.
* ThreadsQuit: the link for quitting the selected thread.

The listeners you should act upon:

* loginListener: this listener should be called after the user logged in (with the user id) or out (with null). Django-rest-messaging-js will not query any information as long as the user is not logged in.
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

If you want more information on how to build an application using react, you can find an example [in django-rest-messaging-js app](https://github.com/raphaelgyory/django-rest-messaging-js/tree/master/example) (built entirely with react and webpack, with serveside loading example).


### Option 2: regular javascript

You do not need advanced React.js skills to use the module this way, but you need basic javascript understanding.

React works best using the .jsx language. Practically, this means you will write javascript with an xml like syntax and wrap it in a 'text/babel' script.

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

To use django-rest-messaging-js, you just need to instantiate its components. Here is the full example used by the demo. Note the use of DjangoRestMessaging.listeners.recipientsListener and DjangoRestMessaging.listeners.loginListener to pass external information to django-rest-messaging-js.

```html
# index.html
{% load staticfiles %}
<!DOCTYPE html>
<html>
  	<head>
	    <meta charset="UTF-8">
	    <title>Django Rest Messaging Demo</title>
	    <script src="https://cdnjs.cloudflare.com/ajax/libs/babel-core/5.8.23/browser.min.js"></script>
	    <script src="https://fb.me/react-0.14.0.js" type="text/javascript"></script>
	    <script src="https://fb.me/react-dom-0.14.0.js" type="text/javascript"></script>
		<script src="//cdn.jsdelivr.net/sockjs/1.0/sockjs.min.js" type="text/javascript"></script>
		<script src="//rawgit.com/centrifugal/centrifuge-js/master/centrifuge.js"></script>
		<script src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.3/jquery.min.js"></script>
		<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/font-awesome/4.5.0/css/font-awesome.min.css">
		<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css" integrity="sha384-1q8mTJOASx8j1Au+a5WDVnPi2lkFfwwEAa8hDDdjZlpLegxhjVME1fgjWPGmkzs7" crossorigin="anonymous">
		<!-- Latest compiled and minified JavaScript -->
		<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/js/bootstrap.min.js" integrity="sha384-0mSbJDEHialfmuBBQP6A4Qrprq5OVfW37PRR3j5ELqxss1yVqOtnepnHVP9aJ7xS" crossorigin="anonymous"></script>
	  	<!-- Moment.js -->
		<script src="https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.12.0/moment.min.js"></script>
		<!-- Django rest messaging js client -->
		<script src="https://cdn.rawgit.com/raphaelgyory/django-rest-messaging-js/master/django-rest-messaging-js/dist/django-rest-messaging-1.0.2.js" type="text/javascript"></script>
	  	<link href='{% static "demo/django-rest-messaging-css.css" %}' rel="stylesheet" type="text/css" >
	</head>

  	<body>
  		<span id="MessagesManager"></span>     		
  		
    	<nav class="navbar navbar-fixed-top">
       		<div class="container">
       			<div class="navbar-header">
       				<button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar">
       					<span class="sr-only">Toggle navigation</span>
       					<span class="icon-bar"></span>
       					<span class="icon-bar"></span>
       					<span class="icon-bar"></span>
       				</button>
       				<a class="navbar-brand" href="#">Django Rest Messaging</a>
       			</div>
       			<div id="navbar" class="navbar-collapse collapse">
       				<ul class="nav navbar-nav">
       					<li>
		                    <a href="/site/">The project</a>
		                </li>
		                <li>
		                    <a href="/site/django-rest-messaging/">REST</a>
		                </li>
		                <li>
		                    <a href="/site/django-rest-messaging-centrifugo/">Real-time</a>
		                </li>
		                <li>
		                    <a href="/site/django-rest-messaging-js/">React.js</a>
		                </li>
		                <li class="active">
		                    <a href="#">Demo</a>
		                </li>
       				</ul>
       				<ul class="nav navbar-nav navbar-right">
       					<li>
		                   	<a href="/site/django-rest-messaging-js/">
		                        <i class="fa fa-arrow-left"></i> Previous
		                    </a>
		                </li>
		                <li class="disabled">
		                    <a>
		                        Next <i class="fa fa-arrow-right"></i>
		                    </a>
		                </li>
		                
		                <li>
		                    <a href="https://github.com/raphaelgyory/django-rest-messaging">
		                        
		                            <i class="fa fa-github"></i>
		                        &nbsp;
		                        GitHub
		                    </a>
		                </li>
	       		    </ul>
       			</div>
       		</div>
       	</nav>
       	<nav class="navbar navbar2">
     		<div class="container">
     			<div id="navbar2" class="navbar-collapse collapse">
     				<ul class="nav navbar-nav navbar-right">
       					<li class="dropdown">
     						<a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">
     							<span id="NotificationsCounter"></span>
     						</a>
     						<ul class="dropdown-menu">
     							<span id="ThreadsListNav"></span>     							
     						</ul>
     					</li>
     					<li class="navbar-right">
     						<button id="dummyLogin" class="btn btn-success btnLogin">Login!</button>
     					</li>
		       		    </ul>
     			</div>
     		</div>
     	</nav>
 		    
 		<div class="container" role="main">
   		    <div class="row">
   		    	<div class="col-md-8">
   		    		  <h3>This is an alternate demo, showing how to use Django-rest-messaging with a regular django html template.</h3>
	    		      <span id="ThreadsForm"></span>
	    		      <div id="messageMaxHeight">
	    		      		<span id="MessagesLoadMore"></span>
	    		      		<span id="MessagesList"></span>
	    		   	  </div>
	    		   	  <span id="MessagesForm"></span>
	    		   	  <span id="ThreadsQuit"></span>
	    		</div>
	    		<div class="col-md-4">
	    			<span id="ThreadsList"></span>
	    			<span id="ThreadsLoadMore"></span>
	    			<span id="ThreadsCreateLink"></span>
    		    </div>
	    	</div>
 		</div>  
  	</body>
  	<script type="text/babel">

		ReactDOM.render(<DjangoRestMessaging.MessagesManager/>, document.getElementById('MessagesManager'));
  		ReactDOM.render(<DjangoRestMessaging.NotificationsCounter/>, document.getElementById('NotificationsCounter'));
		ReactDOM.render(<DjangoRestMessaging.ThreadsList wrappingTag={"li"}/>, document.getElementById('ThreadsListNav'));
		ReactDOM.render(<DjangoRestMessaging.ThreadsForm />, document.getElementById('ThreadsForm'));
		ReactDOM.render(<DjangoRestMessaging.MessagesLoadMore />, document.getElementById('MessagesLoadMore'));
		ReactDOM.render(<DjangoRestMessaging.MessagesList />, document.getElementById('MessagesList'));
		ReactDOM.render(<DjangoRestMessaging.MessagesForm />, document.getElementById('MessagesForm'));
		ReactDOM.render(<DjangoRestMessaging.ThreadsQuit />, document.getElementById('ThreadsQuit'));
		ReactDOM.render(<DjangoRestMessaging.ThreadsList />, document.getElementById('ThreadsList'));
		ReactDOM.render(<DjangoRestMessaging.ThreadsLoadMore />, document.getElementById('ThreadsLoadMore'));
		ReactDOM.render(<DjangoRestMessaging.ThreadsCreateLink />, document.getElementById('ThreadsCreateLink'));
		

		// the users
		var users = [
       	     {
       	    	 "id": 1,
       	    	 "username": "John",
       	    	 "image": "/static/demo/John.png"
       	     },
       	     {
       	    	 "id": 2,
       	    	 "username": "Steve",
       	    	 "image": "/static/demo/Steve.png"
       	     },
       	     {
       	    	 "id": 3,
       	    	 "username": "Marc",
       	    	 "image": "/static/demo/Marc.png"
       	     },
       	     {
       	    	 "id": 4,
       	    	 "username": "Ada",
       	    	 "image": "/static/demo/Ada.png"
       	     },
       	     {
       	    	 "id": 5,
       	    	 "username": "Pepito",
       	    	 "image": "/static/demo/Pepito.png"
       	     },
       	     {
       	    	 "id": 6,
       	    	 "username": "Pedro",
       	    	 "image": "/static/demo/Pedro.png"
       	     },
       	];
	   
	   DjangoRestMessaging.listeners.recipientsListener(users);

		// this is regular jQuery, we log the user in and then call our listeners
		$('#dummyLogin').on("click", function() { 
			DjangoRestMessaging.ajaxRequest('/messaging/js/django-rest-messaging-demo-login/', 'GET', null).done(function(json){
				//doApp();
				DjangoRestMessaging.listeners.logoutListener();
				DjangoRestMessaging.listeners.loginListener(json.id);
			});
			
		});
    	
		// if the user is already logged in, just do
		// DjangoRestMessaging.listeners.loginListener(userId);

  	</script>
  	
  	<script type="text/javascript">
 		// reload
  		setTimeout(function(){window.location.reload();},3600000 - ((new Date) % 3600000) + 60);
  	</script>
  	
</html>
```


## CSS

Django-rest-messaging-js provides no styling. An example of styling can be found [in the css file of the testing app](https://github.com/raphaelgyory/django-rest-messaging-js/blob/master/example/dist/django-rest-messaging-css.css).

## TODO

Django-rest-messaging-js is an early release. The following realeases will focus on 3 points:

* implementing the django SETTING options defined in django-rest-messaging (some options like removing other people from a thread are not yet implemented);

* make the store play more nicely with user information;

* use SASS (for now, some classes implement bootstrap, which is not optimal);

* do js performance enhancements.
