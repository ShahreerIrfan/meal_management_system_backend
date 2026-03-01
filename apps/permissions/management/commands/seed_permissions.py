"""
Management command to seed all permissions.
Run: python manage.py seed_permissions
"""
from django.core.management.base import BaseCommand
from apps.permissions.services import seed_permissions


class Command(BaseCommand):
    help = "Seed all application permissions into AppPermission table."

    def handle(self, *args, **options):
        seed_permissions()
        self.stdout.write(self.style.SUCCESS("Permissions seeded successfully."))
