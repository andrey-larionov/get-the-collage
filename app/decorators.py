from functools import wraps
from flask import request, redirect, session


def access_token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'instagram_access_token' not in session:
            return redirect('/connect')
        return f(*args, **kwargs)
    return decorated_function
