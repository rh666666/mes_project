"""System 应用中间件

包含当前用户中间件，用于自动处理审计字段。
"""

from utils.current_user import clear_current_user, set_current_user


class CurrentUserMiddleware:
    """当前用户中间件

    在每个请求开始时将当前用户存入线程本地存储，
    请求结束后清理，用于模型审计字段自动填充。
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        set_current_user(getattr(request, "user", None))
        response = self.get_response(request)
        clear_current_user()
        return response
