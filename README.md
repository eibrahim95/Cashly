# Cashly

Collect due cash

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

License: MIT

## Design Decisions
![cashly.jpg](docs%2Fcashly.jpg)  
<small>A general view of the system , it is not meant to be a full UML, or even a valid one.</small>

### 1. Where do tasks come from?
- I decided to make the tasks be created from the admin panel, also i'll provide a crud only to managers, so they can use to create tasks
- I also decided to separate the Customer, so the tasks crud would need a customers' crud, which i'll also create.

### 2. Multiple cash collectors and multiple managers. 
- It makes sense that there will be multiple cash collectors and multiple managers, so the following decisions where made.
- Managers assign tasks to specific cash collectors when creating tasks.
  - So, we will need a crud for cash collectors.
- We will not care which manager collects the money from the cash collector, we can assume it's the manager who created the task.
  - For that to make more sense, task creator cannot be changed.

### 3. Different user table ?
- For simplicity, we will use django's auth system, and we will just add a field called System Role, which can be manager or cash collector.
  - Update #1: On a second thought let's create a separate model for manager and collector, and make it inherit from User, this will make the relationships between the manager and task, and between the collector and its pocket make more sense.
- What about the superuser thing ? 
  - We will ignore the superuser status in all the api endpoints, for example if a cash collector is also a superuser, he will still not be able to call endpoints that need a manager.

### 4. Keeping history
- We will try to keep as much history as possible, for example when moving money for a cash collector's pocket to a safe, we will not delete the value from the pocket, but instead will mark it as collected.
- This might require more storage for the DB, and might make us optimize queries as possible, but in cash related systems, transaction data are important (I think).

### 5. Freezing cash collectors.
- At a first glance I thought we would need a celery beat to execute every specific period, and look for cash collectors that has the freezing criteria and freeze them.
- But it seemed like over engineering, and also there is the possibility of requests coming between the beats.
- So instead, with every write to a cash collector's pocket, we will check if it passes the specified amount and then store the time in the future when this cash collector would be frozen.
- This might slow the writes a little bit, but the gains are better.

---
## Settings

Moved to [settings](http://cookiecutter-django.readthedocs.io/en/latest/settings.html).

---
## Basic Commands

### Setting Up Your Users

- To create a **normal user account**, just go to Sign Up and fill out the form. Once you submit it, you'll see a "Verify Your E-mail Address" page. Go to your console to see a simulated email verification message. Copy the link into your browser. Now the user's email should be verified and ready to go.

- To create a **superuser account**, use this command:

      $ python manage.py createsuperuser

For convenience, you can keep your normal user logged in on Chrome and your superuser logged in on Firefox (or similar), so that you can see how the site behaves for both kinds of users.

### Type checks

Running type checks with mypy:

    $ mypy cashly

### Test coverage

To run the tests, check your test coverage, and generate an HTML coverage report:

    $ coverage run -m pytest
    $ coverage html
    $ open htmlcov/index.html

#### Running tests with pytest

    $ pytest

### Live reloading and Sass CSS compilation

Moved to [Live reloading and SASS compilation](https://cookiecutter-django.readthedocs.io/en/latest/developing-locally.html#sass-compilation-live-reloading).

### Celery

This app comes with Celery.

To run a celery worker:

```bash
cd cashly
celery -A config.celery_app worker -l info
```

Please note: For Celery's import magic to work, it is important _where_ the celery commands are run. If you are in the same folder with _manage.py_, you should be right.

To run [periodic tasks](https://docs.celeryq.dev/en/stable/userguide/periodic-tasks.html), you'll need to start the celery beat scheduler service. You can start it as a standalone process:

```bash
cd cashly
celery -A config.celery_app beat
```

or you can embed the beat service inside a worker with the `-B` option (not recommended for production use):

```bash
cd cashly
celery -A config.celery_app worker -B -l info
```

---
## Deployment

The following details how to deploy this application.

### Docker

See detailed [cookiecutter-django Docker documentation](http://cookiecutter-django.readthedocs.io/en/latest/deployment-with-docker.html).
