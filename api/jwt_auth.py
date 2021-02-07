from rest_framework import authentication, exceptions
from django.conf import settings
import jwt
from rest_framework.authentication import CSRFCheck

from validator.models import User


class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_data = authentication.get_authorization_header(request)

        if not auth_data:
            return None

        prefix, token = auth_data.decode('utf-8').split(' ')

        if not prefix or not token:
            raise exceptions.AuthenticationFailed('Authentication failed')

        if prefix != 'JWT':
            raise exceptions.AuthenticationFailed('Authentication method not supported')

        try:
            payload = jwt.decode(token, settings.API_SECRET_KEY, algorithms=[settings.JWT_ALGORYTHM])

            self.enforce_csrf(request)
            user = User.objects.get(username=payload['username'])
            return user, token
        except jwt.DecodeError as e:
            raise exceptions.AuthenticationFailed('Invalid JWT token')
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('JWT token expired')

    @staticmethod
    def enforce_csrf(request):
        """
        Enforce CSRF validation
        """
        check = CSRFCheck()
        # populates request.META['CSRF_COOKIE'], which is used in process_view()
        check.process_request(request)
        reason = check.process_view(request, None, (), {})
        print(reason)
        if reason:
            # CSRF failed, bail with explicit error message
            raise exceptions.PermissionDenied('CSRF Failed: %s' % reason)
