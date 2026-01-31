from django.contrib.auth import authenticate, login
from rest_framework import status
from dj_rest_auth.views import LoginView
from dj_rest_auth.registration.views import RegisterView
from rest_framework_simplejwt.tokens import RefreshToken
from utils import DetailResponse, ErrorResponse


class CustomLoginView(LoginView):
    """自定义登录视图"""

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return ErrorResponse(msg='用户名和密码不能为空', status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, username=username, password=password)

        if user is None:
            return ErrorResponse(msg='用户名或密码错误', status=status.HTTP_401_UNAUTHORIZED)

        login(request, user)

        refresh = RefreshToken.for_user(user)

        data = {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'csrf_token': request.META.get('CSRF_COOKIE'),
        }
        return DetailResponse(data=data)


class CustomLogoutView(LoginView):
    """自定义注销视图"""

    def post(self, request, *args, **kwargs):
        from django.contrib.auth import logout
        try:
            logout(request)
            return DetailResponse(data=None, msg='退出成功')
        except Exception as e:
            return ErrorResponse(msg=str(e), status=status.HTTP_400_BAD_REQUEST)


class CustomRegisterView(RegisterView):
    """自定义注册视图"""

    def create(self, request, *args, **kwargs):
        from django.contrib.auth import get_user_model
        User = get_user_model()

        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        name = request.data.get('name', '')

        if not username or not password:
            return ErrorResponse(msg='用户名和密码不能为空', status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return ErrorResponse(msg='用户名已存在', status=status.HTTP_400_BAD_REQUEST)

        if email and User.objects.filter(email=email).exists():
            return ErrorResponse(msg='邮箱已被注册', status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.create_user(
                username=username,
                email=email or '',
                password=password,
                name=name,
            )
        except Exception as e:
            return ErrorResponse(msg=str(e), status=status.HTTP_400_BAD_REQUEST)

        data = {
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'name': user.name,
            }
        }
        return DetailResponse(data=data)
