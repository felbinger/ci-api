# Challenge Interface

## API Schema
| Method | URL | Headers | Data | Description |
|:---:|:---:|:---:|:---:|:---:|
| GET | /api/auth | Access-Token | / | Infos über eigenen Account |
| POST | /api/auth |  | username, password | Login |
| DELETE | /api/auth | Access-Token | / | Logout |
||||||
| GET | /api/roles | Access-Token | / | Get all roles |
| GET | /api/roles/{name:string} | Access-Token | / | Get a role |
| POST | /api/roles | Access-Token | name, description | Admin: create role |
| PUT | /api/roles/{name:string} | Access-Token | description | Admin: modify role (description) |
| DELETE | /api/roles/{name:string} | Access-Token | / | Admin: delete role |
||||||
| GET | /api/users | Access-Token | / | Admin: Get all accounts |
| GET | /api/users/{uuid:string} | Access-Token | / | Admin: Get a account |
| POST | /api/users |  | username, email, password | Register a new account |
| POST | /api/users | Access-Token | username, email, password, role | Admin: Create a new account |
| PUT | /api/users/{uuid:string} | Access-Token | username (and/or) email (and/or) password | Admin: update user (by UUID) |
| PUT | /api/users/me | Access-Token | username (and/or) email (and/or) password | update your account |
| DELETE | /api/users/{uuid:string} | Access-Token | / | Admin: delete user (by UUID) |
| DELETE | /api/users/me | Access-Token | / | delete your account |
||||||
| GET | /api/categories | Access-Token | / | Get all categories |
| GET | /api/categories/{name:string} | Access-Token | / | Get a category |
| POST | /api/categories | Access-Token | name, description | Admin: create category |
| PUT | /api/categories/{name:string} | Access-Token | description | Admin: modify category (description) |
| DELETE | /api/categories/{name:string} | Access-Token | / | Admin: delete category |
||||||
| GET | /api/urls/ | Access-Token | / | Get all urls |
| GET | /api/urls/{id:int} | Access-Token | / | Get a url |
| POST | /api/urls | Access-Token | url, description, challenge | Admin: create url |
| PUT | /api/urls/{id:int} | Access-Token | url, description, challenge | Admin: modify url |
| DELETE | /api/urls/{id:int} | Access-Token | / | Admin: delete url |
||||||
| GET | /api/challenges | Access-Token | / | Get all challenges |
| GET | /api/challenges/{id:int} | Access-Token | / | Get challenge |
| POST | /api/challenges | Access-Token | name, description, category, flag, points | Admin: create challenge |
| PUT | /api/challenges/{id:int} | Access-Token | ytChallengeId (and/or) ytSolutionId (and/or) description (and/or) points | Admin: update challenge (YouTube video id's and/or description) |
||||||
| POST | /api/solve | Access-Token | flag | Solve Special Challenge |
| PUT | /api/solve/{id:int} | Access-Token | flag | Solve Challenge | |

### GET Result Schemas
* Role: `name`, `description`
* Account (user): `publicId`, `username`, `email`, `created`, `lastLogin`,
  `role` (`name`, `description`), `solved` (`challenge` (`id`, `name`, `category`), `timestamp`)
* Category: `name`, `description`
* URL: `id`, `url`, `description`, `challenge` (`id`, `name`, `category`(`name`, `description`))
* Challenge: `id`, `name`, `description`, `points`, `category`(`name`, `description`), `ytChallengeId`, `ytSolutionId`, 
  `urls` [(`id`, `url`, `description`), ...], `solveCount`

## Database Schema
| Table | Attribute | Datatype (Length) (+ Description) | Settings |
|:---------:|:-------------:|:---------------------------------:|:---------------------------:|
| users | id | Integer(20) | primary key, auto increment |
|  | publicId | Varchar(36) (for uuid4) | unique |
|  | username | Varchar(80) | unique |
|  | email | Varchar(100) | unique |
|  | password | Blob(512) (sha512 Hash) |  |
|  | lastLogin | TimeStamp |  |
|  | created | TimeStamp |  |
|  | role | Integer(20) | foreign key -} role.id |
| roles | id | Integer(20) | primary key, auto increment |
|  | name | Varchar(80) |  |
|  | description | Varchar(100) |  |
| tokens | id | Integer(20) | primary key, auto increment |
|  | user | Integer(20) | foreign key -} user.id |
|  | token | Varchar(128) | unique |
|  | created | TimeStamp |  |
|  | expires | TimeStamp |  |
|  | broken | Integer(1) (boolean) |  |
| challenge | id | Integer(20) | primary key, auto increment |  
|  | flag | Varchar(80) | unique |  
|  | points | Integer(11) |  |  
|  | name | Varchar(80) | unique |  
|  | description | Varchar(512) |  |  
|  | ytChallengeId | Varchar(10) |  |  
|  | ytSolutionId | Varchar(10) |  |  
|  | category | Varchar(80) | |  
| ratings | id | Integer(20) | |
|  | user | Integer(20) |  |
| url | id | Integer(20) | primary key, auto increment |  
|  | description | Varchar(100) |  |  
|  | url | Varchar(100) | unique |
|  | challenge | Integer(20) | foreign key -} challenge.id |  
| solved | id | Integer(20) | primary key, auto increment |  
|  | challenge | Integer(20) | foreign key -} challenge.id |
|  | user | Integer(20) | foreign key -} user.id |  
|  | timestamp | TimeStamp |  |  |

## Installation
* Install [Docker](https://docs.docker.com/install/) and [docker-compose](https://docs.docker.com/compose/install/)
* Build Docker Image

```
git clone ssh://git@git.the-morpheus.de:322/challengeInterface/backend.git
docker build -t backend .
```

* Define your container in the file `docker-compose.yml`:

```yml
version: '3'
services:
  db:
    image: mysql:5.7
    container_name: root_db_1
    restart: always
    ports:
      - "9999:3306"
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: hc
    volumes:
      - "/srv/mysql:/var/lib/mysql"
  backend:
    image: backend
    container_name: root_backend_1
    restart: always
    ports:
      - "8080:80"
    environment:
      MYSQL_PASSWORD: root
```

* Add database hc (in this example automatically)
* Change database collection from `latin1_swedish_ci` to `utf8mb4_unicode_ci`
* Execute following sql:
```sql
INSERT INTO `category` (`id`, `name`, `description`) VALUES
(1, 'HC', 'Hacking Challenges'),
(2, 'CC', 'Coding Challenges'),
(3, 'Special', 'Special Challenges');

INSERT INTO `role` (`id`, `name`, `description`) VALUES
(1, 'admin', 'Admin'),
(2, 'user', 'User');
```

* Use docker-compose:
```bash
# Start all containers
docker-compose up -d
# Stop all containers
docker-compose stop
# Stop and remove all containers
docker-compose down  
# Start a specific container
docker-compose up -d <container>
# Stop a specific container
docker-compose stop <container>
# Stop and remove a specific container
docker-compose rm -fs <container>  
# Show logs
docker-compose logs [container]  
# Show status
docker-compose ps [container]
```
