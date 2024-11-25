# Link API

## Project Description

This project is an API for storing user links. It allows users to register, authenticate, and manage their links and collections of links.

## Functional Features

- **User Authentication**:
  - Registration (email, password)
  - Change password
  - Reset password
  - User authentication

- **Link Management**:
  - Create, edit, delete, and view links
  - Links include page title, short description, URL, image, link type, and timestamps

- **Collection Management**:
  - Create, edit, delete, and view collections of links
  - Each collection has a name and a short description

## Technologies

- Python 3.12+
- FastAPI
- Docker

## Running the Project

To run the project, use the following command from the root of the project:

```bash
docker compose --env-file .env -f contrib/docker/docker-compose.local.yaml -p docker up -d --build
```
## Prerequisites

Before running, ensure you have:

    Docker
    Docker Compose

Also run:

```shell
chmod +x contrib/docker/wait-for-it.sh
```

## API Documentation

The API documentation is available in Swagger at: http://localhost:8001/docs
## Notes

Links and collections must be unique for each user.

When adding a link, the service automatically extracts data from the Open Graph markup or from the title and meta description tags if Open Graph markup is absent.

## Contact Information

If you have any questions or suggestions, please contact the project author.

# Environment Variables

- **Domain**: A logical group of variables.
- The **Domains table** answers the question: *What will stop working if the variables in this domain are not set?*

## Domains

| Domain                 | Description                                      | Usage                                 |
|------------------------|--------------------------------------------------|---------------------------------------|
| app                    | Application configs                              | General application configuration     |
| db                     | PostgreSQL database                              | Store project models data             |
| unisender              | Variables related to sending email via Unisender | Configure messages to Unisender       |

## Variables

| Domain                 | Name                                 | Type | Default                                                          | Example                                                | Description                                                                                                                                                                                                             |
|------------------------|--------------------------------------|------|------------------------------------------------------------------|--------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| app                    | APP_SECRET_KEY                       | str  | secret                                                           | nrMEefHd3r57...                                        | Session middleware and password hash salt                                                                                                                                                                               |
| app                    | APP_DEBUG                            | str  | false                                                            | false                                                  | Whether to start application in debug mode                                                                                                                                                                              |
| db                     | DATABASE_URL                         | str  | -                                                                | postgresql+asyncpg://auth0_user:admin@db:5432/auth0_db | Async URL of the database                                                                                                                                                                                               |
| db                     | POSTGRES_DB                          | str  | auth0_db                                                         | auth0_db                                               | Name of the PostgreSQL database                                                                                                                                                                                         |
| db                     | POSTGRES_USER                        | str  | auth0_user                                                       | auth0_user                                             | Username for the PostgreSQL database                                                                                                                                                                                    |
| db                     | POSTGRES_PASSWORD                    | str  | -                                                                | -                                                      | Password for the PostgreSQL database                                                                                                                                                                                    |
| db                     | DB_ENGINE_OPTION_POOL_SIZE           | int  | 5                                                                | 5                                                      | Defines the number of connections that the database connection pool can maintain open simultaneously. This optimizes performance by reusing open connections rather than creating new ones for each request.            |
| db                     | DB_ENGINE_OPTION_MAX_OVERFLOW        | int  | 50                                                               | 50                                                     | Sets the maximum number of additional connections that can be created when all connections in the pool are in use. This is useful for handling peak loads when more resources are temporarily needed.                   |
| db                     | DB_ENGINE_OPTION_POOL_RECYCLE        | int  | 600                                                              | 600                                                    | Specifies the time (in seconds) after which a connection will be automatically closed and reopened. This helps prevent issues with connections that may be closed by the database server after being idle for too long. |
| db                     | DB_ENGINE_OPTION_POOL_PRE_PING       | bool | false                                                            | false                                                  | Determines whether to check (ping) the connection before using it. If enabled, the system will automatically test each connection before use to prevent errors due to inactive or closed connections.                   |
| -                      | JWT_SECRET_KEY                       | str  | 09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7 | -                                                      | Secret key used to sign JWT tokens                                                                                                                                                                                      |
| unisender              | UNISENDER_API_KEY                    | str  | -                                                                | -                                                      | ID of Unisender template to be sent to user after registration                                                                                                                                                          |
| unisender              | UNISENDER_SENDER_NAME                | str  | -                                                                | Eugene Dyatlov                                         | ID of Unisender template to be sent to user for password recovery                                                                                                                                                       |
| unisender              | UNISENDER_SENDER_EMAIL               | str  | -                                                                | evgenii.dyatlov06@gmail.com                            | ID of Unisender template to be sent to user for password recovery                                                                                                                                                       |
| unisender              | UNISENDER_DEFAULT_LIST_ID            | int  | -                                                                | 1                                                      | ID of Unisender template to be sent to user for password recovery                                                                                                                                                       |
| unisender              | UNISENDER_REGISTER_CODE_TEMPLATE_ID  | int  | -                                                                | 6319230                                                | ID of Unisender template to be sent to user after registration                                                                                                                                                          |
| unisender              | UNISENDER_PASSWORD_RESET_TEMPLATE_ID | int  | -                                                                | 6319230                                                | ID of Unisender template to be sent to user for password recovery                                                                                                                                                       |
| unisender              | UNISENDER_SENDING_TIMEOUT            | int  | -                                                                | 10                                                     | ID of Unisender template to be sent to user for password recovery                                                                                                                                                       |


## SQL Task
The mock database is created when docker compose is launched.

### SQL query:
```sql
SELECT u.email, COUNT(l.id) as count_links
FROM link_vault_users u
LEFT JOIN link_vault_links l ON u.id = l.user_id
WHERE u.deleted_at IS NULL
GROUP BY u.id, u.email, u.created_at
ORDER BY COUNT(l.id) DESC, u.created_at ASC
LIMIT 10;
```