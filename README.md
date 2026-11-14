## Future work

- [ ] Move the Python parser container to the host running the mail server. Update its mail-server connection settings and confirm it can still reach the MySQL database securely.

# Phishing Report Parser

## Requirements

- Docker Engine
- Docker Compose

## Setup

1. Create the password files:

   ```text
   .secrets/db_root_password.txt
   .secrets/db_password.txt
   ```

   Put the MySQL root password in the first file and the application user's password in the second. Do not commit these files to GitHub.

2. Check that `requirements.txt`, `Dockerfile`, `parse_mail.py`, and `scripts/phishing_report_schema.sql` are in place.

3. Build and start the services:

   ```bash
   docker compose up --build
   ```

   The Python script runs once and exits. MySQL stays running.

## Managing the containers

Start the services in the background:

```bash
docker compose up -d --build
```

Stop the services without deleting database data:

```bash
docker compose down
```

See running and stopped containers:

```bash
docker compose ps -a
```

View logs:

```bash
docker compose logs
docker compose logs parse_mail
docker compose logs db
```

Run the Python script again:

```bash
docker compose run --rm --no-deps parse_mail
```

## Database

MySQL is available to other Compose services at hostname `db`, port `3306`. From the host computer, connect to `127.0.0.1`, port `3307`.

Database data persists in the `phishing-report-volume` named volume. The schema file is applied automatically when MySQL initializes a new, empty data volume.

## Remove database data

To stop the services and delete the database volume:

```bash
docker compose down -v
```

**This permanently deletes the MySQL data stored in the volume.** The schema will run again the next time MySQL starts with an empty volume.
