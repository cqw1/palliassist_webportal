# import the User object
from django.contrib.auth.models import User

# verify against mysql db
class SqlBackend:

    # create an authentication method
    # this is called by the standard django login procedure
    def authenticate(self, username=None, password=None):
        try:
            # try to find a user matching the username
            user = User.objects.get(username=username)

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


    # required for backend to work properly - unchanged in most scenarios
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None



