from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Avg, Sum
from django.utils import timezone
from datetime import timedelta
from .models import CatRol, CatPais, CatPersonaje, ConfiguracionUsuario, Usuario


def index(request):
    return render(request, "index.html")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("character_selection")
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None and not user.esta_baneado:
            login(request, user)
            return redirect("character_selection")
        messages.error(request, "Usuario o contraseña incorrectos / Cuenta bloqueada.")
    return render(request, "login.html")


def register_view(request):
    if request.user.is_authenticated:
        return redirect("character_selection")
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password")
        confirm = request.POST.get("confirm_password")
        pais_id = request.POST.get("id_pais")
        terminos = request.POST.get("acepto_terminos")

        if password != confirm:
            messages.error(request, "Las contraseñas no coinciden.")
        elif not terminos:
            messages.error(request, "Debes aceptar los términos y condiciones.")
        elif len(password) < 10:
            messages.error(request, "La contraseña debe tener al menos 10 caracteres.")
        elif Usuario.objects.filter(username=username).exists():
            messages.error(request, "Ese nombre de usuario ya existe.")
        elif Usuario.objects.filter(email=email).exists():
            messages.error(request, "Ese email ya está registrado.")
        else:
            rol = CatRol.objects.get(nombre_rol="JUGADOR")
            pais = CatPais.objects.filter(id=pais_id, activo=True).first()
            if not pais:
                messages.error(request, "País no válido.")
            else:
                user = Usuario.objects.create_user(
                    username=username, email=email, password=password
                )
                user.id_rol = rol
                user.id_pais = pais
                user.nombre_mostrar = username
                user.acepto_terminos = True
                user.save()
                ConfiguracionUsuario.objects.create(id_usuario=user)
                login(request, user)
                messages.success(request, "Registro exitoso. ¡Bienvenido!")
                return redirect("character_selection")

    paises = CatPais.objects.filter(activo=True)
    return render(request, "register.html", {"paises": paises})


def logout_view(request):
    logout(request)
    return redirect("index")


@login_required(login_url="/login/")
def character_selection(request):
    personajes = CatPersonaje.objects.filter(activo=True)
    return render(request, "character_selection.html", {"personajes": personajes})


@login_required(login_url="/login/")
def select_character(request):
    if request.method == "POST":
        personaje_id = request.POST.get("personaje_id")
        personaje = CatPersonaje.objects.filter(id=personaje_id, activo=True).first()
        if personaje:
            request.user.personaje_seleccionado = personaje
            request.user.save()
            return JsonResponse({"ok": True, "message": "Personaje seleccionado"})
        return JsonResponse({"ok": False, "message": "Personaje no encontrado"})
    return JsonResponse({"ok": False, "message": "Método no permitido"})


@login_required(login_url="/login/")
def profile(request):
    from .models import Partida, LogroUsuario

    historial = Partida.objects.filter(id_usuario=request.user).order_by("-fecha")[:10]
    logros = LogroUsuario.objects.filter(id_usuario=request.user).select_related(
        "id_logro"
    )
    return render(
        request,
        "profile.html",
        {
            "usuario": request.user,
            "historial": historial,
            "logros": logros,
        },
    )


@login_required(login_url="/login/")
def level_selection(request):
    return render(
        request,
        "level_selection.html",
        {
            "nivel_desbloqueado": request.user.nivel_maximo_desbloqueado,
        },
    )


@login_required(login_url="/login/")
def leaderboard(request):
    base_qs = Usuario.objects.filter(esta_baneado=False, is_active=True).select_related(
        "id_pais", "personaje_seleccionado"
    )
    try:
        jugadores_qs = base_qs.filter(configuracion__mostrar_en_ranking=True)
    except:
        jugadores_qs = base_qs

    jugadores = jugadores_qs.order_by("-xp_total")[:20]
    top3 = list(jugadores_qs.order_by("-xp_total")[:3])

    tu_posicion = None
    if request.user in jugadores:
        tu_posicion = list(jugadores).index(request.user) + 1

    return render(
        request,
        "leaderboard.html",
        {
            "jugadores": jugadores,
            "top3": top3,
            "tu_posicion": tu_posicion,
        },
    )


