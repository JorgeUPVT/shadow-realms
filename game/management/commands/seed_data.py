from django.core.management.base import BaseCommand
from game.models import CatRol, CatPais, CatPersonaje


class Command(BaseCommand):
    help = "Carga datos iniciales de catálogos"

    def handle(self, *args, **kwargs):
        # Roles
        CatRol.objects.get_or_create(
            nombre_rol="ADMIN", defaults={"descripcion": "Administrador"}
        )
        CatRol.objects.get_or_create(
            nombre_rol="JUGADOR", defaults={"descripcion": "Jugador estándar"}
        )
        CatRol.objects.get_or_create(
            nombre_rol="MODERADOR", defaults={"descripcion": "Moderador"}
        )
        self.stdout.write("Roles creados")

        # Países
        paises = [
            ("México", "MX", "🇲🇽"),
            ("Estados Unidos", "US", "🇺🇸"),
            ("España", "ES", "🇪🇸"),
            ("Argentina", "AR", "🇦🇷"),
            ("Colombia", "CO", "🇨🇴"),
            ("Chile", "CL", "🇨🇱"),
            ("Brasil", "BR", "🇧🇷"),
            ("Perú", "PE", "🇵🇪"),
            ("Venezuela", "VE", "🇻🇪"),
            ("Ecuador", "EC", "🇪🇨"),
            ("Guatemala", "GT", "🇬🇹"),
            ("Cuba", "CU", "🇨🇺"),
            ("Bolivia", "BO", "🇧🇴"),
            ("Honduras", "HN", "🇭🇳"),
            ("Paraguay", "PY", "🇵🇾"),
            ("El Salvador", "SV", "🇸🇻"),
            ("Nicaragua", "NI", "🇳🇮"),
            ("Costa Rica", "CR", "🇨🇷"),
            ("Uruguay", "UY", "🇺🇾"),
            ("Panamá", "PA", "🇵🇦"),
            ("Reino Unido", "GB", "🇬🇧"),
            ("Alemania", "DE", "🇩🇪"),
            ("Francia", "FR", "🇫🇷"),
            ("Italia", "IT", "🇮🇹"),
            ("Japón", "JP", "🇯🇵"),
            ("Canadá", "CA", "🇨🇦"),
            ("Australia", "AU", "🇦🇺"),
            ("Portugal", "PT", "🇵🇹"),
            ("Corea del Sur", "KR", "🇰🇷"),
            ("Otro", "XX", ""),
        ]
        for nombre, iso, emoji in paises:
            CatPais.objects.get_or_create(
                codigo_iso=iso, defaults={"nombre": nombre, "emoji_bandera": emoji}
            )
        self.stdout.write("Países creados")

        # Personajes
        personajes = [
            (
                "El Caballero Oscuro",
                "Guerrero",
                9,
                6,
                4,
                8,
                280,
                80,
                "Lobo Espectral",
                "knight",
            ),
            (
                "La Hechicera de Sombras",
                "Maga",
                4,
                7,
                10,
                5,
                180,
                130,
                "Cuervo Místico",
                "mage",
            ),
            (
                "El Arquero Fantasma",
                "Cazador",
                6,
                10,
                6,
                4,
                200,
                100,
                "Zorro Plateado",
                "archer",
            ),
            (
                "El Paladín de Luz",
                "Protector",
                8,
                5,
                7,
                9,
                260,
                100,
                "Unicornio Blanco",
                "paladin",
            ),
        ]
        for n, c, f, v, m, d, hp, en, comp, key in personajes:
            CatPersonaje.objects.get_or_create(
                sprite_key=key,
                defaults={
                    "nombre": n,
                    "clase": c,
                    "stat_fuerza": f,
                    "stat_velocidad": v,
                    "stat_magia": m,
                    "stat_defensa": d,
                    "hp_base": hp,
                    "energia_base": en,
                    "companero": comp,
                },
            )
        self.stdout.write(" Personajes creados")

        self.stdout.write(
            self.style.SUCCESS("🎮 Datos iniciales cargados correctamente")
        )
