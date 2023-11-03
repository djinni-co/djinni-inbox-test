# Djinni Sandbox

Lil Djinni for testing purposes

## Installation

### Prerequisites 

- Python 3.9
- Docker  

### Local setup

After cloning the repo:

1. Setup env

```bash
# Python virtual env
python3 -m venv venv
source venv/bin/activate
```

```bash
# Env variables
# Copy example file, change values if needed
cp .env.example .env
```

2. Build and run the docker container
```
docker-compose build
docker-compose up -d
```

3. Check if installation succeeds by opening the [http://localhost:8000/]()


4. Migrate the database 
```
docker-compose run web python ./app/manage.py migrate
```

5. Populate with test data

run `docker ps` and get the CONTAINER ID of the postgres:image
You'll see something like this, here `e180ffc7d5d6` is the container id of the pg container.

```
CONTAINER ID   IMAGE                COMMAND                  CREATED       STATUS       PORTS                    NAMES
9432a9884aad   djinni-sandbox-web   "python app/manage.p…"   7 hours ago   Up 7 hours   0.0.0.0:8000->8000/tcp   djinni-sandbox-web-1
e180ffc7d5d6   postgres:latest      "docker-entrypoint.s…"   7 hours ago   Up 7 hours   0.0.0.0:5432->5432/tcp   djinni-sandbox-db-1
```

Then run this command to write backup.sql onto djinni_sandbox db
```
cat backup.sql | docker exec -i CONTAINER ID psql --user admin djinni_sandbox
```

Good to go! 👍👍
