import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Crea o actualiza el usuario de la app desde APP_USERNAME y APP_PASSWORD.'

    def handle(self, *args, **options):
        username = os.environ.get('APP_USERNAME', 'vetadmin').strip()
        password = os.environ.get('APP_PASSWORD', '').strip()

        if not password:
            self.stdout.write(
                'APP_PASSWORD no definido: no se creó usuario. '
                'Definilo en Railway o usá createsuperuser.'
            )
            return

        User = get_user_model()
        user, created = User.objects.get_or_create(
            username=username,
            defaults={'is_staff': False, 'is_superuser': False},
        )
        user.set_password(password)
        user.is_active = True
        user.save()

        verb = 'creado' if created else 'actualizado'
        self.stdout.write(self.style.SUCCESS(f'Usuario "{username}" {verb}.'))
