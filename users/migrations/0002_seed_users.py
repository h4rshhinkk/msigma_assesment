from django.db import migrations
from django.contrib.auth.hashers import make_password


def create_users(apps, schema_editor):
    User = apps.get_model("users", "User")

    if not User.objects.filter(email="admin@test.com").exists():
        User.objects.create(
            email="admin@test.com",
            password=make_password("admin123"),
            role="ADMIN",
            is_staff=True,
            is_superuser=True,
            is_active=True
        )

    if not User.objects.filter(email="reviewer@test.com").exists():
        User.objects.create(
            email="reviewer@test.com",
            password=make_password("review123"),
            role="REVIEWER",
            is_staff=False,
            is_superuser=False,
            is_active=True
        )


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_users),
    ]