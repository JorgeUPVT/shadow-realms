from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models


class CatRol(models.Model):
    nombre_rol = models.CharField(max_length=30, unique=True)
    descripcion = models.CharField(max_length=200, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "cat_rol"

    def __str__(self):
        return self.nombre_rol


class CatPais(models.Model):
    nombre = models.CharField(max_length=100)
    codigo_iso = models.CharField(max_length=2, unique=True)
    emoji_bandera = models.CharField(max_length=10, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "cat_pais"

    def __str__(self):
        return self.nombre


class CatPersonaje(models.Model):
    nombre = models.CharField(max_length=80)
    clase = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True)
    stat_fuerza = models.SmallIntegerField()
    stat_velocidad = models.SmallIntegerField()
    stat_magia = models.SmallIntegerField()
    stat_defensa = models.SmallIntegerField()
    hp_base = models.SmallIntegerField(default=250)
    energia_base = models.SmallIntegerField(default=100)
    companero = models.CharField(max_length=100, blank=True)
    sprite_key = models.CharField(max_length=50, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "cat_personaje"

    def __str__(self):
        return self.nombre


class UsuarioManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra):
        if not email:
            raise ValueError("El email es obligatorio")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        return self.create_user(username, email, password, **extra)


class Usuario(AbstractBaseUser, PermissionsMixin):
    id_rol = models.ForeignKey(CatRol, on_delete=models.RESTRICT, null=True, blank=True)
    id_pais = models.ForeignKey(
        CatPais, on_delete=models.SET_NULL, null=True, blank=True
    )
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=150, unique=True)
    nombre_mostrar = models.CharField(max_length=80, blank=True)
    biografia = models.TextField(blank=True)
    xp_total = models.IntegerField(default=0)
    nivel_cuenta = models.SmallIntegerField(default=1)
    partidas_jugadas = models.IntegerField(default=0)
    partidas_ganadas = models.IntegerField(default=0)
    estrellas_totales = models.IntegerField(default=0)
    titulo = models.CharField(max_length=100, blank=True)
    esta_baneado = models.BooleanField(default=False)
    acepto_terminos = models.BooleanField(default=False)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_ultimo_login = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    nivel_maximo_desbloqueado = models.SmallIntegerField(default=1)
    personaje_seleccionado = models.ForeignKey(
        "CatPersonaje",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="usuarios",
    )

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]
    objects = UsuarioManager()

    class Meta:
        db_table = "usuario"

    def __str__(self):
        return self.username


class ConfiguracionUsuario(models.Model):
    id_usuario = models.OneToOneField(
        Usuario, on_delete=models.CASCADE, related_name="configuracion"
    )
    volumen_general = models.SmallIntegerField(default=80)
    dificultad_default = models.CharField(max_length=20, default="NORMAL")
    perfil_visible = models.CharField(max_length=20, default="PUBLICO")
    mostrar_en_ranking = models.BooleanField(default=True)
    notificaciones_email = models.BooleanField(default=True)

    class Meta:
        db_table = "configuracion_usuario"


class Partida(models.Model):
    RESULTADO_CHOICES = [
        ("VICTORIA", "Victoria"),
        ("DERROTA", "Derrota"),
    ]
    id_usuario = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, related_name="partidas"
    )
    id_personaje = models.ForeignKey(
        CatPersonaje, on_delete=models.SET_NULL, null=True, blank=True
    )
    nivel_id = models.SmallIntegerField(default=1)
    resultado = models.CharField(max_length=10, choices=RESULTADO_CHOICES)
    score = models.IntegerField(default=0)
    xp_ganada = models.IntegerField(default=0)
    tiempo_segundos = models.IntegerField(default=0)
    estrellas = models.SmallIntegerField(default=0)

    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "partida"
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.id_usuario.username} - Nivel {self.nivel_id} - {self.resultado}"


class Logro(models.Model):
    clave = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=200)
    icono = models.CharField(max_length=10, default="🏅")
    xp_recompensa = models.IntegerField(default=100)

    class Meta:
        db_table = "logro"

    def __str__(self):
        return self.nombre


class LogroUsuario(models.Model):
    id_usuario = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, related_name="logros"
    )
    id_logro = models.ForeignKey(Logro, on_delete=models.CASCADE)
    fecha_obtenido = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "logro_usuario"
        unique_together = ("id_usuario", "id_logro")

    def __str__(self):
        return f"{self.id_usuario.username} - {self.id_logro.nombre}"
