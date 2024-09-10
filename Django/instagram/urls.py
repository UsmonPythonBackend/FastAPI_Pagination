from django.contrib import admin
from django.urls import path, include
from .views import HomeView, PostsView, CommentsView, LikesView, FollowersView


urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('posts/', PostsView.as_view(), name='posts'),
    path('comments/', CommentsView.as_view(), name='comments'),
    path('likes/', LikesView.as_view(), name='like'),
    path('followers/', FollowersView.as_view(), name='follower'),

]
