"""
Definition of views.
"""

from django.shortcuts import render
from django.http import HttpRequest, JsonResponse, HttpResponseRedirect
from django.template import RequestContext
from datetime import datetime
from cgi import parse_qs, escape
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import views as auth_views
from django.core.urlresolvers import reverse
from app.models import UnreadMessage


import logging
#import MySQLdb
from redcap import Project, RedcapError

from twilio.access_token import AccessToken, IpMessagingGrant


def dashboard(request):
    """Renders the dashboard page."""
    assert isinstance(request, HttpRequest)

    # Check if user is logged in. Otherwise redirect to login page.
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('login'))

    unread_messages = []

    for i in range(4):
        # create_unread_message(patient_id, patient_name, num_unread)
        temp = UnreadMessage.objects.create_unread_message(i * 10, "Patient " + str(i), i * 10)
        unread_messages.append(temp)

    context = {
        'title':'Dashboard',
        'year':datetime.now().year,
        'unread_messages': unread_messages
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
        'app/dashboard.html',
        context
    )


def loginRedirect(request, **kwargs):
    # Checks to see if user is logged in. If so, redirect to dashboard page.
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('dashboard'))
    else:
        return auth_views.login(request, **kwargs)


def patients(request):
    """Renders the patients page."""
    assert isinstance(request, HttpRequest)

    # Check if user is logged in. Otherwise redirect to login page.
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('login'))


    context = {
        'title': 'Patients',
        'message': 'List of patients.',
        'year': datetime.now().year,
        'patient_results': [],
    }

    return render(
        request,
        'app/patients.html',
        context
    )

def messages(request):
    """Renders the messages page."""
    assert isinstance(request, HttpRequest)

    # Check if user is logged in. Otherwise redirect to login page.
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('login'))

    context = {
        'title':'Messages',
        'message':'Send messages.',
        'year':datetime.now().year,
    }

    return render(
        request,
        'app/messages.html',
        context
    )

"""
Saves a message to the REDCap database.
"""
def saveMessage(request):
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

"""
Gets an access token for Twilio IP messaging. Called by messages.js.
"""
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

