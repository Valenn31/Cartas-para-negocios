#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carta_restaurantes.settings')
django.setup()

from carta_restaurantes.models import Categoria, Subcategoria, Comida

# Datos de ejemplo
datos_ejemplo = {
    "Desayunos": {
        "orden": 1,
        "subcategorias": {
            "Cafetería": [
                {"nombre": "Café Americano", "descripcion": "Café negro intenso y aromático", "precio": 2.50},
                {"nombre": "Cortado", "descripcion": "Café con un toque de leche", "precio": 3.00},
                {"nombre": "Cappuccino", "descripcion": "Café espresso con espuma de leche", "precio": 3.50},
                {"nombre": "Latte", "descripcion": "Café suave con abundante leche", "precio": 4.00},
                {"nombre": "Café con Leche", "descripcion": "El clásico de siempre", "precio": 2.80},
                {"nombre": "Espresso", "descripcion": "Café concentrado y fuerte", "precio": 2.20},
            ],
            "Facturas": [
                {"nombre": "Croissant Simple", "descripcion": "Crujiente y mantecoso", "precio": 2.00},
                {"nombre": "Croissant de Jamón y Queso", "descripcion": "Relleno con jamón cocido y queso", "precio": 3.50},
                {"nombre": "Medialuna", "descripcion": "Dulce y esponjosa", "precio": 1.50},
                {"nombre": "Vigilante", "descripcion": "Queso y dulce de membrillo", "precio": 4.00},
                {"nombre": "Tostadas con Mermelada", "descripcion": "Pan tostado con mermelada casera", "precio": 3.00},
                {"nombre": "Churros con Dulce de Leche", "descripcion": "Recién hechos y crocantes", "precio": 3.80},
            ],
            "Licuados y Smoothies": [
                {"nombre": "Licuado de Frutilla", "descripcion": "Con leche y frutillas frescas", "precio": 4.00},
                {"nombre": "Licuado de Banana", "descripcion": "Cremoso licuado de banana", "precio": 3.50},
                {"nombre": "Licuado de Durazno", "descripcion": "Refrescante y natural", "precio": 4.20},
                {"nombre": "Smoothie de Frutos Rojos", "descripcion": "Mix de berries con yogurt", "precio": 5.00},
                {"nombre": "Smoothie Verde", "descripcion": "Espinaca, manzana y apio", "precio": 4.80},
            ]
        }
    },
    "Pizzas": {
        "orden": 2,
        "subcategorias": {
            "Clásicas": [
                {"nombre": "Margherita", "descripcion": "Tomate, mozzarella y albahaca fresca", "precio": 12.00},
                {"nombre": "Napolitana", "descripcion": "Tomate, mozzarella, jamón y aceitunas", "precio": 14.00},
                {"nombre": "Muzarella", "descripcion": "Salsa de tomate y abundante mozzarella", "precio": 11.00},
                {"nombre": "Calabresa", "descripcion": "Mozzarella, salame y morrones", "precio": 15.00},
                {"nombre": "Fugazza", "descripcion": "Cebolla, oregano y aceitunas", "precio": 10.50},
            ],
            "Especiales": [
                {"nombre": "Cuatro Quesos", "descripcion": "Mozzarella, roquefort, parmesano y provoleta", "precio": 16.00},
                {"nombre": "Hawaiana", "descripcion": "Jamón, ananá y mozzarella", "precio": 15.50},
                {"nombre": "Vegetariana", "descripcion": "Verduras grilladas y queso de cabra", "precio": 14.50},
                {"nombre": "Prosciutto", "descripcion": "Jamón crudo, rúcula y parmesano", "precio": 18.00},
                {"nombre": "Barbacoa", "descripcion": "Carne mechada, cebolla morada y salsa BBQ", "precio": 17.50},
            ]
        }
    },
    "Hamburguesas": {
        "orden": 3,
        "subcategorias": {
            "Clásicas": [
                {"nombre": "Victory Burger", "descripcion": "Carne, lechuga, tomate, cebolla y salsa especial", "precio": 8.50},
                {"nombre": "Cheeseburger", "descripcion": "Carne, queso cheddar, lechuga y tomate", "precio": 9.00},
                {"nombre": "Bacon Burger", "descripcion": "Carne, bacon crujiente y queso", "precio": 10.00},
                {"nombre": "Doble Carne", "descripcion": "Doble medallón de carne y queso", "precio": 12.00},
            ],
            "Gourmet": [
                {"nombre": "Truffle Burger", "descripcion": "Carne, hongos, queso brie y trufa", "precio": 16.00},
                {"nombre": "BBQ Ranch", "descripcion": "Carne, cebolla caramelizada y salsa BBQ", "precio": 13.50},
                {"nombre": "Crispy Chicken", "descripcion": "Pollo empanado, lechuga y mayo", "precio": 11.00},
                {"nombre": "Veggie Deluxe", "descripcion": "Hamburguesa de lentejas y quinoa", "precio": 10.50},
            ]
        }
    },
    "Pastas": {
        "orden": 4,
        "subcategorias": {
            "Tradicionales": [
                {"nombre": "Spaghetti Bolognesa", "descripcion": "Con salsa de carne tradicional", "precio": 14.00},
                {"nombre": "Penne Arrabiata", "descripcion": "Salsa de tomate picante", "precio": 12.00},
                {"nombre": "Fettuccine Alfredo", "descripcion": "Crema, manteca y parmesano", "precio": 13.50},
                {"nombre": "Ravioles de Ricota", "descripcion": "Con salsa de tomate y albahaca", "precio": 15.00},
                {"nombre": "Carbonara", "descripcion": "Panceta, huevo y parmesano", "precio": 14.50},
            ],
            "Gourmet": [
                {"nombre": "Risotto de Hongos", "descripcion": "Arroz cremoso con hongos porcini", "precio": 18.00},
                {"nombre": "Ñoquis de Papa", "descripcion": "Con salsa de queso azul", "precio": 16.00},
                {"nombre": "Lasagna de Verduras", "descripcion": "Capas de pasta con verduras grilladas", "precio": 17.00},
                {"nombre": "Cannelloni de Espinaca", "descripcion": "Rellenos con ricota y espinaca", "precio": 16.50},
                {"nombre": "Pasta Puttanesca", "descripcion": "Aceitunas, alcaparras y anchoas", "precio": 15.50},
            ]
        }
    },
    "Ensaladas": {
        "orden": 5,
        "subcategorias": {
            "Verdes": [
                {"nombre": "César", "descripcion": "Lechuga, crutones, parmesano y pollo", "precio": 9.50},
                {"nombre": "Mixta", "descripcion": "Lechuga, tomate, cebolla y zanahoria", "precio": 7.00},
                {"nombre": "Rúcula y Parmesano", "descripcion": "Con aceite de oliva y limón", "precio": 8.50},
                {"nombre": "Caprese", "descripcion": "Tomate, mozzarella y albahaca", "precio": 10.00},
            ],
            "Completas": [
                {"nombre": "Quinoa Bowl", "descripcion": "Quinoa, palta, tomates cherry y semillas", "precio": 12.00},
                {"nombre": "Mediterránea", "descripcion": "Aceitunas, queso feta y pepinos", "precio": 11.50},
                {"nombre": "Pollo Grillado", "descripcion": "Con verduras de estación", "precio": 13.00},
                {"nombre": "Salmón y Palta", "descripcion": "Salmón ahumado con rúcula", "precio": 15.00},
            ]
        }
    },
    "Bebidas": {
        "orden": 6,
        "subcategorias": {
            "Gaseosas": [
                {"nombre": "Coca Cola", "descripcion": "500ml", "precio": 2.50},
                {"nombre": "Sprite", "descripcion": "500ml", "precio": 2.50},
                {"nombre": "Fanta", "descripcion": "500ml", "precio": 2.50},
                {"nombre": "Agua con Gas", "descripcion": "500ml", "precio": 2.00},
                {"nombre": "Agua Sin Gas", "descripcion": "500ml", "precio": 1.80},
            ],
            "Jugos Naturales": [
                {"nombre": "Jugo de Naranja", "descripcion": "Exprimido natural", "precio": 3.50},
                {"nombre": "Jugo de Pomelo", "descripcion": "Fresco y natural", "precio": 3.80},
                {"nombre": "Limonada", "descripcion": "Con menta fresca", "precio": 3.00},
                {"nombre": "Agua Saborizada", "descripcion": "Sabores varios", "precio": 2.80},
            ],
            "Cervezas": [
                {"nombre": "Cerveza Rubia", "descripcion": "Pinta 500ml", "precio": 4.50},
                {"nombre": "Cerveza Negra", "descripcion": "Pinta 500ml", "precio": 5.00},
                {"nombre": "Cerveza IPA", "descripcion": "Artesanal 500ml", "precio": 6.00},
                {"nombre": "Cerveza Sin Alcohol", "descripcion": "Pinta 500ml", "precio": 4.00},
            ]
        }
    },
    "Postres": {
        "orden": 7,
        "subcategorias": {
            "Helados": [
                {"nombre": "Copa Helada", "descripcion": "3 bochas con crema y cerezas", "precio": 6.50},
                {"nombre": "Banana Split", "descripcion": "Banana, helado y salsa de chocolate", "precio": 7.00},
                {"nombre": "Sundae de Chocolate", "descripcion": "Helado con salsa caliente", "precio": 5.50},
                {"nombre": "Milkshake", "descripcion": "Batido cremoso, varios sabores", "precio": 4.80},
            ],
            "Tortas": [
                {"nombre": "Cheesecake", "descripcion": "Con frutos rojos", "precio": 8.00},
                {"nombre": "Tiramisu", "descripcion": "Clásico italiano con café", "precio": 7.50},
                {"nombre": "Brownie con Helado", "descripcion": "Tibio con helado de vainilla", "precio": 6.80},
                {"nombre": "Flan Casero", "descripcion": "Con dulce de leche y crema", "precio": 5.00},
                {"nombre": "Tarta de Manzana", "descripcion": "Con canela y helado", "precio": 6.00},
            ],
            "Frutas": [
                {"nombre": "Macedonia", "descripcion": "Frutas frescas de estación", "precio": 4.50},
                {"nombre": "Ensalada de Frutas", "descripcion": "Con yogurt y granola", "precio": 5.50},
                {"nombre": "Smoothie Bowl", "descripcion": "Base de açaí con frutas", "precio": 7.00},
            ]
        }
    },
    "Cócteles": {
        "orden": 8,
        "subcategorias": {
            "Clásicos": [
                {"nombre": "Mojito", "descripcion": "Ron, menta, lima y soda", "precio": 8.50},
                {"nombre": "Caipirinha", "descripcion": "Cachaça, lima y azúcar", "precio": 7.50},
                {"nombre": "Pisco Sour", "descripcion": "Pisco, limón y clara de huevo", "precio": 9.00},
                {"nombre": "Daiquiri", "descripcion": "Ron blanco, lima y azúcar", "precio": 8.00},
            ],
            "Signature": [
                {"nombre": "Victory Punch", "descripcion": "Mezcla especial de la casa", "precio": 12.00},
                {"nombre": "Tropical Sunset", "descripcion": "Ron, mango y maracuyá", "precio": 10.50},
                {"nombre": "Gin Garden", "descripcion": "Gin, pepino y albahaca", "precio": 11.00},
                {"nombre": "Spicy Margarita", "descripcion": "Tequila, lima y jalapeño", "precio": 9.50},
            ],
            "Sin Alcohol": [
                {"nombre": "Virgin Mojito", "descripcion": "Menta, lima y soda", "precio": 4.50},
                {"nombre": "Limonada de Jengibre", "descripcion": "Refrescante y picante", "precio": 4.00},
                {"nombre": "Agua de Coco", "descripcion": "Natural y refrescante", "precio": 3.50},
                {"nombre": "Té Helado", "descripcion": "Con frutas y hierbas", "precio": 3.80},
            ]
        }
    }
}

