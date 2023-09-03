from django.urls import path

from . import views

app_name = "idverification"

urlpatterns = [
    path("home/", views.home, name="home"),
    path("create_dir/", views.create_dir, name="create_dir"),
    path("<int:dir_id>/add_admin", views.add_admin, name="add_admin"),
    path("<int:dir_id>/identity_check_admin", views.identity_check_admin, name="identity_check_admin"),
    path("<int:dir_id>/select_user/", views.select_user, name="select_user"),
    path("<int:dir_id>/add_credentials/<int:client_id>", views.add_credentials, name="add_credentials"),
    path("<int:dir_id>/identity_check/<int:user_id>/<str:credentials_path>", views.identity_check, name="identity_check"),
    path('video_feed', views.video_feed, name='video_feed'),
    path('video_feed2', views.video_feed2, name='video_feed2'),
    path('identity_check2', views.identity_check2, name='identity_check2'),
    path('check_complete', views.check_complete, name='check_complete'),
    path('check_complete2', views.check_complete2, name='check_complete2'),
]
