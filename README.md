# Phishing Report System

## Requirements

- Docker Engine
- Docker Compose

## Setup and start

1. Create these password files:

   ```text
   .secrets/db_root_password.txt
   .secrets/db_password.txt
   ```

   Put the MySQL root password in the first file and the application user’s password in the second. Do not commit `.secrets/` to GitHub.

2. Make sure these project files are present:

   ```text
   Dockerfile
   requirements.txt
   parse_mail.py
   scripts/phishing_report_schema.sql
   ```

3. Build the Python image and start the services:

   ```bash
   docker compose up --build
   ```

   The Python script runs once and exits. The MySQL container continues running.

To start the services in the background:

```bash
docker compose up -d --build
```

## Manage the containers

Show running and stopped containers:

```bash
docker compose ps -a
```

View logs:

```bash
docker compose logs
docker compose logs parse_mail
docker compose logs db
```

Run the parser again:

```bash
docker compose run --rm --no-deps parse_mail
```

Stop the services without deleting database data:

```bash
docker compose down
```

## Database

The parser can reach MySQL on the Compose network using hostname `db` and port `3306`. From the host computer, MySQL is available at `127.0.0.1:3307`.

Open a MySQL prompt using the application account:

```bash
docker compose exec db mysql -u user -p phishing-db
```

Enter the application database password when prompted. At the `mysql>` prompt, enter SQL commands. Exit the prompt with:

```sql
exit
```

Database data persists in the `phishing-report-volume` named volume. The schema file is applied automatically only when MySQL initializes an empty data volume.

## Remove database data

To stop the services and delete the database volume:

```bash
docker compose down -v
```

**This permanently deletes the MySQL data stored in the volume.** The schema will run again the next time MySQL starts with an empty volume.

## Future work

- [ ] Move the Python parser container to the host running the mail server. Update its mail-server connection settings and confirm it can still reach the MySQL database securely.
