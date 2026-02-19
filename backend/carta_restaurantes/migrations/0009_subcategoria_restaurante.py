# Generated manually to add restaurante field to subcategoria

from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('carta_restaurantes', '0008_categoria_restaurante'),
    ]

    operations = [
        migrations.AddField(
            model_name='subcategoria',
            name='restaurante',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='subcategorias', to='carta_restaurantes.restaurante', verbose_name='Restaurante'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='subcategoria',
            name='restaurante',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subcategorias', to='carta_restaurantes.restaurante', verbose_name='Restaurante'),
        ),
    ]