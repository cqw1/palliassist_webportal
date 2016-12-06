"""
Definition of views.
"""

from django.shortcuts import render
from django.http import HttpRequest, JsonResponse
from django.template import RequestContext
from datetime import datetime
from cgi import parse_qs, escape
from django.views.decorators.csrf import csrf_exempt

import logging
#import MySQLdb
from redcap import Project, RedcapError

from twilio.access_token import AccessToken, IpMessagingGrant


def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    context = {
        'title':'Home Page',
        'year':datetime.now().year,
    }

    """
    URL = 'https://hcbredcap.com.br/api/'
    TOKEN = 'F2C5AEE8A2594B0A9E442EE91C56CC7A'

    project = Project(URL, TOKEN)

    for field in project.metadata:
        print "%s (%s) => %s" % (field['field_name'],field['field_type'], field['field_label'])

    data = project.export_records()
    for d in data:
        print d
        """


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

def saveMessage(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)

    print request

    sender = request.GET['sender']
    channel = request.GET['channel']
    content = request.GET['content']
    content_type = request.GET['type']
    time_sent = request.GET['time_sent']

    print "saveMessage:"
    print sender, channel, content, content_type, time_sent

    """
    db = MySQLdb.connect(host="us-cdbr-azure-southcentral-f.cloudapp.net", user="b811fcf3c52d36", passwd="91e7ba1e", db="palliative")
    cur = db.cursor()

    sender_id = cur.execute("SELECT id FROM palliative.login WHERE username = '" + sender + "';")
    print sender_id

    result = cur.execute("INSERT INTO palliative.messages VALUES(" + str(sender_id) + ", '" + channel + "', '" + content + "', '" + content_type + "', " + str(time_sent) + ");")
    print result

    cur.close()

    db.commit()
    db.close()
    """

    URL = 'https://hcbredcap.com.br/api/'
    TOKEN = 'F2C5AEE8A2594B0A9E442EE91C56CC7A'

    project = Project(URL, TOKEN)

    for field in project.metadata:
        print "%s (%s) => %s" % (field['field_name'],field['field_type'], field['field_label'])

    data = project.export_records()
    for d in data:
        print d

    d = data[0]
    d['content'] = content
    d['content_type'] = content_type
    d['channel'] = channel
    d['time_sent'] = time_sent

    response = project.import_records(data)
    print response['count']
        

    
    return JsonResponse({})


def token(request):
    assert isinstance(request, HttpRequest)

    # get credentials for environment variables
    account_sid = 'ACbf05fc8a591d9136132c9d62d8319eb1'
    api_key = 'SKeed5a60867e8f918ac7f2e9fa819d98a'
    api_secret = 'R3W2DYt3Eq1hbwj2GRKQV531XeVDU9sJ'

    # old one with testchannel nd general
    #service_sid = 'IS7d421d86df064d9698e91ee6e3d4bcf5'

    service_sid = 'IS2ec68050ef5e4c79b15b78c3ded7ddc5'

    # create a randomly generated username for the client
    identity = request.GET['identity']

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
