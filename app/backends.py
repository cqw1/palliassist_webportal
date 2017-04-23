# import the User object
from django.contrib.auth.models import User
from django.conf import settings
from redcap import Project, RedcapError

# verify against redcap db
class REDCapBackend:

    # create an authentication method
    # this is called by the standard django login procedure
    def authenticate(self, username=None, password=None):
        print
        print "[REDCapBackend.authenticate]"
        print

        """
        # Clear all users from the db
        print "before:", User.objects.all()
        User.objects.all().delete()
        print "after:", User.objects.all()
        """

        """
        URL = 'https://hcbredcap.com.br/api/'
        TOKEN = 'F2C5AEE8A2594B0A9E442EE91C56CC7A'

        #project = Project(URL, TOKEN)
        #print project

        for field in settings.REDCAP_USER_PROJECT.metadata:
            print "%s (%s) => %s" % (field['field_name'],field['field_type'], field['field_label'])

        found = False
        data = settings.REDCAP_USER_PROJECT.export_records()
        for d in data:
            if d['username'] == username and d['password'] == password:
                found = True
                break

        if not found:
            # No user with the input username was found. 
            return None

        try:
            # User existed.
            user = User.objects.get(username=username)
            return user

        except User.DoesNotExist:
            # Creating new user.
            user = User(username=username)
            user.password = password
            user.save()
            return user
        return None
        """


        """
        try:
            # try to find a user matching the username
            user = User.objects.get(username=username_input)

            # check the password is the reverse of the username
            if password == username[::-1]:

                # yes? return the Django user object
                return user

            else:
                # no? return none - triggers default login failed
                return None

        except User.DoesNotExist:
            # no user was found, return none - triggers default login failed
            return None

        """


    # required for backend to work properly - unchanged in most scenarios
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None



