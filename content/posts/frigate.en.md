---
title: "Complete Guide: Installing Frigate on Yandex Cloud with NetBird"
date: 2025-02-14T00:00:00+03:00
draft: false
summary: "Deploying Frigate NVR on Yandex Cloud: NetBird VPN, Docker, separate disk for recordings, and access to home cameras."
categories: ["Technology"]
tags: ["frigate", "nvr", "video-surveillance", "yandex-cloud", "netbird", "vpn", "docker", "rtsp"]
cover:
  image: "/images/external/frigate-logo.svg"
  alt: "Frigate NVR — AI-powered video surveillance system"
  caption: "Frigate NVR — local video surveillance with object detection"
---

![Frigate NVR — AI-powered video surveillance system](/images/external/frigate-logo.svg "Frigate NVR")

# Complete Guide: Installing Frigate on Yandex Cloud with Home Network Access via NetBird

This guide describes the full process of deploying the Frigate video surveillance system on a Yandex Cloud server with recordings stored on a separate disk and access to home cameras through the secure NetBird VPN.

The guide includes:

* NetBird setup
* connecting the server to the home network
* connecting and mounting the disk
* installing Docker and Docker Compose
* installing and configuring Frigate
* configuring video storage
* accessing the Web UI

---

# Architecture

![Yandex Cloud — cloud platform](/images/external/yandex-cloud-logo.svg "Yandex Cloud")

How it works: cameras stream RTSP to a device on the home network (router, NAS, or PC). NetBird connects this device to a virtual machine in Yandex Cloud. Frigate in Docker on the VM receives streams via NetBird IP, writes recordings to a separate disk, and serves the Web UI on port 8971.

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

# Part 1. NetBird Setup

![NetBird — Zero Trust VPN based on WireGuard](/images/external/netbird-logo.png "NetBird")

NetBird is used to create a secure private network between:

* the Yandex Cloud server
* the home network

**Why this is needed:** Cameras are at home, while Frigate is in the cloud. Without a VPN, the Yandex Cloud server cannot reach the RTSP streams from cameras in your local network. NetBird creates an encrypted tunnel between the cloud and home — cameras stay behind NAT, but the server can access them as if they were on the same network. This is safer than port forwarding on the router.

Official site:

