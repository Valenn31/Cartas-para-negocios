# Generated by Django 5.2.4 on 2025-07-17 15:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carta_restaurantes', '0004_alter_categoria_orden'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subcategoria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('orden', models.PositiveIntegerField(db_index=True, default=0)),
                ('categoria', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subcategorias', to='carta_restaurantes.categoria')),
            ],
            options={
                'verbose_name': 'Subcategoría',
                'verbose_name_plural': 'Subcategorías',
                'ordering': ['orden', 'nombre'],
            },
        ),
        migrations.AddField(
            model_name='comida',
            name='subcategoria',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='carta_restaurantes.subcategoria'),
        ),
    ]
