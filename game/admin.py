from django.contrib import admin
from .models import Usuario, CatRol, CatPais, CatPersonaje, ConfiguracionUsuario


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = [
        "username",
        "email",
        "id_rol",
        "nivel_cuenta",
        "esta_baneado",
        "fecha_registro",
    ]
    list_filter = ["esta_baneado", "id_rol"]
    search_fields = ["username", "email"]
    actions = ["banear_usuarios", "desbanear_usuarios"]

    def banear_usuarios(self, request, queryset):
        queryset.update(esta_baneado=True)

    banear_usuarios.short_description = "Banear usuarios seleccionados"

    def desbanear_usuarios(self, request, queryset):
        queryset.update(esta_baneado=False)

    desbanear_usuarios.short_description = "Desbanear usuarios seleccionados"


@admin.register(CatRol)
class CatRolAdmin(admin.ModelAdmin):
    list_display = ["nombre_rol", "descripcion", "activo"]


@admin.register(CatPais)
class CatPaisAdmin(admin.ModelAdmin):
    list_display = ["nombre", "codigo_iso", "emoji_bandera", "activo"]
    search_fields = ["nombre", "codigo_iso"]


@admin.register(CatPersonaje)
class CatPersonajeAdmin(admin.ModelAdmin):
    list_display = [
        "nombre",
        "clase",
        "stat_fuerza",
        "stat_velocidad",
        "stat_magia",
        "stat_defensa",
        "activo",
    ]


@admin.register(ConfiguracionUsuario)
class ConfiguracionUsuarioAdmin(admin.ModelAdmin):
    list_display = ["id_usuario", "dificultad_default", "perfil_visible"]
