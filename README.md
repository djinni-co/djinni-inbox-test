# Djinni Inbox Test Task

Тестова задача для вакансії бекендера на Джин,\
https://djinni.co/jobs/596044-middle-senior-python-developer-v-komandu-dzhi/

## Задача

У вас є інбокс рекрутера, куди приходять відгуки на вакансії. Відгуків багато, ви хочете допомогти рекрутеру їх швидше розібрати за допомогою scoring-алгоритму.

Що треба зробити:

1. Придумати scoring algorithm для сортування відгуків за їх “якістю” - наскільки вони попадають або не попадають під вимоги вакансії. 
2. Придумати як показати цю інформацію на фронтенді.
3. Імплементувати це в коді і записати лум з результатами, див нижче.
4. Надіслати нам PR. Не забудьте додати посилання на лум! :-)

Що має бути в лум:
1. Demo. Як працює ваше рішення.
2. Code walkaround. Що ви зробили, чому саме так і що ще треба для релізу на прод.
3. Future ideas. Як може виглядати версія 2.0 цього алгоритма і що для цього вам потрібно? Уявіть що ви можете імплементувати будь-які зміни в то як зараз працює Джин.

Клієнта для лум можна скачати тут -
https://www.loom.com/

Безкоштовна версія дозволяє записувати луми до пʼяти хвилин, цього має вистачити.

Якщо залишились питання пишіть на @ovvshieee в телеграм. Удачі!

## 50 тис грн донат за найкраще рішення

Бонус від Джина :)

Автор найкращого рішення обирає фонд або збір для ЗСУ, на який Джин від вашого імені зробить донат на 50 тис грн.

Дедлайн для подачі PR - 23:59 12 листопада 2023.

Подаватися на вакансію не обовʼязково - можете зробити задачу just for fun. І підтримати важливий для вас збір на ЗСУ.

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

3. Check if the installation succeeds by opening the [http://localhost:8000/]()


4. Prepare the database 

run `docker ps` and get the CONTAINER ID of the postgres:image
You should see something like this, the `e180ffc7d5d6` is the container id of the pg container.

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
