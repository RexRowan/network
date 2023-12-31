from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new_post", views.newPost, name="new_post"),  # Consider renaming the view to new_post as well
    path("profile/<int:user_id>", views.profile, name="profile"),
    path("follow", views.follow, name="follow"),  # This now toggles follow/unfollow
    path("following", views.following, name="following"),
    path("edit/<int:post_id>", views.edit, name="edit"),
    path("toggle_like/<int:post_id>", views.toggle_like, name="toggle_like"),  # New path for like/unlike
]
