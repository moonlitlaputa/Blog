from functools import wraps
from flask import g, request


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not g.current_user.can(permission):
                return {"message": "Insufficient permission"}, 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# def cached(timeout=5 * 60, key='%s'):
#     def decorator(f):
#         @wraps(f)
#         def decorated_function(*args, **kwargs):
#             cache_key = key % request.path
#             rv = cache.get(cache)
