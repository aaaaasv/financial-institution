# Financial Institution

## General info

A backend API for bank employees.

## Built with

* [Python 3.8](https://www.python.org/)
* [Django 3.2.4](https://www.djangoproject.com/)
* [PostgreSQL 12](https://www.postgresql.org/)
* [Docker 20.10](https://www.docker.com/)
* [docker-compose 1.29](https://docs.docker.com/compose/)

## Setup

Clone the repository:

```sh
$ git clone https://github.com/aaaaasv/financial-institution.git
$ cd financial-institution
```
### Run with Docker

1. Run containers

For development:
```sh
$ docker-compose up --build
```

For production (PostgreSQL + static files management with nginx):
```sh
$ docker-compose -f docker-compose.prod.yaml up --build
```

2. Migrate

```sh
$ docker-compose -f docker-compose.prod.yaml exec web python manage.py migrate
```

3. Collect static files (for production) 
```sh
$ docker-compose -f docker-compose.prod.yaml exec web python manage.py collectstatic
```

<details><summary>Setup without Docker</summary>
<p>

1. Create a virtual environment:

```sh
$ python -m venv venv
$ source venv/bin/activate
```

2. Install the dependencies:

```sh
(venv)$ pip install -r requirements.txt
```

3. Once `pip` has finished downloading the dependencies, apply migrations and run the server:
```sh
(venv)$ python manage.py migrate
(venv)$ python manage.py runserver
```
And navigate to `http://127.0.0.1:8000`.

Note: Use the --insecure option for force static files serving.  [This is only intended for development](https://docs.djangoproject.com/en/3.2/ref/contrib/staticfiles/#cmdoption-runserver-insecure):
```sh
(venv)$ python manage.py runserver --insecure
```
</p>
</details>


### Configuration

You can change default configuration in `.env.dev` and `.env.prod` files.

## Usage

On the main page, you can find Swagger documentation about endpoints available to you. The system is designed to be used only by employees, so until you create superuser account and sign in with it, you will not see any endpoints.

#### User hierarchy

* Superuser - can create staff users
* Staff (bank employees) - can create and view customers, bank accounts, make transactions, and view transaction history
* Customers - can have bank accounts, created by staff users

To create superuser with Docker - run:

```sh
$ docker-compose -f docker-compose.prod.yaml exec web python manage.py createsuperuser
```

To create staff user:

1. Authenticate with superuser account
2. Send request for user creation with `is_staff = true` in the body


### Authentication

In addition to basic (username-password) authentication, the application supports JSON Web Tokens:
* `api/token/` - to obtain a new token (with username and password in the body)
* `api/token/refresh/` - to refresh old token

### Error tracking

Application supports error tracking with Sentry. To activate it add `SENTRY_DSN` variable and your [client key (DSN)](https://docs.sentry.io/product/sentry-basics/dsn-explainer/)  to environmental variables.

### Tests

```
$ docker-compose -f docker-compose.prod.yaml exec web python manage.py test
```