# TODO
## API
* config.py: Check bugged TestingConfig
* Challenge Update: How to update the URL's?
  * Create tests after implementing
* How to insert rows into the database if the does not exist? (roles(user,admin) + categories(HC,CC,Special))

* Create mysql database with collection `utf8mb4_unicode_ci` if not exists:
https://sqlalchemy-utils.readthedocs.io/en/latest/database_helpers.html#database-exists
```python
from sqlalchemy_utils import database_exists, create_database
uri = app.config['SQLALCHEMY_DATABASE_URI']
if not database_exists(uri):
    create_database(uri, encoding="utf8mb4_unicode_ci")
```

* Change MySQL database collection to `utf8mb4_unicode_ci` via sqlalchemy (if possible)

* Leerzeichen im Schemas trimmen


## Frontend (HTML, CSS, JS)
* Rules hinzufügen
* Mail Subject/Message in config.py anpassen
* ID für Announcement Video des Challenge Interface einfügen

## Rules
* DoS (Denial of Service) ist verboten!
* XSS ist verboten
* Challenges nicht kaputtmachen
  * Wenn du bemerkst das eine Challenge verändert wurde oder nicht richtig funktioniert dann lass es uns wissen.
