# Generated manually to add restaurante field to categoria

from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('carta_restaurantes', '0007_restaurante'),
    ]

    operations = [
        migrations.AddField(
            model_name='categoria',
            name='restaurante',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='categorias', to='carta_restaurantes.restaurante', verbose_name='Restaurante'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='categoria',
            name='restaurante',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='categorias', to='carta_restaurantes.restaurante', verbose_name='Restaurante'),
        ),
    ]