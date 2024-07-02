import os
import subprocess
import sys
import venv
import secrets
import time

def install_virtualenv():
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'show', 'virtualenv'])
    except subprocess.CalledProcessError:
        print("virtualenv is not installed. Installing now...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'virtualenv'])

def create_virtualenv(project_path):
    venv_path = os.path.join(project_path, 'venv')
    if not os.path.exists(venv_path):
        venv.create(venv_path, with_pip=True)
        print(f'Virtual environment created at {venv_path}.')
    else:
        print(f'Virtual environment already exists at {venv_path}.')
    return venv_path

def install_dependencies(venv_path, requirements_file):
    pip_path = os.path.join(venv_path, 'bin', 'pip')
    subprocess.call([pip_path, 'install', '-r', requirements_file])

def create_env_file(project_path, db_choice, db_config=None):
    secret_key = secrets.token_urlsafe(50)
    env_path = os.path.join(project_path, '.env')
    with open(env_path, 'w') as file:
        file.write(f'SECRET_KEY={secret_key}\n')
        file.write(f'DEBUG=True\n')
        if db_choice in ['2', '3'] and db_config:
            for key, value in db_config.items():
                file.write(f'{key}={value}\n')
    return env_path

def validate_name(name, name_type):
    if ' ' in name:
        print(f"Error: {name_type} name cannot contain spaces.")
        sys.exit(1)

def update_settings_installed_apps(project_path, app_name):
    settings_path = os.path.join(project_path, 'core', 'settings.py')
    with open(settings_path, 'r') as file:
        settings = file.read()

    local_apps_line = "LOCAL_APPS = [\n"
    new_app = f"    'apps.{app_name}',\n"
    if new_app not in settings:
        settings = settings.replace(local_apps_line, f"{local_apps_line}{new_app}")

    with open(settings_path, 'w') as file:
        file.write(settings)

def update_app_config(app_path, app_name):
    app_config_path = os.path.join(app_path, 'apps.py')
    with open(app_config_path, 'r') as file:
        app_config = file.read()

    app_config = app_config.replace(f"name = '{app_name}'", f"name = 'apps.{app_name}'")

    with open(app_config_path, 'w') as file:
        file.write(app_config)

def update_urls(project_path, app_name):
    urls_path = os.path.join(project_path, 'core', 'urls.py')
    with open(urls_path, 'r') as file:
        urls = file.read()

    if "from django.urls import path" in urls:
        urls = urls.replace("from django.urls import path", "from django.urls import path, include, re_path")

    if "from django.conf import settings" not in urls:
        urls = f"from django.conf import settings\nfrom django.conf.urls.static import static\n{urls}"

    new_imports = f"# path('{app_name}/', include('apps.{app_name}.urls')),"
    if new_imports not in urls:
        urls = urls.replace(
            "urlpatterns = [\n    path('admin/', admin.site.urls),",
            f"""urlpatterns = [\n    path('admin/', admin.site.urls),\n    {new_imports}"""
        )

    if "urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)" not in urls:
        urls += """
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
"""

    with open(urls_path, 'w') as file:
        file.write(urls)

def create_django_app(project_path, app_name):
    apps_path = os.path.join(project_path, 'apps')
    if not os.path.exists(apps_path):
        os.makedirs(apps_path, exist_ok=True)
        init_file = os.path.join(apps_path, '__init__.py')
        open(init_file, 'a').close()

    app_path = os.path.join(apps_path, app_name)
    if not os.path.exists(app_path):
        os.makedirs(app_path, exist_ok=True)
    subprocess.call(['django-admin', 'startapp', app_name, app_path])
    update_app_config(app_path, app_name)
    update_settings_installed_apps(project_path, app_name)
    update_urls(project_path, app_name)
    print(f'App {app_name} created successfully in apps directory.')

def create_django_project(project_name, db_choice, db_config=None):
    project_path = os.path.join(os.getcwd(), project_name)
    tasks = [
        'Creating Django project',
        'Creating virtual environment',
        'Setting up database configuration',
        'Creating initial directories',
        'Writing requirements file',
        'Creating .env file',
        'Installing dependencies'
    ]

    for task in tqdm(tasks, desc='Setting up project', unit='task'):
        if task == 'Creating Django project':
            os.makedirs(project_path, exist_ok=True)
            subprocess.call(['django-admin', 'startproject', 'core', project_path])

        elif task == 'Creating virtual environment':
            venv_path = create_virtualenv(project_path)

        elif task == 'Setting up database configuration':
            settings_path = os.path.join(project_path, 'core', 'settings.py')
            with open(settings_path, 'r') as file:
                settings = file.read()

            settings = settings.replace(
                "SECRET_KEY = 'django-insecure-'",
                "SECRET_KEY = config('SECRET_KEY')"
            )

            if db_choice in ['2', '3']:
                # Remove existing SQLite configuration
                settings = settings.replace("""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
""", "")

                db_config_string = """
DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE'),
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
    }
}
"""

                settings = settings.replace(
                    "# Database\n# https://docs.djangoproject.com/en/4.2/ref/settings/#databases\n\n",
                    db_config_string
                )

            settings = settings.replace(
                "from pathlib import Path",
                "from pathlib import Path\nfrom decouple import config\nimport os"
            )

            settings = settings.replace(
                "DEBUG = True",
                "DEBUG = config('DEBUG', default=True, cast=bool)"
            )

            # Remove old INSTALLED_APPS and add new format
            start = settings.find("INSTALLED_APPS = [")
            end = settings.find("]", start) + 1
            settings = settings[:start] + settings[end:]

            settings += """
DEFAULT_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
]

THIRD_PARTY_APPS = [

]

LOCAL_APPS = [

]

INSTALLED_APPS = DEFAULT_APPS + THIRD_PARTY_APPS + LOCAL_APPS
"""

            # Modify TEMPLATES configuration
            settings = settings.replace(
                "'DIRS': [],",
                "'DIRS': [BASE_DIR / 'templates'],"
            )

            # Add STATIC and MEDIA settings below existing STATIC_URL
            if "STATIC_URL = 'static/'" in settings:
                settings = settings.replace(
                    "STATIC_URL = 'static/'",
                    """STATIC_URL = 'static/'
#STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
MEDIA_URL = '/media/'
"""
                )

            with open(settings_path, 'w') as file:
                file.write(settings)

        elif task == 'Creating initial directories':
            os.makedirs(os.path.join(project_path, 'static'), exist_ok=True)
            os.makedirs(os.path.join(project_path, 'templates'), exist_ok=True)
            apps_path = os.path.join(project_path, 'apps')
            os.makedirs(apps_path, exist_ok=True)
            init_file = os.path.join(apps_path, '__init__.py')
            open(init_file, 'a').close()

        elif task == 'Writing requirements file':
            requirements_path = os.path.join(project_path, 'requirements.txt')
            with open(requirements_path, 'w') as file:
                file.write('Django\n')
                file.write('python-decouple\n')
                if db_choice == '2':
                    file.write('psycopg2-binary\n')
                elif db_choice == '3':
                    file.write('mysqlclient\n')

        elif task == 'Creating .env file':
            create_env_file(project_path, db_choice, db_config)

        elif task == 'Installing dependencies':
            install_dependencies(venv_path, requirements_path)

    print(f'\nDjango project {project_name} created successfully with {db_choice} database.')
    print(f'Virtual environment created at {os.path.join(project_path, "venv")}.')
    print(f'To activate the virtual environment, run: source {os.path.join(project_path, "venv", "bin", "activate")}')

def check_db_connection(db_choice, db_config):
    connection = None
    try:
        if db_choice == '2':  # PostgreSQL
            connection = psycopg2.connect(
                dbname=db_config['DB_NAME'],
                user=db_config['DB_USER'],
                password=db_config['DB_PASSWORD'],
                host=db_config['DB_HOST'],
                port=db_config['DB_PORT']
            )
        elif db_choice == '3':  # MySQL
            connection = MySQLdb.connect(
                db=db_config['DB_NAME'],
                user=db_config['DB_USER'],
                passwd=db_config['DB_PASSWORD'],
                host=db_config['DB_HOST'],
                port=int(db_config['DB_PORT'])
            )
        if connection:
            print("\nDatabase connection successful.")
            return True
    except Exception as e:
        print(f"\nDatabase connection failed: {e}")
        return False
    finally:
        if connection:
            connection.close()

def check_mysql_dependencies():
    try:
        subprocess.check_call(['mysql_config', '--version'])
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("MySQL development headers not found. Please install the necessary packages.")
        if sys.platform.startswith('linux'):
            print("For Debian/Ubuntu, run: sudo apt-get install python3-dev default-libmysqlclient-dev build-essential")
        elif sys.platform.startswith('darwin'):
            print("For macOS, run: brew install mysql-client")
            print("Then add mysql-client to your PATH: export PATH=$PATH:/usr/local/opt/mysql-client/bin")
        sys.exit(1)

def main():
    install_virtualenv()

    project_name = input("Enter the project name: ")
    validate_name(project_name, "Project")
    
    print("Choose the database:\n1. SQLite\n2. PostgreSQL\n3. MySQL")
    db_choice = input("Enter the number of your choice: ")

    if db_choice not in ['1', '2', '3']:
        print("Invalid database choice. Please choose '1', '2', or '3'.")
        sys.exit(1)

    db_config = None
    if db_choice == '2':
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'psycopg2-binary'])
        db_config = {
            'DB_ENGINE': 'django.db.backends.postgresql_psycopg2',
            'DB_NAME': input("Enter the database name: "),
            'DB_USER': input("Enter the database user: "),
            'DB_PASSWORD': input("Enter the database password: "),
            'DB_HOST': input("Enter the database host: "),
            'DB_PORT': input("Enter the database port (default 5432): ") or '5432'
        }
    elif db_choice == '3':
        check_mysql_dependencies()
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'mysqlclient'])
        db_config = {
            'DB_ENGINE': 'django.db.backends.mysql',
            'DB_NAME': input("Enter the database name (default my_database): ") or 'my_database',
            'DB_USER': input("Enter the database user: "),
            'DB_PASSWORD': input("Enter the database password: "),
            'DB_HOST': input("Enter the database host: "),
            'DB_PORT': input("Enter the database port (default 3306): ") or '3306'
        }

    # Validate database connection for PostgreSQL and MySQL only
    if db_choice in ['2', '3']:
        print("Checking database connection...")
        spinner = ["|", "/", "-", "\\"]
        for _ in range(10):  # Simulate a connection delay
            for frame in spinner:
                sys.stdout.write(f"\r{frame}")
                sys.stdout.flush()
                time.sleep(0.1)

        check_db_connection(db_choice, db_config)

    create_django_project(project_name, db_choice, db_config)

    while True:
        create_app = input("Do you want to create a new app? (y/n): ")
        if create_app.lower() == 'y':
            app_name = input("Enter the app name: ")
            validate_name(app_name, "App")
            create_django_app(os.path.join(os.getcwd(), project_name), app_name)
        else:
            break

if __name__ == '__main__':
    try:
        from tqdm import tqdm
    except ImportError:
        print("tqdm is not installed. Installing now...")
        subprocess.call([sys.executable, '-m', 'pip', 'install', 'tqdm'])
        from tqdm import tqdm

    main()
