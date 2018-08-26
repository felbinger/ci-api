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
|||||||
| GET | /api/solve/ | Access-Token | | Get all solved challenges | |
| POST | /api/solve/<id:int> | Access-Token | flag | Solv Challenge |  | |

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
|  | name | Varchar(80) |  |  
|  | description | Varchar(512) |  |  
|  | ytChallengeId | Varchar(10) |  |  
|  | ytSolutionId | Varchar(10) |  |  
|  | category | Integer(20) | foreign key -> category.id |  
| challenge_url | id | Integer(20) | primary key, auto increment |  
|  | challenge | Integer(20) | foreign key -> challenge.id |  
|  | url | Integer(20) | foreign key -> url.id |  
| url | id | Integer(20) | primary key, auto increment |  
|  | description | Varchar(100) |  |  
|  | url | Varchar(100) | unique |  
| category | id | Integer(20) | primary key, auto increment |  
|  | description | Varchar(100) |  |  
| solved | id | Integer(20) | primary key, auto increment |  
|  | challenge | Integer(20) | foreign key -> challenge.id |
|  | user | Integer(20) | foreign key -> user.id |  
|  | timestamp | TimeStamp |  |  |
