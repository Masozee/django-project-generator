## Overview
The Django Project Generator is a Python script designed to streamline the process of setting up new Django projects. It automates the creation of a Django project with a virtual environment, database configuration, and initial app setup. The script supports PostgreSQL, MySQL, and SQLite databases, allowing developers to choose their preferred database during setup.

## Features
Automated Django Project Setup: Creates a new Django project with a virtual environment.
Database Configuration: Supports PostgreSQL, MySQL, and SQLite with easy configuration prompts.
Environment Variables: Generates a .env file to securely store sensitive information like the secret key and database credentials.
App Initialization: Allows the creation of new Django apps within the project structure, including updates to INSTALLED_APPS and URL configurations.
Dependency Installation: Installs necessary dependencies using a requirements.txt file.
Template and Static Files Configuration: Sets up directories for templates and static files.

## How to Use
Clone the Repository:

```
git clone https://github.com/Masozee/django-project-generator.git
cd django-project-generator
Run the Script:
```

```
python generate.py
```
## Follow the Prompts:

### Enter the project name.
Choose the database (1 for SQLite, 2 for PostgreSQL, 3 for MySQL).
If PostgreSQL or MySQL is selected, enter the database configuration details (name, user, password, host, and port).

### Create Additional Apps:

After setting up the project, the script will prompt you to create new apps. Follow the prompts to add as many apps as needed.
Example

```
Enter the project name: my_project
Choose the database:
1. SQLite
2. PostgreSQL
3. MySQL
Enter the number of your choice: 2
Enter the database name: my_db
Enter the database user: my_user
Enter the database password: my_password
Enter the database host: localhost
Enter the database port (default 5432): 5432
Checking database connection...
Database connection successful.

Do you want to create a new app? (y/n): y
Enter the app name: my_app
App my_app created successfully in apps directory.
```
## Requirements
Python 3.6+
Django 4.2+
python-decouple
Database clients: psycopg2 for PostgreSQL, mysqlclient for MySQL
Contributing
Contributions are welcome! Please open an issue or submit a pull request with your improvements.

## License
This project is licensed under the MIT License.