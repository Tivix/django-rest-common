from django.conf import settings

from rest_framework.authentication import TokenAuthentication as BaseTokenAuthentication
from rest_framework import exceptions, HTTP_HEADER_ENCODING


class TokenAuthentication(BaseTokenAuthentication):

    header_name = getattr(settings, 'CUSTOM_TOKEN_HEADER_NAME',
        'HTTP_API_AUTHORIZATION')

    def get_authorization_header(self, request):
        auth = request.META.get(self.header_name, b'')

        # this is added to enable testing API in swagger on DEVs
        if (settings.IS_DEV or settings.IS_STAGING) and not auth:
            auth = request.META.get('HTTP_AUTHORIZATION', b'')
        if isinstance(auth, type('')):
            auth = auth.encode(HTTP_HEADER_ENCODING)
        return auth

    def authenticate(self, request):
        auth = self.get_authorization_header(request).split()

        if not auth or auth[0].lower() != b'token':
            return None

        if len(auth) == 1:
            msg = 'Invalid token header. No credentials provided.'
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = 'Invalid token header. Token string should not contain spaces.'
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(auth[1])
