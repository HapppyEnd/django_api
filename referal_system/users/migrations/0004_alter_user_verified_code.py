# Generated by Django 5.1.3 on 2024-11-30 20:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_rename_referal_code_user_reference_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='verified_code',
            field=models.CharField(blank=True, max_length=6, null=True),
        ),
    ]