[https://app.netbird.io/](https://app.netbird.io/)

---

# Step 1. Registration and login

Go to:

[https://app.netbird.io/](https://app.netbird.io/)

Create an account or sign in.

**Why:** NetBird Cloud manages all connected devices and access rules. Without an account, you cannot create a Setup Key and connect the server to the home network.

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

**Why:** The Setup Key is a one-time token for connecting a device to your NetBird network. It assigns the server to the `remote` group and allows you to configure rules for who can connect to whom. A separate key for the cloud server is needed to distinguish it from home devices in access policies.

⚠️ Important: use the Setup Key, otherwise the device may disconnect.

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

**Why:** The NetBird client on the server connects it to your private network and assigns it a virtual IP (e.g., 100.64.0.x). After that, the server can reach home devices via this IP as if they were on the same local network.

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

**Why:** The home device (router, NAS, or PC with cameras) must be on the NetBird network and in the `Home` group. Then, by access rules, the server from the `remote` group can connect to it. Groups are needed for segmentation: you explicitly allow who can access whom.

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

**Why:** By default, NetBird uses Zero Trust — devices cannot see each other until you allow it. This rule says: "devices from the `remote` group (cloud server) can connect to devices from the `Home` group." Without it, ping and RTSP connections to cameras will fail.

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

If it works — the network is configured.

**Why:** This confirms that the VPN works and the cloud server can reach the home network. If ping succeeds, Frigate will also be able to receive RTSP streams from cameras via the NetBird IP.

---

# Part 2. Connecting and mounting the disk

**Why a separate disk:** The system disk (vda) in Yandex Cloud is usually 10–40 GB — not enough for video recordings. Frigate writes 24/7, and space runs out in a few days. A separate disk (vdb) of 256–512 GB provides room for recordings with configurable retention.

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

**Why:** A new disk comes "raw" — without a filesystem. `mkfs.ext4` creates ext4, which works well on Linux: journaling, stability on failure, good support for large video files. Important: formatting erases all data on the disk.

---

# Step 8. Mounting

```bash
sudo mkdir /data
sudo mount /dev/vdb /data
```

**Why:** The disk must be "attached" to a directory so the system can use it. Without mounting, writes to `/data` go to the system disk. After `mount`, everything written to `/data` is stored on the separate disk.

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

**Why:** After reboot, the disk would unmount and Frigate would stop writing recordings. The `/etc/fstab` entry makes the system automatically mount the disk on boot. UUID is used instead of `/dev/vdb` because device names can change, while the disk UUID is stable. `nofail` prevents the system from hanging on boot if the disk is temporarily unavailable.

---

# Step 10. Setting permissions

```bash
sudo mkdir -p /data/frigate/{config,media,db}
sudo chown -R skv:skv /data/frigate
```

**Why:** Frigate in Docker will run as your user (or root in the container). The `config`, `media`, and `db` directories are for configuration, recordings, and the database. `chown` gives your user write access so you don't need `sudo` when editing configs and so Docker can write to these directories.

---

# Part 3. Installing Docker

![Docker — containerization platform](/images/external/docker-logo.png "Docker")

**Why Docker:** Frigate is distributed as a ready-made Docker image with all dependencies (Python, FFmpeg, detectors, etc.). Installing via Docker avoids manual environment setup, version conflicts, and simplifies updates — just restart the container with a new image.

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

Add user:

```bash
sudo usermod -aG docker skv
newgrp docker
```

Verify:

```bash
docker ps
```

**Why `usermod -aG docker`:** By default, only root can run containers. Adding the user to the `docker` group allows running Docker without `sudo`, which is more convenient and safer for daily use.

---

# Part 4. Installing Docker Compose

```bash
sudo apt install docker-compose -y
```

Verify:

```bash
docker compose version
```

**Why Docker Compose:** Instead of a long `docker run` command with many flags, Compose describes services in a YAML file. Easier to keep configuration in a repo, change parameters, and restart with a single `docker compose up -d` command.

---

# Part 5. Installing Frigate

![Frigate — NVR with AI object detection](/images/external/frigate-logo.svg "Frigate NVR")

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

**What each option does:**
* `shm_size: "512mb"` — Frigate stores frames in shared memory for detection. For 2–4 720p cameras, 256–512 MB is enough; if insufficient, you'll get a "Bus error".
* `volumes` — directory bindings: `config` for settings and DB, `media` for recordings and clips, `db` for SQLite. `localtime` is needed for correct timestamps in logs and metadata.
* `8971` — Web UI and API (with auth). `8554` — RTSP restream for cameras. `8555` — WebRTC for two-way communication with cameras.
* `TZ` — timezone for correct event time display.

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

**Why this config:** Minimal config for first run. MQTT is disabled — it's only needed for Home Assistant integration. `record` enables recording with 3-day retention in `all` mode (all frames, not just on detection). `cameras: {}` is empty — add cameras later via Web UI or manually in the config, specifying the RTSP path via NetBird IP (e.g., `rtsp://100.64.0.5:554/stream1`).

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

**Why `-d`:** The `-d` (detached) flag runs the container in the background. Without it, the terminal would be occupied by Frigate logs. The container keeps running after closing SSH.

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

**Why:** On first run, Frigate generates a random password and prints it in the logs. This protects the Web UI from unauthorized access. You can change the password in settings after logging in.

---

# Part 9. Accessing the Web UI

```
http://SERVER_IP:8971
```

**Why:** The Web UI is Frigate's main interface: live camera view, zone and mask configuration, event and recording playback, adding cameras. Make sure port 8971 is open in Yandex Cloud Security Groups for your IP, otherwise external access will be blocked.

---

# Part 10. Verifying recording

```bash
ls /data/frigate/media
```

**Why:** Verify that Frigate writes to the separate disk. In `media/recordings`, directories will appear by camera and date. If cameras aren't added yet, directories will be empty — that's normal. The main thing is that the path is mounted and writable.

---

# Structure

```
/data/frigate
 ├── config
 ├── media
 ├── db
 └── docker-compose.yml
```

**Directory purposes:** `config` — config and SQLite with events; `media` — recordings, clips, and exports; `db` — additional Frigate data; `docker-compose.yml` — service description for restart and updates.

---

# Done

Frigate is now running on Yandex Cloud with access to home cameras via NetBird.

Video is stored on a separate disk.

The system is ready for production use.
