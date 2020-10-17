from .base import *

SECRET_KEY = 'l&#yqb9!cgbaznt&xp#l&#yqb9!cgbaznt&xp#+-+-l&#yqb9!cgbaznt&xp#+-3-$v!cl2v=!f6fcdgpo=*)^5hehu('

DEBUG = True

ALLOWED_HOSTS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}