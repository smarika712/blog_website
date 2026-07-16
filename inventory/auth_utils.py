
import jwt
import datetime
from django.conf import settings
from django.contrib.auth.models import User


def _now():
    return datetime.datetime.utcnow()


def generate_access_token(user):
    payload = {
        'user_id': user.id,
        'username': user.username,
        'type': 'access',
        'iat': _now(),
        'exp': _now() + settings.ACCESS_TOKEN_LIFETIME,
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def generate_refresh_token(user):
    payload = {
        'user_id': user.id,
        'type': 'refresh',
        'iat': _now(),
        'exp': _now() + settings.REFRESH_TOKEN_LIFETIME,
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


class TokenError(Exception):
    """Raised when a token is missing, expired, or invalid."""


def decode_token(token, expected_type):
    if not token:
        raise TokenError('Token missing.')
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise TokenError('Token expired.')
    except jwt.InvalidTokenError:
        raise TokenError('Invalid token.')

    if payload.get('type') != expected_type:
        raise TokenError('Wrong token type.')
    return payload


def get_user_from_access_token(token):
    try:
        payload = decode_token(token, 'access')
    except TokenError:
        return None
    return User.objects.filter(id=payload.get('user_id')).first()


def set_auth_cookies(response, user):
    """Attach fresh access + refresh token cookies to a response."""
    access_token = generate_access_token(user)
    refresh_token = generate_refresh_token(user)

    response.set_cookie(
        settings.ACCESS_TOKEN_COOKIE, access_token,
        httponly=True, samesite='Lax',
        max_age=int(settings.ACCESS_TOKEN_LIFETIME.total_seconds()),
    )
    response.set_cookie(
        settings.REFRESH_TOKEN_COOKIE, refresh_token,
        httponly=True, samesite='Lax',
        max_age=int(settings.REFRESH_TOKEN_LIFETIME.total_seconds()),
    )
    return response


def clear_auth_cookies(response):
    response.delete_cookie(settings.ACCESS_TOKEN_COOKIE)
    response.delete_cookie(settings.REFRESH_TOKEN_COOKIE)
    return response