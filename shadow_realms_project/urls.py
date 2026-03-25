from django.contrib import admin
from django.urls import path
from game import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("seleccion/", views.character_selection, name="character_selection"),
    path("perfil/", views.profile, name="profile"),
    path("niveles/", views.level_selection, name="level_selection"),
    path("ranking/", views.leaderboard, name="leaderboard"),
    path("configuracion/", views.settings_view, name="settings"),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("panel/usuarios/", views.admin_users, name="admin_users"),
    path("panel/leaderboard/", views.admin_leaderboard, name="admin_leaderboard"),
    path("panel/reports/", views.admin_reports, name="admin_reports"),
    path("seleccionar-personaje/", views.select_character, name="select_character"),
    path("juego/", views.game_view, name="game"),
    path("juego/guardar/", views.save_game_result, name="save_game_result"),
]