@login_required(login_url="/login/")
def settings_view(request):
    if request.method == "POST":
        accion = request.POST.get("accion")

        if accion == "cambiar_password":
            current = request.POST.get("current_password")
            new_pass = request.POST.get("new_password")
            confirm = request.POST.get("confirm_password")
            user = authenticate(
                request, username=request.user.username, password=current
            )
            if not user:
                messages.error(request, "Contraseña actual incorrecta.")
            elif new_pass != confirm:
                messages.error(request, "Las contraseñas no coinciden.")
            elif len(new_pass) < 10:
                messages.error(
                    request, "La nueva contraseña debe tener al menos 10 caracteres."
                )
            else:
                request.user.set_password(new_pass)
                request.user.save()
                messages.success(request, "Contraseña cambiada correctamente.")

        elif accion == "actualizar_perfil":
            email = request.POST.get("email", "").strip()
            pais_id = request.POST.get("id_pais")
            bio = request.POST.get("bio", "").strip()[:200]
            pais = CatPais.objects.filter(id=pais_id, activo=True).first()

            if not email:
                messages.error(request, "El email es obligatorio.")
            elif (
                Usuario.objects.exclude(pk=request.user.pk).filter(email=email).exists()
            ):
                messages.error(request, "Ese email ya está en uso.")
            elif not pais:
                messages.error(request, "País no válido.")
            else:
                request.user.email = email
                request.user.biografia = bio
                request.user.id_pais = pais
                request.user.save(update_fields=["email", "biografia", "id_pais"])
                messages.success(request, "Perfil actualizado correctamente.")

        return redirect("settings")

    paises = CatPais.objects.filter(activo=True)
    return render(request, "settings.html", {"usuario": request.user, "paises": paises})


@login_required(login_url="/login/")
def game_view(request):
    nivel_id = request.GET.get("nivel", 1)
    niveles = {
        "1": {
            "nombre": "Nivel 1: Pantano Maldito",
            "boss": "Vorgath el Sapo",
            "emoji": "🐸",
        },
        "2": {
            "nombre": "Nivel 2: Montañas Congeladas",
            "boss": "Ursagor el Oso Polar",
            "emoji": "🐻",
        },
        "3": {
            "nombre": "Nivel 3: Bosque de Sombras",
            "boss": "Nyx la Sombra Viviente",
            "emoji": "🌑",
        },
        "4": {
            "nombre": "Nivel 4: Ruinas Antiguas",
            "boss": "Kael el Centauro Oscuro",
            "emoji": "💀",
        },
        "5": {
            "nombre": "Nivel 5: Castillo del Dragón",
            "boss": "Malakor el Rey Sombra",
            "emoji": "🐉",
        },
    }
    nivel = niveles.get(str(nivel_id), niveles["1"])
    return render(
        request,
        "game.html",
        {
            "nivel_id": nivel_id,
            "nivel_nombre": nivel["nombre"],
            "boss_nombre": nivel["boss"],
            "boss_emoji": nivel["emoji"],
        },
    )


# ─── Helpers (sin decoradores) ───────────────────────────────────────────────


def calcular_estrellas(score, tiempo_segundos):
    estrellas = 1
    if score >= 500:
        estrellas = 2
    if score >= 1000:
        estrellas = 3
    if score >= 1500 and tiempo_segundos <= 120:
        estrellas = 4
    if score >= 2000 and tiempo_segundos <= 60:
        estrellas = 5
    return estrellas


def otorgar_logros(usuario, partida):
    from .models import Logro, LogroUsuario, Partida

    logros_nuevos = []

    def dar(clave):
        try:
            logro = Logro.objects.get(clave=clave)
            _, creado = LogroUsuario.objects.get_or_create(
                id_usuario=usuario, id_logro=logro
            )
            if creado:
                logros_nuevos.append({"nombre": logro.nombre, "icono": logro.icono})
                usuario.xp_total += logro.xp_recompensa
        except Logro.DoesNotExist:
            pass

    if usuario.partidas_ganadas == 1:
        dar("primer_victoria")
    if usuario.partidas_ganadas >= 10:
        dar("victorias_10")
    if usuario.partidas_ganadas >= 25:
        dar("victorias_25")
    if usuario.nivel_cuenta >= 3:
        dar("nivel_3")
    if usuario.nivel_cuenta >= 5:
        dar("nivel_5")
    if partida.nivel_id == 5 and partida.resultado == "VICTORIA":
        dar("nivel_5_juego")
    if usuario.estrellas_totales >= 15:
        dar("estrellas_15")
    if partida.tiempo_segundos <= 30 and partida.resultado == "VICTORIA":
        dar("velocista")

    ultimas = Partida.objects.filter(id_usuario=usuario).order_by("-fecha")[:3]
    if ultimas.count() == 3 and all(p.resultado == "VICTORIA" for p in ultimas):
        dar("racha_3")

    if logros_nuevos:
        usuario.save(update_fields=["xp_total"])

    return logros_nuevos


# ─── Vista guardar partida ────────────────────────────────────────────────────


