from django.urls import path

from . import views

app_name = "repository"
urlpatterns = [
    path("<int:dir_id>/", views.dir_content, name="dir_content"),
    path("<int:dir_id>/admin/", views.dir_admin, name="dir_admin"),
    path("<int:dir_id>/delete_content/<int:content_id>/", views.delete_img, name="delete_content"),
    path("<int:dir_id>/clients/", views.admin_clients, name="admin_clients"),
    path("<int:dir_id>/history/", views.check_history, name="check_history"),
    path("<int:attempt_id>/detail/", views.attempt_detail, name="attempt_detail"),
    path("<int:dir_id>/add_client/", views.add_client, name="add_client"),
    path("<int:dir_id>/delete_client/<int:client_id>", views.delete_client, name="delete_client"),
    path("<int:dir_id>/client/<int:client_id>", views.client_detail, name="client_detail"),
    path("<int:dir_id>/create_pass", views.create_pass, name="create_pass"),
]