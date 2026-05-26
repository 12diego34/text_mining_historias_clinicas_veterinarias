import shutil
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand

from fichas.models import Ficha


class Command(BaseCommand):
    help = 'Carga fichas demo y PDFs desde seed/ si la base está vacía (p. ej. primer deploy en Railway).'

    def handle(self, *args, **options):
        if Ficha.objects.exists():
            self.stdout.write('Ya hay fichas en la base; seed omitido.')
            return

        seed_uploads = Path(settings.BASE_DIR) / 'seed' / 'uploads'
        media_uploads = Path(settings.MEDIA_ROOT) / 'uploads'
        if seed_uploads.is_dir():
            shutil.copytree(seed_uploads, media_uploads, dirs_exist_ok=True)
            self.stdout.write(f'PDFs copiados a {media_uploads}')

        fixture = Path(settings.BASE_DIR) / 'fixtures' / 'fichas_demo.json'
        if not fixture.is_file():
            self.stderr.write(self.style.ERROR(f'No existe {fixture}'))
            return

        call_command('loaddata', str(fixture))
        self.stdout.write(self.style.SUCCESS(f'Cargadas {Ficha.objects.count()} fichas demo.'))