def cargar_datos():
    print("🍽️ Cargando datos de ejemplo...")
    
    # Limpiar datos existentes
    print("🧹 Limpiando datos existentes...")
    Comida.objects.all().delete()
    Subcategoria.objects.all().delete()
    Categoria.objects.all().delete()
    
    for categoria_nombre, categoria_data in datos_ejemplo.items():
        print(f"📂 Creando categoría: {categoria_nombre}")
        
        # Crear categoría
        categoria = Categoria.objects.create(
            nombre=categoria_nombre,
            orden=categoria_data["orden"]
        )
        
        orden_subcategoria = 1
        for subcategoria_nombre, comidas in categoria_data["subcategorias"].items():
            print(f"  📁 Creando subcategoría: {subcategoria_nombre}")
            
            # Crear subcategoría
            subcategoria = Subcategoria.objects.create(
                categoria=categoria,
                nombre=subcategoria_nombre,
                orden=orden_subcategoria
            )
            orden_subcategoria += 1
            
            # Crear comidas
            for comida_data in comidas:
                print(f"    🍽️ Creando comida: {comida_data['nombre']}")
                Comida.objects.create(
                    categoria=categoria,
                    subcategoria=subcategoria,
                    nombre=comida_data["nombre"],
                    descripcion=comida_data["descripcion"],
                    precio=comida_data["precio"],
                    disponible=True
                )
    
    print("✅ ¡Datos cargados exitosamente!")
    print(f"📊 Resumen:")
    print(f"   - Categorías: {Categoria.objects.count()}")
    print(f"   - Subcategorías: {Subcategoria.objects.count()}")
    print(f"   - Comidas: {Comida.objects.count()}")

if __name__ == "__main__":
    cargar_datos()
