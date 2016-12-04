"""
Definition of views.
"""

from django.shortcuts import render
from django.http import HttpRequest, JsonResponse
from django.template import RequestContext
from datetime import datetime

import logging

from twilio.access_token import AccessToken, IpMessagingGrant

def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    context = {
        'title':'Home Page',
        'year':datetime.now().year,
    }

    return render(
        request,
        'app/index.html',
        context
    )

def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    context = {
        'title':'Contact',
        'message':'Your contact page.',
        'year':datetime.now().year,
    }

    return render(
        request,
        'app/contact.html',
        context
    )

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    context = {
        'title':'About',
        'message':'Your application description page.',
        'year':datetime.now().year,
    }

    return render(
        request,
        'app/about.html',
        context
    )

def messaging(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    context = {
        'title':'Messaging',
        'message':'Send messages.',
        'year':datetime.now().year,
    }
    return render(
        request,
        'app/messaging.html',
        context
    )

def token(request):
    assert isinstance(request, HttpRequest)

    # get credentials for environment variables
    account_sid = 'ACbf05fc8a591d9136132c9d62d8319eb1'
    api_key = 'SKeed5a60867e8f918ac7f2e9fa819d98a'
    api_secret = 'R3W2DYt3Eq1hbwj2GRKQV531XeVDU9sJ'
    service_sid = 'IS7d421d86df064d9698e91ee6e3d4bcf5'

    # create a randomly generated username for the client
    identity = "bob"

    # <unique app>:<user>:<device>
    endpoint = "TwilioChatDemo:8:29"

    # Create access token with credentials
    token = AccessToken(account_sid, api_key, api_secret, identity)

    # Create an IP Messaging grant and add to token
    ipm_grant = IpMessagingGrant(endpoint_id=endpoint, service_sid=service_sid)
    token.add_grant(ipm_grant)

    # COMMENTED CAUSE FLASK THING - Return token info as JSON 
    #return jsonify(identity=identity, token=token.to_jwt())
    return JsonResponse({'identity': identity, 'token': token.to_jwt()})
