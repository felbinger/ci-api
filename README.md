# Challenge Interface

## TODO
* PyTests
* Comment code

## API Schema
| Method | URL | Headers | Payload | Description | Status |
|:------:|:------------------------------:|:------------:|:-----------------------------------------:|:------------------------------------:|:------:|
| GET | /api/auth | Access-Token | / | Infos über eigenen Account | Done |
| POST | /api/auth |  | username, password | Login | Done |
| DELETE | /api/auth | Access-Token | / | Logout | Done |
|||||||
| GET | /api/roles | Access-Token | / | Get all Roles | Done |
| POST | /api/roles | Access-Token | name, description | Admin: Create Role | Done |
| PUT | /api/roles/<id:int> | Access-Token | description | Admin: Modify Role Description | Done |
| DELETE | /api/roles/<id:int> | Access-Token | / | Admin: Delete Role | Done |
|||||||
| GET | /api/users | Access-Token | / | Admin: Get all Accounts (Infos) | Done |
| GET | /api/users/<uuid:string> | Access-Token | / | Admin: Get Account by UUID | Done |
| POST | /api/users |  | username, email, password | Register a new Account | Done |
| POST | /api/users | Access-Token | username, email, password, role | Admin: Create a new Account | Done |
| PUT | /api/users/<uuid:string> | Access-Token | username (and/or) email (and/or) password | Admin: Update User (by UUID) | Done |
| PUT | /api/users/me | Access-Token | username (and/or) email (and/or) password | Update your Account | Done |
| DELETE | /api/users/<uuid:string> | Access-Token | / | Admin: Delete User (by UUID) | Done |
| DELETE | /api/users/me | Access-Token | / | Delete your Account | Done |
|||||||
| GET | /api/challenges | Access-Token | / | Get all Challenges | Done |
| GET | /api/challenges/<name:string> | Access-Token | / | Get Challenge | Done |
| POST | /api/challenges | Access-Token | name, description, category, flag | Create Challenge | Done |
| PUT | /api/challenges/<id:int> | Access-Token | ytChallengeId (and/or) ytSolutionId (and/or) description | Update Challenge (Youtube Video IDs and/or Description) | Done |
|||||||
| GET | /api/solve/ | Access-Token | / | Get all solved challenges | Done |
| POST | /api/solve/<id:int> | Access-Token | flag | Solv Challenge | Done | |

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
|  | role | Integer(20) | foreign key -> role.id |
| roles | id | Integer(20) | primary key, auto increment |
|  | name | Varchar(80) |  |
|  | description | Varchar(100) |  |
| tokens | id | Integer(20) | primary key, auto increment |
|  | user | Integer(20) | foreign key -> user.id |
|  | token | Varchar(128) | unique |
|  | created | TimeStamp |  |
|  | expires | TimeStamp |  |
|  | broken | Integer(1) (boolean) |  |
| challenge | id | Integer(20) | primary key, auto increment |  
|  | flag | Varchar(80) | unique |  
|  | name | Varchar(80) | unique |  
|  | description | Varchar(512) |  |  
|  | ytChallengeId | Varchar(10) |  |  
|  | ytSolutionId | Varchar(10) |  |  
|  | category | Varchar(80) | |  
| url | id | Integer(20) | primary key, auto increment |  
|  | description | Varchar(100) |  |  
|  | url | Varchar(100) | unique |
|  | challenge | Integer(20) | foreign key -> challenge.id |  
| solved | id | Integer(20) | primary key, auto increment |  
|  | challenge | Integer(20) | foreign key -> challenge.id |
|  | user | Integer(20) | foreign key -> user.id |  
|  | timestamp | TimeStamp |  |  |

## Installation
* Install Docker
* Build Docker Image

```
git clone ssh://git@git.the-morpheus.de:322/challengeInterface/backend.git
docker build -t backend .
```

* Start Docker Container

```
docker run -it -p 8080:80 -e MYSQL_PASSWORD=myPassword backend
```

* Use docker-compose

```
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
      MYSQL_PASSWORD: myPassword
```
