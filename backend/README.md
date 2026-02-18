
Run frontend:
    npm start

Run Backend (Development):
    .\venv\Scripts\Activate.ps1
    python .\manage.py runserver

Run Backend (Production with Waitress - Windows Compatible):
    .\venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    waitress-serve --host=0.0.0.0 --port=8000 carta_restaurantes.wsgi:application

Or using the production scripts:
    .\start_production.ps1   # PowerShell
    .\start_production.bat   # Command Prompt

Server will be available at: http://localhost:8000
