from rest_framework import serializers
from .models import Categoria, Subcategoria, Comida

class SubcategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategoria
        fields = ['id', 'nombre', 'orden']

class CategoriaSerializer(serializers.ModelSerializer):
    subcategorias = SubcategoriaSerializer(many=True, read_only=True)
    
    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'imagen', 'orden', 'subcategorias']


class ComidaSerializer(serializers.ModelSerializer):
    subcategoria_nombre = serializers.CharField(source='subcategoria.nombre', read_only=True)
    
    class Meta:
        model = Comida
        fields = '__all__'
