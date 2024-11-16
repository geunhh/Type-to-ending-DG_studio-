
import requests
from django.conf import settings
from django.shortcuts import redirect,render
from django.contrib.auth import get_user_model, login
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.decorators import login_required


User = get_user_model()



class KakaoLogin(View):
    def get(self, request):
        kakao_auth_url = (
            "https://kauth.kakao.com/oauth/authorize"
            f"?client_id={settings.KAKAO_REST_API_KEY}"
            f"&redirect_uri={settings.KAKAO_REDIRECT_URI}"
            f"&response_type=code"
        )
        return JsonResponse({"login_url": kakao_auth_url})
    
class KakaoCallback(View):
    def get(self, request):
        code = request.GET.get("code")
        if not code:
            return JsonResponse({"error": "Authorization code is missing"}, status=400)

        # Access Token 요청
        token_url = "https://kauth.kakao.com/oauth/token"
        token_data = {
            "grant_type": "authorization_code",
            "client_id": settings.KAKAO_REST_API_KEY,
            "redirect_uri": settings.KAKAO_REDIRECT_URI,
            "code": code,
        }
        token_headers = {"Content-Type": "application/x-www-form-urlencoded"}
        token_response = requests.post(token_url, data=token_data, headers=token_headers)
        token_json = token_response.json()

        access_token = token_json.get("access_token")
        if not access_token:
            return JsonResponse({"error": "Failed to retrieve access token"}, status=400)

        # 사용자 정보 요청
        user_info_url = "https://kapi.kakao.com/v2/user/me"
        headers = {"Authorization": f"Bearer {access_token}"}
        user_info_response = requests.get(user_info_url, headers=headers)
        user_info = user_info_response.json()

        # 사용자 정보 추출
        kakao_id = user_info["id"]
        profile = user_info["kakao_account"]["profile"]
        nickname = profile.get("nickname")
        profile_image = profile.get("profile_image_url")

        # 사용자 생성 또는 로그인 처리
        user, created = User.objects.get_or_create(kakao_id=kakao_id)
        if created:
            user.username = nickname
            user.nickname = nickname
            user.profile_image = profile_image
            user.save()

        login(request, user)
        return redirect("profile")
    
def profile_view(request):
    return render(request, 'accounts/profile.html', {
        'user': request.user,  # 인증된 사용자 객체를 템플릿에 전달
    })
    
