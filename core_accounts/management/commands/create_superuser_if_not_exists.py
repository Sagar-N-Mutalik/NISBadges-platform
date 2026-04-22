import os
from django.core.management.base import BaseCommand
from core_accounts.models import CoreUser

class Command(BaseCommand):
    help = 'Creates a superuser automatically using environment variables.'

    def handle(self, *args, **options):
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "admin@nisbadges.com")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

        if not password:
            self.stdout.write(self.style.ERROR("SUPERUSER PASSWORD NOT SET. Skipping creation."))
            return

        # Check if the user already exists to prevent integrity errors
        if not CoreUser.objects.filter(email=email).exists():
            CoreUser.objects.create_superuser(
                email=email,
                password=password,
                full_name="System Administrator" 
            )
            self.stdout.write(self.style.SUCCESS(f"Successfully created superuser: {email}"))
        else:
            self.stdout.write(self.style.WARNING(f"Superuser {email} already exists. Skipping."))