# Generated by Django 4.1.7 on 2023-03-22 13:17

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("training_service", "0003_responsehistory_question"),
    ]

    operations = [
        migrations.RenameField(
            model_name="comment",
            old_name="theory",
            new_name="text",
        ),
    ]