# Script para iniciar el servidor Django con Waitress en Windows

Write-Host "Activando entorno virtual..." -ForegroundColor Green
& ".\venv\Scripts\Activate.ps1"

Write-Host "Instalando dependencias..." -ForegroundColor Green
pip install -r requirements.txt

Write-Host "Aplicando migraciones..." -ForegroundColor Green
python manage.py migrate

Write-Host "Recolectando archivos estáticos..." -ForegroundColor Green
python manage.py collectstatic --noinput

Write-Host "Iniciando servidor con Waitress en puerto 8000..." -ForegroundColor Green
Write-Host "Accede a: http://localhost:8000" -ForegroundColor Yellow
waitress-serve --host=0.0.0.0 --port=8000 carta_restaurantes.wsgi:application