@login_required(login_url="/login/")
def save_game_result(request):
    if request.method == "POST":
        from .models import Partida
        from django.db import connection

        resultado = request.POST.get("resultado")
        score = int(request.POST.get("score", 0))
        nivel_id = int(request.POST.get("nivel_id", 1))
        tiempo = int(request.POST.get("tiempo", 0))
        xp_ganada = 0
        estrellas = calcular_estrellas(score, tiempo)

        if resultado == "victoria":
            xp_ganada = 500 + score
            request.user.xp_total += xp_ganada
            request.user.partidas_ganadas += 1
            request.user.estrellas_totales += estrellas
            if nivel_id >= request.user.nivel_maximo_desbloqueado:
                request.user.nivel_maximo_desbloqueado = nivel_id + 1

        request.user.partidas_jugadas += 1
        nuevo_nivel = (request.user.xp_total // 1000) + 1
        request.user.nivel_cuenta = min(nuevo_nivel, 99)

        request.user.save(
            update_fields=[
                "xp_total",
                "partidas_ganadas",
                "partidas_jugadas",
                "estrellas_totales",
                "nivel_maximo_desbloqueado",
                "nivel_cuenta",
            ]
        )

        partida = Partida.objects.create(
            id_usuario=request.user,
            id_personaje=request.user.personaje_seleccionado,
            nivel_id=nivel_id,
            resultado=resultado.upper(),
            score=score,
            xp_ganada=xp_ganada,
            tiempo_segundos=tiempo,
        )

        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE partida SET estrellas = %s WHERE id = %s",
                [estrellas if resultado == "victoria" else 0, partida.pk],
            )

        logros_nuevos = (
            otorgar_logros(request.user, partida) if resultado == "victoria" else []
        )

        return JsonResponse(
            {
                "ok": True,
                "xp_ganada": xp_ganada,
                "estrellas": estrellas if resultado == "victoria" else 0,
                "nivel_nuevo": request.user.nivel_cuenta,
                "logros_nuevos": logros_nuevos,
            }
        )
    return JsonResponse({"ok": False})


# ─── Admin ────────────────────────────────────────────────────────────────────


def is_admin(user):
    return user.is_staff or user.is_superuser


@login_required(login_url="/login/")
@user_passes_test(is_admin, login_url="index", redirect_field_name=None)
def admin_dashboard(request):
    total_usuarios = Usuario.objects.count()
    usuarios_activos = Usuario.objects.filter(is_active=True).count()
    usuarios_esta_semana = Usuario.objects.filter(
        fecha_registro__gte=timezone.now() - timedelta(days=7)
    ).count()
    partidas_totales = (
        Usuario.objects.aggregate(total=Sum("partidas_jugadas"))["total"] or 0
    )
    nivel_promedio = Usuario.objects.aggregate(avg=Avg("nivel_cuenta"))["avg"] or 0

    nuevos_por_dia = []
    for i in range(6, -1, -1):
        dia = timezone.now().date() - timedelta(days=i)
        count = Usuario.objects.filter(fecha_registro__date=dia).count()
        nuevos_por_dia.append(count)

    max_nuevos = max(nuevos_por_dia) if nuevos_por_dia else 1
    alturas_grafico = [
        round((c / max_nuevos) * 100) if max_nuevos > 0 else 0 for c in nuevos_por_dia
    ]

    personajes_populares = (
        CatPersonaje.objects.annotate(num_usuarios=Count("usuarios"))
        .filter(num_usuarios__gt=0)
        .order_by("-num_usuarios")[:5]
    )
    personajes_con_pct = [
        {
            "nombre": p.nombre,
            "num_usuarios": p.num_usuarios,
            "porcentaje": (
                round(p.num_usuarios / total_usuarios * 100, 1)
                if total_usuarios > 0
                else 0
            ),
        }
        for p in personajes_populares
    ]
    actividad_reciente = Usuario.objects.order_by("-fecha_registro")[:10]
    grafico_data = list(zip(nuevos_por_dia, alturas_grafico))

    return render(
        request,
        "admin_dashboard.html",
        {
            "total_usuarios": total_usuarios,
            "usuarios_activos": usuarios_activos,
            "usuarios_esta_semana": usuarios_esta_semana,
            "partidas_totales": partidas_totales,
            "nivel_promedio": round(nivel_promedio, 1) if nivel_promedio else 0,
            "grafico_data": grafico_data,
            "personajes_populares": personajes_con_pct,
            "actividad_reciente": actividad_reciente,
            "admin_user": request.user.nombre_mostrar or request.user.username,
        },
    )


@login_required(login_url="/login/")
@user_passes_test(is_admin, login_url="index", redirect_field_name=None)
def admin_users(request):
    usuarios = Usuario.objects.select_related(
        "id_pais", "personaje_seleccionado"
    ).order_by("-fecha_registro")
    return render(request, "admin_users.html", {"usuarios": usuarios})


@login_required(login_url="/login/")
@user_passes_test(is_admin, login_url="index", redirect_field_name=None)
def admin_leaderboard(request):
    top_jugadores = Usuario.objects.select_related(
        "id_pais", "personaje_seleccionado"
    ).order_by("-xp_total")[:100]
    return render(request, "admin_leaderboard.html", {"top_jugadores": top_jugadores})


@login_required(login_url="/login/")
@user_passes_test(is_admin, login_url="index", redirect_field_name=None)
def admin_reports(request):
    return render(
        request,
        "admin_reports.html",
        {
            "titulo": "Reportes",
            "total_usuarios": Usuario.objects.count(),
            "total_partidas": Usuario.objects.aggregate(total=Sum("partidas_jugadas"))[
                "total"
            ]
            or 0,
        },
    )
