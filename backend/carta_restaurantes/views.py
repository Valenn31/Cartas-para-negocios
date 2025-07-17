from rest_framework import generics
from .models import Categoria, Subcategoria, Comida
from .serializers import CategoriaSerializer, SubcategoriaSerializer, ComidaSerializer

class CategoriaList(generics.ListAPIView):
    queryset = Categoria.objects.all().order_by('orden')
    serializer_class = CategoriaSerializer

class SubcategoriaList(generics.ListAPIView):
    serializer_class = SubcategoriaSerializer
    
    def get_queryset(self):
        categoria_id = self.kwargs.get('categoria_id')
        return Subcategoria.objects.filter(categoria_id=categoria_id).order_by('orden')

class ComidaList(generics.ListAPIView):
    queryset = Comida.objects.all()
    serializer_class = ComidaSerializer

class ComidaPorSubcategoria(generics.ListAPIView):
    serializer_class = ComidaSerializer
    
    def get_queryset(self):
        subcategoria_id = self.kwargs.get('subcategoria_id')
        return Comida.objects.filter(subcategoria_id=subcategoria_id, disponible=True)
