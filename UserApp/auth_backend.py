from django.contrib.auth.backends import ModelBackend

class BlockedUserBackend(ModelBackend):
    def user_can_authenticate(self, user):
        profile = user.userprofile
        if profile.is_blocked():
            return False
        return True
