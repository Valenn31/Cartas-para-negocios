"""
Configuración alternativa para servidores WSGI
Nota: Este archivo ya no se usa con Waitress en Windows.
Para Waitress, usa los parámetros de línea de comandos en los scripts.

Si quieres usar Gunicorn en Linux/Mac, mantén esta configuración:
"""

# Dirección y puerto donde escuchar
bind = "0.0.0.0:8000"

# Número de procesos trabajadores
workers = 3

# Tipo de worker (sync es bueno para la mayoría de aplicaciones Django)
worker_class = "sync"

# Tiempo máximo para que un worker procese una petición (en segundos)
timeout = 30

# Tiempo máximo para que un worker arranque (en segundos)
worker_timeout = 30

# Número máximo de peticiones que un worker puede procesar antes de reiniciarse
max_requests = 1000

# Variación aleatoria para max_requests (previene que todos los workers se reinicien al mismo tiempo)
max_requests_jitter = 50

# Límite de memoria por worker (opcional)
# max_worker_memory = 128 * 1024 * 1024  # 128MB

# Configuración de logging
loglevel = "info"
accesslog = "-"  # Log de acceso a stdout
errorlog = "-"   # Log de errores a stderr

# Formato del log de acceso
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Configuraciones adicionales
preload_app = True  # Carga la aplicación antes de hacer fork de los workers
keepalive = 2       # Segundos para mantener conexiones keep-alive

# Para desarrollo (descomenta si necesitas recarga automática)
# reload = True