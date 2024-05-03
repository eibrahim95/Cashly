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
## Deliverables
### Models
There are 7 models
- users:Manager: extends normal user model.
- users:CacheCollector: extends normal user model.
- billing:Customer: So we don't repeat customer details on every bill(task), 1NF.
- billing:CustomerBill: A task assigned to specific CashCollector.
- accounting:CashCollectorPocket: A task collected by a CashCollector (The money is in his pocket).
- accounting:CentralSafe: The money paid to Managers from CashCollectors.
- accounting:CashCollectorTimeline: Store CashCollector events.

### Status at different points.
- You can log in to admin panel and see the CashCollectorTimeline list, search with a specific collector username.
- You can use `/api/v1/collector-status-report/` rest api while logged in with the desired collector.

### Restfull APIs
- Please download this [postman collection](https://api.postman.com/collections/3035580-f8619d63-0b92-4e36-878f-2ee31b07f400?access_key=PMAT-01HWZ5ZJMAAZNET471K0WE2CCQ), it has all the details on the endpoints.
- In the postman collection variables, update `MANAGER_AUTH_KEY`, `COLLECTOR_AUTH_KEY`, these are the keys used for manager, collector operations respectively.
- The 1,2,3,4 folders are manager operations, the 5,6 folders are collectors operations.

### Test cases
- I've written integration tests for the main scenario, in 2 different ways, one directly using orm, and other using apis.
  - You can run it using `DJANGO_SETTINGS_MODULE=config.settings.test pytest -s -vv -k main_scenario`
- I've also written tests for the most important edge cases.
  - You can run it using `DJANGO_SETTINGS_MODULE=config.settings.test pytest -s -vv -k edge_cases`

### Running project.
- Create a virtualenv, activate it, install `requirements/local.txt`.
- Migrate database `python manage.py migrate`.
- Create a super user `DJANGO_SUPERUSER_PASSWORD=superadmin python manage.py createsuperuser --username superadmin --email superadmin@cachly.ai --noinput`
  - This creates a superuser with username `superadmin` and password `superadmin`.
- Create a manager `echo "from cashly.users.models import Manager;manager=Manager.objects.create(username='manager1');manager.set_password('Cashly@2024');manager.save()" | python manage.py shell`
  - This creates a manager with username `manager` and password `Cashly@2024`.
- Run the server `python manage.py runserver`.
- You can now use the manager in the Rest API to create collectors and customer and bills.

---
