---
title: "Complete guide: installing Frigate on Yandex Cloud with NetBird"
date: 2025-02-14T00:00:00+03:00
draft: false
summary: "Setting up Frigate NVR on Yandex Cloud: NetBird VPN to home cameras, Docker, a separate disk for recordings."
categories: ["Technology"]
tags: ["frigate", "nvr", "video-surveillance", "yandex-cloud", "netbird", "vpn", "docker", "rtsp"]
cover:
  image: "/images/frigate/frigate-logo.svg"
  alt: "Frigate NVR — AI-powered video surveillance system"
  caption: "Frigate NVR — local video surveillance with object detection (logo: [frigate.video](https://frigate.video))"
---

![Frigate NVR — AI-powered video surveillance system](/images/frigate/frigate-logo.svg "Frigate NVR")
*Logo: [frigate.video](https://frigate.video)*

# Complete guide: installing Frigate on Yandex Cloud with home network access via NetBird

I'm running Frigate on a VM in Yandex Cloud. Recordings go to a separate disk, and the server reaches my home cameras over NetBird VPN. Below is how I did it, step by step.

In the guide:

* NetBird setup
* connecting the server to the home network
* mounting the disk
* installing Docker and Docker Compose
* installing and configuring Frigate
* recording storage
* Web UI access

---

# Architecture

![Yandex Cloud — cloud platform](/images/frigate/yandex-cloud.svg "Yandex Cloud")
*Logo: [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Yandex_Cloud_logo.svg)*

How it works. Cameras push RTSP to a device on the home network (router, NAS, or PC). NetBird connects that device to a VM in Yandex Cloud. Frigate in Docker pulls streams over the NetBird IP, writes recordings to a separate disk, Web UI sits on port 8971.

```
Home cameras
      │
      │ RTSP
      │
Home server / router
      │
      │ NetBird VPN
      │
Yandex Cloud VM
      │
      │ Docker
      │
      │ Frigate
      │
      └── /data/frigate/media (recordings)
```

---

# Part 1. NetBird setup

NetBird ([netbird.io](https://netbird.io)) is used to create a secure private network between:

* the Yandex Cloud server
* the home network

Why a VPN: cameras are behind home NAT, Frigate is in the cloud. I don't want to forward ports on the router, so I use an encrypted tunnel. The server reaches the cameras as if they were on the same LAN.

Official site:

[https://app.netbird.io/](https://app.netbird.io/)

---

# Step 1. Registration and login

Open:

[https://app.netbird.io/](https://app.netbird.io/)

Create an account or sign in. NetBird Cloud is the control plane for devices and policies. Without an account you can't create a Setup Key.

---

# Step 2. Creating a Setup Key for the server

Go to:

```
Access Control → Setup Keys
```

Click:

```
Create Setup Key
```

Specify:

Name:

```
yandex-cloud
```

Group:

```
remote
```

Save the Setup Key.

Example:

```
6A40F5F1-777-XXXX
```

A Setup Key is the join token for a device. It puts the server into the `remote` group. A separate key for the cloud server keeps it distinguishable from home devices in policies.

⚠️ Without a Setup Key, the device may drop off the network.

---

# Step 3. Installing NetBird on the Yandex Cloud server

Connect to the server:

```bash
ssh skv@SERVER_IP
```

Install NetBird:

```bash
curl -fsSL https://pkgs.netbird.io/install.sh | sh
```

Connect the server:

```bash
sudo netbird up --setup-key YOUR_SETUP_KEY
```

Check status:

```bash
netbird status
```

Should show:

```
Connected: yes
```

The server now has a virtual IP in the NetBird network (e.g. `100.64.0.x`) and can reach home devices over it like they're on the same LAN.

---

# Step 4. Installing NetBird at home

On the home server or computer:

```bash
curl -fsSL https://pkgs.netbird.io/install.sh | sh
```

```bash
sudo netbird up --setup-key YOUR_HOME_SETUP_KEY
```

Add the device to the group:

```
Home
```

The home device (router, NAS, or PC with cameras) goes into the `Home` group. Groups are for segmentation — you explicitly say who can reach whom.

---

# Step 5. Configuring access rules

Go to:

```
Access Control → Policies
```

Create a rule:

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

NetBird defaults to Zero Trust: devices can't see each other until you allow it. Without this rule neither ping nor RTSP will go through.

---

# Step 6. Verifying the connection

Get the NetBird IP of the home device:

Example:

```
100.64.0.5
```

From the server:

```bash
ping 100.64.0.5
```

If ping works, the network is up and RTSP from the cameras will also flow.

---

# Part 2. Connecting and mounting the disk

The system disk in Yandex Cloud is usually 10–40 GB — not enough for 24/7 recordings, it'll fill up in a few days. I attached a separate 512 GB disk for `/data/frigate/media`.

Check disks:

```bash
lsblk
```

Example:

```
vda 40G
vdb 512G
```

---

# Step 7. Formatting the disk

```bash
sudo mkfs.ext4 /dev/vdb
```

A new disk comes raw, without a filesystem. ext4 is the default choice — journaling, fine with large video files. The command wipes whatever was on the disk.

---

# Step 8. Mounting

```bash
sudo mkdir /data
sudo mount /dev/vdb /data
```

Without mounting, writes to `/data` go to the system disk. After `mount`, everything in `/data` lands on the separate disk.

Verify:

```bash
df -h
```

---

# Step 9. Auto-mounting

Get UUID:

```bash
sudo blkid /dev/vdb
```

Edit:

```bash
sudo nano /etc/fstab
```

Add:

```
UUID=YOUR_UUID /data ext4 defaults,nofail 0 2
```

Without this, the disk unmounts on reboot and Frigate stops writing. I use UUID instead of `/dev/vdb` because device names can change but the UUID doesn't. `nofail` keeps boot from hanging if the disk is temporarily unavailable.

---

# Step 10. Setting permissions

```bash
sudo mkdir -p /data/frigate/{config,media,db}
sudo chown -R skv:skv /data/frigate
```

`config`, `media`, `db` hold settings, recordings, and the database. `chown` lets me edit configs without `sudo` and lets Docker write to these directories.

---

# Part 3. Installing Docker

![Docker — containerization platform](/images/frigate/docker.png "Docker")
*Logo: [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Docker_(container_engine)_logo.png)*

Frigate ships as a Docker image with all the dependencies bundled (Python, FFmpeg, detectors). With Docker I skip the environment fiddling and version conflicts, and updates are a restart with a new image.

Update system:

```bash
sudo apt update
```

Install Docker:

```bash
sudo apt install docker.io -y
```

Start:

```bash
sudo systemctl enable docker
sudo systemctl start docker
```

Add my user to the `docker` group so I can run it without `sudo`:

```bash
sudo usermod -aG docker skv
newgrp docker
```

Verify:

```bash
docker ps
```

---

# Part 4. Installing Docker Compose

```bash
sudo apt install docker-compose -y
```

Verify:

```bash
docker compose version
```

Compose keeps me from juggling long `docker run` commands. The service is described in YAML, restart is one `docker compose up -d`, and the config can live in git.

---

# Part 5. Installing Frigate

![Frigate — NVR with AI object detection](/images/frigate/frigate-logo.svg "Frigate NVR")

Create compose file:

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

What's what:

* `shm_size: "512mb"` — Frigate keeps frames in shared memory for detection. For 2–4 cameras at 720p, 256–512 MB is enough. Less and you'll hit "Bus error".
* `volumes` — `config` for settings, `media` for recordings, `db` for SQLite. `localtime` keeps log and metadata timestamps in sync with the system.
* `8971` — Web UI and API. `8554` — RTSP restream. `8555` — WebRTC for two-way audio.
* `TZ` — timezone for event timestamps.

---

# Part 6. Creating Frigate configuration

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

Minimum for the first run. MQTT off — that's only useful with Home Assistant. `record` writes in `all` mode (every frame, not just on detection) with 3-day retention. `cameras: {}` is empty for now — cameras get added later via the Web UI or by hand in the config with an RTSP URL through the NetBird IP, e.g. `rtsp://100.64.0.5:554/stream1`.

---

# Part 7. Starting

```bash
cd /data/frigate

docker compose up -d
```

Verify:

```bash
docker ps
```

`-d` runs the container in the background — the terminal isn't tied up by logs, and the container keeps running after I close SSH.

---

# Part 8. Getting the password

```bash
docker logs frigate
```

or

```bash
docker logs frigate | grep password
```

Login:

```
admin
```

On the first run Frigate generates a random password and dumps it in the logs. You can change it in settings after logging in.

---

# Part 9. Accessing the Web UI

```
http://SERVER_IP:8971
```

The Web UI is Frigate's main interface: live view, zones, masks, events, recordings, adding cameras. Make sure port 8971 is open in Yandex Cloud Security Groups for your IP, otherwise you won't reach it from outside.

---

# Part 10. Verifying recording

```bash
ls /data/frigate/media
```

A check that Frigate is actually writing to the separate disk. `media/recordings` will fill with directories by camera and date. With no cameras yet, the directories stay empty — that's fine, what matters is that the path is mounted and writable.

---

# Structure

```
/data/frigate
 ├── config
 ├── media
 ├── db
 └── docker-compose.yml
```

`config` — config and the SQLite with events. `media` — recordings, clips, exports. `db` — extra Frigate data. `docker-compose.yml` — the service description for restarts and updates.

---

# Done

Frigate is running on Yandex Cloud, reaching home cameras via NetBird, recordings are on the separate disk. From here it's adding cameras and tuning zones and masks in the Web UI.
