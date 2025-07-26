from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework.response import Response


class CookieTokenObtainPairView(TokenObtainPairView):
  def post(self, request, *args, **kwargs):
    response = super().post(request, *args, **kwargs)
    refresh = response.data.get('refresh')

    if refresh:
      response.set_cookie(
        key="refresh_token",
        value=refresh,
        httponly=True,
        secure=False,
        samesite="Lax",
        max_age=7 * 24 * 60 * 60,
      )
    return response


class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):

        refresh_token = request.COOKIES.get('refresh_token')

        if refresh_token:
            request.data['refresh'] = refresh_token

        response = super().post(request, *args, **kwargs)    
        return response
