# Generated by Django 3.2.12 on 2022-04-13 16:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0007_alter_comment_description'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='contributor',
            constraint=models.UniqueConstraint(condition=models.Q(('role', 'm')), fields=('project',), name='unique_project_manager'),
        ),
    ]