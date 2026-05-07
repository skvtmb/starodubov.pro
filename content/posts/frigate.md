---
title: "Полный гайд: установка Frigate на Yandex Cloud с NetBird"
date: 2025-02-14T00:00:00+03:00
draft: false
summary: "Поднимаю Frigate NVR на Yandex Cloud: NetBird VPN до домашних камер, Docker, отдельный диск под записи."
categories: ["Технологии"]
tags: ["frigate", "nvr", "видеонаблюдение", "yandex-cloud", "netbird", "vpn", "docker", "rtsp"]
cover:
  image: "/images/frigate/frigate-logo.svg"
  alt: "Frigate NVR — система видеонаблюдения с AI"
  caption: "Frigate NVR — локальное видеонаблюдение с детекцией объектов (логотип: [frigate.video](https://frigate.video))"
---

![Frigate NVR — система видеонаблюдения с AI](/images/frigate/frigate-logo.svg "Frigate NVR")
*Логотип: [frigate.video](https://frigate.video)*

# Полный гайд: установка Frigate на Yandex Cloud с подключением к домашней сети через NetBird

Поднимаю Frigate на VM в Yandex Cloud. Записи кладу на отдельный диск, до домашних камер хожу через NetBird VPN. Ниже — пошагово, как я это делал.

В гайде:

* настройка NetBird
* подключение сервера к домашней сети
* монтирование диска
* установка Docker и Docker Compose
* установка и настройка Frigate
* хранение записей
* доступ к Web UI

---

# Архитектура

![Yandex Cloud — облачная платформа](/images/frigate/yandex-cloud.svg "Yandex Cloud")
*Логотип: [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Yandex_Cloud_logo.svg)*

Как это работает. Камеры отдают RTSP на устройство в домашней сети (роутер, NAS или ПК). NetBird связывает его с VM в Yandex Cloud. Frigate в Docker забирает потоки по NetBird IP, пишет записи на отдельный диск, Web UI висит на 8971.

```
Домашние камеры
      │
      │ RTSP
      │
Домашний сервер / роутер
      │
      │ NetBird VPN
      │
Yandex Cloud VM
      │
      │ Docker
      │
      │ Frigate
      │
      └── /data/frigate/media (записи)
```

---

# Часть 1. Настройка NetBird

NetBird ([netbird.io](https://netbird.io)) используется для создания защищённой приватной сети между:

* сервером в Yandex Cloud
* домашней сетью

Зачем VPN: камеры за домашним NAT, Frigate в облаке. Пробрасывать порты на роутере я не хочу, поэтому связь через зашифрованный туннель. Сервер получает доступ к камерам так, будто они в одной сети.

Официальный сайт:

[https://app.netbird.io/](https://app.netbird.io/)

---

# Шаг 1. Регистрация и вход

Идём на:

[https://app.netbird.io/](https://app.netbird.io/)

Создаём аккаунт или логинимся. NetBird Cloud — это панель управления устройствами и правилами доступа. Без неё Setup Key создать не получится.

---

# Шаг 2. Создание Setup Key для сервера

Перейдите:

```
Access Control → Setup Keys
```

Нажмите:

```
Create Setup Key
```

Укажите:

Name:

```
yandex-cloud
```

Group:

```
remote
```

Сохраните Setup Key.

Пример:

```
6A40F5F1-777-XXXX
```

Setup Key — это токен подключения к сети. Привязывает сервер к группе `remote`. Отдельный ключ для облачного сервера нужен, чтобы потом в политиках отличать его от домашних устройств.

⚠️ Без Setup Key устройство может отвалиться от сети.

---

# Шаг 3. Установка NetBird на сервер Yandex Cloud

Подключаемся к серверу:

```bash
ssh skv@SERVER_IP
```

Ставим NetBird:

```bash
curl -fsSL https://pkgs.netbird.io/install.sh | sh
```

Поднимаем туннель:

```bash
sudo netbird up --setup-key YOUR_SETUP_KEY
```

Проверяем статус:

```bash
netbird status
```

Должно быть:

```
Connected: yes
```

После этого у сервера появится виртуальный IP в сети NetBird (например, `100.64.0.x`), и до домашних устройств можно ходить по нему как по локалке.

---

# Шаг 4. Установка NetBird дома

На домашнем сервере или компьютере:

```bash
curl -fsSL https://pkgs.netbird.io/install.sh | sh
```

```bash
sudo netbird up --setup-key YOUR_HOME_SETUP_KEY
```

Добавляем устройство в группу:

```
Home
```

Домашнее устройство (роутер, NAS или ПК с камерами) должно быть в группе `Home`. Группы — для сегментации: явно решаем, кто куда ходит.

---

# Шаг 5. Настройка правил доступа

Идём в:

```
Access Control → Policies
```

Создаём правило:

Source:

```
remote
```

Destination:

```
Home
```

Action:

```
Allow
```

У NetBird по умолчанию Zero Trust: устройства друг друга не видят, пока явно не разрешишь. Без этого правила ни ping, ни RTSP не пойдут.

---

# Шаг 6. Проверка соединения

Берём NetBird IP домашнего устройства:

Пример:

```
100.64.0.5
```

С сервера:

```bash
ping 100.64.0.5
```

Если ping проходит — сеть настроена, RTSP с камер тоже пойдёт.

---

# Часть 2. Подключение и монтирование диска

Системный диск в Yandex Cloud обычно 10–40 ГБ — для круглосуточной записи мало, забьётся за несколько дней. Я взял отдельный диск на 512 ГБ под `/data/frigate/media`.

Проверяем диски:

```bash
lsblk
```

Пример:

```
vda 40G
vdb 512G
```

---

# Шаг 7. Форматирование диска

```bash
sudo mkfs.ext4 /dev/vdb
```

Новый диск приходит сырым, без ФС. ext4 — стандартный выбор: журналирование, спокойно тянет большие видеофайлы. Команда удаляет всё, что было на диске.

---

# Шаг 8. Монтирование

```bash
sudo mkdir /data
sudo mount /dev/vdb /data
```

Без монтирования запись в `/data` уйдёт на системный диск. После `mount` всё, что пишется в `/data`, ложится на отдельный.

Проверяем:

```bash
df -h
```

---

# Шаг 9. Автомонтирование

Берём UUID:

```bash
sudo blkid /dev/vdb
```

Открываем fstab:

```bash
sudo nano /etc/fstab
```

И добавляем строку:

```
UUID=YOUR_UUID /data ext4 defaults,nofail 0 2
```

Без этого после ребута диск отвалится и Frigate перестанет писать. UUID беру вместо `/dev/vdb` — имена устройств могут поменяться, UUID нет. `nofail` нужен, чтобы система не повисла на загрузке, если диск временно недоступен.

---

# Шаг 10. Настройка прав

```bash
sudo mkdir -p /data/frigate/{config,media,db}
sudo chown -R skv:skv /data/frigate
```

`config`, `media`, `db` — для настроек, записей и БД. `chown` нужен, чтобы редактировать конфиги без `sudo` и чтобы Docker мог писать в эти каталоги.

---

# Часть 3. Установка Docker

![Docker — платформа контейнеризации](/images/frigate/docker.png "Docker")
*Логотип: [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Docker_(container_engine)_logo.png)*

Frigate раздаётся готовым Docker-образом со всеми зависимостями (Python, FFmpeg, детекторы). Через Docker не приходится возиться с окружением и версиями, обновление — просто рестарт с новым образом.

Обновляем систему:

```bash
sudo apt update
```

Ставим Docker:

```bash
sudo apt install docker.io -y
```

Запускаем:

```bash
sudo systemctl enable docker
sudo systemctl start docker
```

Добавляем себя в группу `docker`, чтобы запускать без `sudo`:

```bash
sudo usermod -aG docker skv
newgrp docker
```

Проверка:

```bash
docker ps
```

---

# Часть 4. Установка Docker Compose

```bash
sudo apt install docker-compose -y
```

Проверка:

```bash
docker compose version
```

Compose нужен, чтобы не таскать длинные `docker run` с флагами. Сервис описан в YAML, всё перезапускается одной командой `docker compose up -d`, конфиг можно держать в git.

---

# Часть 5. Установка Frigate

![Frigate — NVR с AI-детекцией объектов](/images/frigate/frigate-logo.svg "Frigate NVR")

Создаём compose-файл:

```bash
nano /data/frigate/docker-compose.yml
```

```yaml
services:
  frigate:
    container_name: frigate
    image: ghcr.io/blakeblackshear/frigate:stable
    restart: unless-stopped

    shm_size: "512mb"

    volumes:
      - /data/frigate/config:/config
      - /data/frigate/media:/media/frigate
      - /data/frigate/db:/db
      - /etc/localtime:/etc/localtime:ro

    ports:
      - "8971:8971"
      - "8554:8554"
      - "8555:8555/tcp"
      - "8555:8555/udp"

    environment:
      - TZ=Europe/Berlin
```

Что тут к чему:

* `shm_size: "512mb"` — Frigate держит кадры в shared memory для детекции. На 2–4 камеры 720p хватает 256–512 МБ. Меньше — получите «Bus error».
* `volumes` — `config` для настроек, `media` для записей, `db` для SQLite. `localtime` — чтобы время в логах и метаданных совпадало с системным.
* `8971` — Web UI и API. `8554` — RTSP-рестрим. `8555` — WebRTC для двусторонней связи с камерами.
* `TZ` — часовой пояс для времени событий.

---

# Часть 6. Создание конфигурации Frigate

```bash
nano /data/frigate/config/config.yml
```

```yaml
mqtt:
  enabled: false

record:
  enabled: true
  retain:
    days: 3
    mode: all

cameras: {}
```

Минимум для первого запуска. MQTT отключаю — он нужен только под Home Assistant. `record` пишет в режиме `all` (все кадры, не только при детекции) с хранением 3 дня. `cameras: {}` оставляю пустым — камеры добавляются позже через Web UI или руками в конфиг с RTSP-путём через NetBird IP, например `rtsp://100.64.0.5:554/stream1`.

---

# Часть 7. Запуск

```bash
cd /data/frigate

docker compose up -d
```

Проверка:

```bash
docker ps
```

`-d` запускает контейнер в фоне: терминал не висит на логах, после закрытия SSH контейнер продолжает работать.

---

# Часть 8. Получение пароля

```bash
docker logs frigate
```

или

```bash
docker logs frigate | grep password
```

Логин:

```
admin
```

При первом запуске Frigate генерит случайный пароль и кладёт его в лог. Сменить можно в настройках после входа.

---

# Часть 9. Доступ к Web UI

```
http://SERVER_IP:8971
```

Web UI — основной интерфейс: live с камер, зоны, маски, события, записи, добавление камер. В Security Groups Yandex Cloud не забудьте открыть 8971 для своего IP, иначе извне ничего не увидите.

---

# Часть 10. Проверка записи

```bash
ls /data/frigate/media
```

Это проверка, что Frigate пишет именно на отдельный диск. В `media/recordings` появятся каталоги по камерам и датам. Пока камер нет, каталоги пустые — это нормально, главное, что путь смонтирован и пишется.

---

# Структура

```
/data/frigate
 ├── config
 ├── media
 ├── db
 └── docker-compose.yml
```

`config` — конфиг и SQLite с событиями. `media` — записи, клипы, экспорты. `db` — дополнительные данные. `docker-compose.yml` — описание сервиса для перезапуска и обновлений.

---

# Готово

Frigate крутится на Yandex Cloud, ходит до домашних камер через NetBird, записи лежат на отдельном диске. Дальше — добавление камер, настройка зон и масок в Web UI.
