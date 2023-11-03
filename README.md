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

Good to go! 👍👍
