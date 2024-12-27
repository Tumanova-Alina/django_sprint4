from django.urls import path

from . import views


app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(), name='index'),
    path('posts/<int:pk>/', views.post_detail, name='post_detail'),
    path('category/<slug:category_slug>/',
         views.category_posts, name='category_posts'),
    path('posts/<int:pk>/edit/',
         views.PostUpdateView.as_view(), name='edit_post'),
    path('posts/create/', views.PostCreateView.as_view(), name='create_post'),
    path('posts/<int:pk>/delete/',
         views.PostDeleteView.as_view(), name='delete_post'),
    path('profile/<slug:username>/delete/',
         views.ProfileDeleteView.as_view(), name='delete'),
    path('profile/<slug:username>/edit/', views.ProfileUpdateView.as_view(),
         name='edit_profile'),
    path('profile/<slug:username>/', views.ProfileDetailView.as_view(),
         name='profile'),
    path('posts/<int:pk>/comments/', views.CommentListView.as_view(),
         name='view_comments'),
    path('posts/<int:pk>/edit_comment/<comment_id>/',
         views.CommentUpdateView.as_view(), name='edit_comment'),
    path('posts/<int:pk>/delete_comment/<comment_id>/',
         views.CommentDeleteView.as_view(),
         name='delete_comment'),
    path('posts/<int:pk>/comment/', views.CommentCreateView.as_view(),
         name='add_comment'),
]
