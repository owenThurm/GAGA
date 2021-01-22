import os
import sys
sys.path.append('/home/bitnami/htdocs/Repos/app/GAGA/GAGA')
sys.path.append('/home/bitnami/htdocs/Repos/app/GAGA')
os.environ.setdefault("PYTHON_EGG_CACHE", "/home/bitnami/htdocs/Repos/app/GAGA/egg_cache")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "GAGA.settings")
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
