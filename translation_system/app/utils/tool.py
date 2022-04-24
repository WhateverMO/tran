import functools
from flask import session, jsonify, g, make_response
from datetime import timedelta
from flask import current_app, request


# 验证登录状态的“装饰器”
def user_login_required(view_func):
    @functools.wraps(view_func)
    def wrapper(*args, **kwargs):
        # 判断用户登陆状态
        user_name = session.get("username")
        # 如果用户是登陆的，则执行该视图函数
        if user_name is not None:
            # 将user_id保存到g对象中，在视图函数中可以通过g对象获取保存数据
            g.user_name = user_name
            return view_func(*args, **kwargs)
        else:
            # 如果未登录，返回未登录信息
            return jsonify(msg="该用户未登录", code=4000)

    return wrapper


def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, str):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, str):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return functools.update_wrapper(wrapped_function, f)
    return decorator
