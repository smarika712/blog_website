from functools import wraps

from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth.models import User

from .auth_utils import decode_token, TokenError


def token_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        # Get access token from cookie
        token = request.COOKIES.get(
            settings.ACCESS_TOKEN_COOKIE
        )

        # No access token
        if not token:
            return redirect('login')


        try:
            # Decode JWT token
            payload = decode_token(
                token,
                'access'
            )

            # Get user from token
            user = User.objects.get(
                id=payload.get('user_id')
            )

            # Attach user to request
            request.user = user


        except (TokenError, User.DoesNotExist):
            return redirect('login')


        return view_func(
            request,
            *args,
            **kwargs
        )

    return wrapper