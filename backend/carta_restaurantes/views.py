from rest_framework import generics
from .models import Categoria, Comida
from .serializers import CategoriaSerializer, ComidaSerializer

class CategoriaList(generics.ListAPIView):
    queryset = Categoria.objects.all().order_by('orden')
    serializer_class = CategoriaSerializer

class ComidaList(generics.ListAPIView):
    queryset = Comida.objects.all()
    serializer_class = ComidaSerializer
