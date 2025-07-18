from rest_framework import serializers
from .models import Categoria, Subcategoria, Comida

class SubcategoriaSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    
    class Meta:
        model = Subcategoria
        fields = ['id', 'nombre', 'orden', 'categoria', 'categoria_nombre']

class CategoriaSerializer(serializers.ModelSerializer):
    subcategorias = SubcategoriaSerializer(many=True, read_only=True)
    
    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'imagen', 'orden', 'subcategorias']


class ComidaSerializer(serializers.ModelSerializer):
    subcategoria_nombre = serializers.CharField(source='subcategoria.nombre', read_only=True)
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    
    class Meta:
        model = Comida
        fields = '__all__'
