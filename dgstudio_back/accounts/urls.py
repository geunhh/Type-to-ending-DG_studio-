from django.urls import path
from .views import KakaoLogin, KakaoCallback, profile_view

urlpatterns = [
    path('login/', KakaoLogin.as_view(), name='login'),
    path('callback/', KakaoCallback.as_view(), name='kakao-callback'),
    path('profile/', profile_view, name='profile'),
]