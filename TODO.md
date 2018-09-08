# TODO

* Kommentieren

## API
* Challenge erstellung/URL Update testen

* Prio Low: Create mysql database with collection `utf8mb4_unicode_ci` if not exists:
https://sqlalchemy-utils.readthedocs.io/en/latest/database_helpers.html#database-exists
```python
from sqlalchemy_utils import database_exists, create_database
uri = app.config['SQLALCHEMY_DATABASE_URI']
if not database_exists(uri):
    create_database(uri, encoding="utf8mb4_unicode_ci")
```

* Prio Low: Change MySQL database collection to `utf8mb4_unicode_ci` via sqlalchemy (if possible)
  * define in database model
    http://stackoverflow.com/questions/18561190/ddg#18561417
    https://groups.google.com/d/msg/sqlalchemy/XDDPiyWJsAk/T7splX0ABwAJ


## Backend
* admin: create challenge (with url)
  * create challenge before url's

## General and Frontend (HTML, CSS, JS)
* rules.html erstellen
* config.py: Mail Subject/Message anpassen
* ID für Announcement Video des Challenge Interface einfügen - muss mit Cedric koordiniert werden.
* admin: update challenge (url's)
  * save url id in the rows...

## Rules
* DoS (Denial of Service) ist verboten!
* XSS ist verboten
* Challenges nicht verändern
  * Wenn du bemerkst das eine Challenge verändert wurde oder nicht richtig funktioniert dann lass es uns wissen.
