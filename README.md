# Challenge Interface
## API Schema
| Method | URL | Headers | Payload | Description | Status |
|:------:|:------------------------------:|:------------:|:-----------------------------------------:|:------------------------------------:|:------:|
| GET | /api/auth | Access-Token | / | Infos über eigenen Account | Done |
| POST | /api/auth |  | username, password | Login | Done |
| DELETE | /api/auth | Access-Token | / | Logout | Done |
|  |  |  |  |  |  |
| GET | /api/users | Access-Token | / | Admin: Get all Accounts (Infos) | Done |
| GET | /api/users/<uuid:string> | Access-Token | / | Admin: Get Account by UUID | Done |
| POST | /api/users |  | username, email, password | Register a new Account | Done |
| PUT | /api/users/<uuid:string> | Access-Token | username (and/or) email (and/or) password | Admin: Update User (by UUID) | Done |
| PUT | /api/users/me | Access-Token | username (and/or) email (and/or) password | Update your Account | Done |
| DELETE | /api/users/<uuid:string> | Access-Token | / | Admin: Delete User (by UUID) | Done |
| DELETE | /api/users/me | Access-Token | / | Delete your Account | Done |
|  |  |  |  |  |  |
| GET | /api/challenges | Access-Token | / | Get all Challenges |  |
| GET | /api/challenges/<id:int> | Access-Token | / | Get Challenge by ID |  |
| POST | /api/challenges | Access-Token | category, flag, description, urls | Create Challenge |  |
| PUT | /api/challenges/<id:int> | Access-Token | ytChallengeId (and/or) ytSolutionId | Update Challenge (Youtube Video IDs) |  |
| PUT | /api/challenges/solve/<id:int> | Access-Token | flag | Solv Challenge |  |

## Database Schema
| Table | Attribute | Datatype (Length) (+ Description) | Settings | Description |
|:---------:|:-------------:|:---------------------------------:|:---------------------------:|:------------------------------------:|
| users | id | Integer(20) | primary key, auto increment | Infos über eigenen Account |
|  | publicId | Varchar(36) (for uuid4) | unique | Login |
|  | username | Varchar(80) | unique | Logout |
|  | email | Varchar(100) | unique |  |
|  | password | Blob(512) (sha512 Hash) |  | Admin: Get all Accounts (Infos) |
|  | lastLogin | TimeStamp |  | Admin: Get Account by UUID |
|  | created | TimeStamp |  | Register a new Account |
|  | role | Integer(20) | foreign key -> role.id | Admin: Update User (by UUID) |
| roles | id | Integer(20) | primary key, auto increment | Update your Account |
|  | name | Varchar(80) |  | Admin: Delete User (by UUID) |
|  | description | Varchar(100) |  | Delete your Account |
| tokens | id | Integer(20) | primary key, auto increment |  |
|  | user | Integer(20) | foreign key -> user.id | Get all Challenges |
|  | token | Varchar(128) | unique | Get Challenge by ID |
|  | created | TimeStamp |  | Create Challenge |
|  | expires | TimeStamp |  | Update Challenge (Youtube Video IDs) |
|  | broken | Integer(1) (boolean) |  | Solv Challenge |
| challenge | id | Integer(20) | primary key, auto increment |  |
|  | flag | Varchar(80) | unique |  |
|  | name | Varchar(80) |  |  |
|  | description | Varchar(512) |  |  |
|  | urls | Integer(20) | foreign key -> url.id |  |
|  | ytChallengeId | Varchar(10) |  |  |
|  | ytSolutionId | Varchar(10) |  |  |
|  | category | Integer(20) | foreign key -> category.id |  |
| url | id | Integer(20) | primary key, auto increment |  |
|  | description | Varchar(100) |  |  |
|  | url | Varchar(100) | unique |  |
| category | id | Integer(20) | primary key, auto increment |  |
|  | description | Varchar(100) |  |  |
| solved | id | Integer(20) | primary key, auto increment |  |
|  | challenge | Integer(20) | foreign key -> challenge.id |  |
|  | user | Integer(20) | foreign key -> user.id |  |
|  | timestamp | TimeStamp |  |  |
