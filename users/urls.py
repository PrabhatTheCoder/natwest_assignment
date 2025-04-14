from django.urls import path
from .views import RegisterUserView, LoginUserView, LogoutUserView, GetAccessTokenView

urlpatterns = [
    path('register/',RegisterUserView.as_view()),
    path('get-access-token/', GetAccessTokenView.as_view()), 
    path('login/', LoginUserView.as_view()),
    path('logout/', LogoutUserView.as_view())
]
