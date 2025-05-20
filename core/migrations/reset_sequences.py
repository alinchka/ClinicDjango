from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0001_initial'),  # Замените на вашу последнюю миграцию
    ]

    operations = [
        migrations.RunSQL(
            "SELECT setval(pg_get_serial_sequence('core_doctor', 'id'), coalesce(max(id),0) + 1, false) FROM core_doctor;",
            reverse_sql="SELECT 1;"
        ),
    ] 