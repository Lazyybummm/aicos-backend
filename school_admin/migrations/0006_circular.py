# school_admin/migrations/000X_circular.py
# Rename this file to the next sequential number in your migrations folder.
# e.g. if the last one is 0003_..., name this 0004_circular.py

import uuid
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        # ← Replace '0003_...' with whatever your latest school_admin migration is
        ('school_admin', '0003_schoolsettings'),
        ('academics', '0001_initial'),          # ClassLevel lives here
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tenants', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Circular',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('school', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='%(app_label)s_%(class)s_set',
                    to='tenants.school',
                )),
                ('title',   models.CharField(max_length=255)),
                ('content', models.TextField()),
                ('target_audience', models.CharField(
                    choices=[
                        ('all',      'All'),
                        ('students', 'Students'),
                        ('teachers', 'Teachers'),
                        ('parents',  'Parents'),
                    ],
                    db_index=True,
                    default='all',
                    max_length=20,
                )),
                ('target_class_levels', models.ManyToManyField(
                    blank=True,
                    related_name='circulars',
                    to='academics.classlevel',
                    help_text='Leave empty to target every class in the school.',
                )),
                ('attachment_key',  models.CharField(blank=True, max_length=500, null=True)),
                ('attachment_name', models.CharField(blank=True, max_length=255, null=True)),
                ('is_published', models.BooleanField(default=True)),
                ('created_by', models.ForeignKey(
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='circulars_created',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
