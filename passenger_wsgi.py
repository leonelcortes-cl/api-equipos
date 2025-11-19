import sys, os

# Ruta del proyecto
project_path = '/home/cso60906/maquinaria'
if project_path not in sys.path:
    sys.path.insert(0, project_path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Maquinaria.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
