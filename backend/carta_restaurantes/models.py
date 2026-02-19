from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

class Restaurante(models.Model):
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    slug = models.SlugField(max_length=50, unique=True, verbose_name='Slug')
    descripcion = models.TextField(blank=True, verbose_name='Descripción')
    propietario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Propietario')
    activo = models.BooleanField(default=True, verbose_name='Activo')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Restaurante'
        verbose_name_plural = 'Restaurantes'
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.nombre

class Categoria(models.Model):
    restaurante = models.ForeignKey(Restaurante, on_delete=models.CASCADE, related_name='categorias', verbose_name='Restaurante')
    nombre = models.CharField(max_length=100)
    imagen = models.ImageField(upload_to='categorias/', blank=True, null=True)
    orden = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        ordering = ['orden', 'nombre']

    def __str__(self):
        return f"{self.restaurante.nombre} - {self.nombre}"


class Subcategoria(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='subcategorias')
    nombre = models.CharField(max_length=100)
    orden = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        ordering = ['orden', 'nombre']
        verbose_name = 'Subcategoría'
        verbose_name_plural = 'Subcategorías'

    def __str__(self):
        return f"{self.categoria.nombre} - {self.nombre}"


class Comida(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    subcategoria = models.ForeignKey(Subcategoria, on_delete=models.CASCADE, blank=True, null=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    disponible = models.BooleanField(default=True)
    orden = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.nombre
