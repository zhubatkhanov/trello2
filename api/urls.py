from django.urls import path
from .views import RegisterView, LoginView, UserView, LogoutView
from .views import BoardListCreate, BoardDetail, ListCardListCreate, ListCardDetail, MoveListView
from .views import CardListCreate, CardDetail, UserDetailView



urlpatterns = [
    path('register', RegisterView.as_view()),
    path('login', LoginView.as_view()),
    path('user', UserView.as_view()),
    path('logout', LogoutView.as_view()),
    path('users/<int:pk>', UserDetailView.as_view()),
    
    path('board', BoardListCreate.as_view()),
    path('boards/<int:pk>', BoardDetail.as_view()),
    
    path('list', ListCardListCreate.as_view()),
    path('lists/<int:pk>', ListCardDetail.as_view()),
    path('movelist/<int:pk>', MoveListView.as_view()),
    
    path('card', CardListCreate.as_view()),
    path('cards/<int:pk>', CardDetail.as_view()),
]