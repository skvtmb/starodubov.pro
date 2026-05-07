---
title: "GEEKOM A5: How a Mini PC Replaced My Server"
slug: "geekom-a5-kak-mini-pk-zamenil-mne-server"
date: 2025-01-11T00:00:00+03:00
draft: false
summary: "How I dumped a bulky home server and replaced it with a compact GEEKOM A5. What was wrong with the old build, how I picked a replacement, and how it ended up."
categories: ["Technology"]
tags: ["mini-pc", "geekom", "amd", "ryzen", "computers", "review", "specs", "hardware", "server"]
---

![GEEKOM A5 Mini PC](/images/geekom-a5/geekom-1.jpeg "GEEKOM A5 Mini PC")

How I kicked a bulky server out from under my desk and found a box that's quiet, efficient and not annoying. If you're also tired of noise, extra iron and constant trade-offs — this might help.

## How it started

Until recently I had a full-blown server at home. On paper it looked great: a beefy platform, lots of ports, NVMe, room for VMs. Seemed like an ideal home NAS and service host.

![My old home server](/images/geekom-a5/old-server-1.jpeg "Old server in Ginzzu CL150 case")

At the core: a **HUANANZHI X99 BD4** motherboard on LGA2011-3, a Chinese clone of a server board. On top of it ran an **Intel Xeon E5-2680 v4** — fourteen cores, 28 threads. RAM was a mix: two 8 GB sticks plus two 16 GB sticks, **48 GB DDR4** total. System on a **256 GB** NVMe, cooled by an **A04**.

![Server internals](/images/geekom-a5/old-server-2.jpeg "HUANANZHI X99 BD4 server platform with Xeon E5-2680 v4")

All of this lived in a **Ginzzu CL150** case with tempered glass. Looked serious, ate space. Power came from a **Ginzzu SB500** 500W PSU. Networking via **Intel AX210 Desktop Kit** with Wi-Fi 6. A **GeForce GT 730** 2 GB was there only to push picture, the server CPU has no iGPU. Storage — an **ExeGate HS435-02** four-bay HDD cage.

![Server configuration](/images/geekom-a5/old-server-3.jpeg "Full old server configuration")

On paper the config was serious. Six SATA, four USB 3.0, quad-channel memory, an M.2 slot for fast storage. Specs-wise, a great base for VMs, a file dump and various services.

In reality it played out differently.

## First warning signs

The first thing that started getting to me was the noise. Even with quiet fans, the server hummed constantly. It didn't scream, but it was always there. Especially at night.

Then I started watching the electricity bill. A box running 24/7 ate a fair bit. And it heated up. Even in winter, the room with the server felt warmer than the others.

But the main problem wasn't the iron, it was the software.

## XPEnology experience: pretty isn't the same as reliable

I started with **XPEnology** on the server — an unofficial build of Synology firmware. Familiar UI, convenient, looks like a real Synology, but without paying for their hardware. Sounded perfect.

In practice the fun began. Updates — forbidden, any one of them could brick the system. Small bugs popped up constantly, I patched them by hand. Drives would randomly drop. XPEnology would stop seeing them, I'd reboot and hope they came back.

At some point I realized: this setup wasn't giving me what I'd built it for — reliability. From a home server I want one thing: that it just works. No surprises, no rituals, no babysitting.

## The turning point

That's when I called it. I didn't need an iron monster that demanded attention. I needed something simple, quiet and stable.

I started looking for options and ran into the **GEEKOM A5** mini PC. Palm-sized box. Specs — a real AMD Ryzen device, not a toy.

Then it clicked: what if the mini PC handles the brain and the drives go into a separate enclosure? That's how the **GEEKOM A5 + external DAS** (Direct Attached Storage) idea was born.

## The new setup

When the A5 arrived, the first thing I noticed was silence. After the server's constant hum, this box ran practically without a sound. There's a fan, but you almost don't hear it. First win.

![GEEKOM A5 - front view](/images/geekom-a5/geekom-1.jpeg "Compact GEEKOM A5")

Second win showed up about a month in: the electricity bill dropped noticeably. A mini PC pulls a lot less than a server platform sitting on 24/7.

![GEEKOM A5 - ports and connectors](/images/geekom-a5/geekom-2.jpeg "Rich set of ports on GEEKOM A5")

Third — the size. Instead of a big tower under the desk, there's a small box on a shelf you can almost miss.

![GEEKOM A5 in work environment](/images/geekom-a5/geekom-3.jpeg "GEEKOM A5 at the workstation")

## First impressions

For the first days I watched it. Is it stable? Will it choke on something? Will it handle my workload?

It handles. Boot is fast thanks to NVMe. Docker containers start without drama. The file dump on DAS works steadily. None of the glitches and drive drops I had on XPEnology.

A week in I'd forgotten there ever was a server under the desk. The new setup just works. No babysitting, no problems.

## What changed

Sometimes less really is more. Instead of a bulky, power-hungry server I got:

* **a quiet system** — no more constant humming
* **stable operation** — no random failures or drive drops
* **fewer workarounds** — I'm not patching bugs around the clock
* **more control** — I actually understand what's running and how

![GEEKOM A5 - side view](/images/geekom-a5/geekom-4.jpeg "Compact dimensions of GEEKOM A5")

The GEEKOM A5 turned out to be a solid base — not only for office work but for a home server too. Especially if, like me, you're tired of noise, extra iron and endless compromises.

## 📋 Full GEEKOM A5 Technical Specifications

### Main Specifications

#### Processor
* **Model**: AMD Ryzen 7 5825U
* **Architecture**: Zen 3
* **Cores**: 8 cores
* **Threads**: 16 threads
* **Base frequency**: 2.0 GHz
* **Max frequency (Boost)**: 4.5 GHz
* **TDP**: 15 W

#### Memory
* **Capacity**: 16 GB DDR4
* **Type**: DDR4 (dual-channel)
* **Expandable to**: up to 64 GB
* **Slots**: 2 SO-DIMM DDR4 slots

#### Storage
* **Capacity**: 512 GB SSD
* **Type**: NVMe PCIe 3.0 M.2 2280
* **Expandable to**: up to 2 TB
* **Slots**: 1 M.2 2280 PCIe 3.0 slot

#### Graphics
* **Integrated GPU**: AMD Radeon Vega 8
* **GPU cores**: 8
* **Video support**:
  * H.265/HEVC decoding
  * 4K video playback
  * Support for up to 4 monitors simultaneously

#### Ports and Interfaces

##### USB Ports
* **USB-C 3.2 Gen 2**: 1 port (with DisplayPort support)
* **USB-A 3.2 Gen 2**: 4 ports
* **USB-A 2.0**: none

##### Video Outputs
* **HDMI 2.0**: 2 ports (4K@60Hz support)
* **USB-C DisplayPort**: 1 port (via USB-C 3.2 Gen 2)
* **Connection support**: up to 4 monitors simultaneously

##### Network Interfaces
* **Ethernet**: 2.5 Gigabit Ethernet (RJ-45)
* **Wi-Fi**: Wi-Fi 6 (802.11ax)
* **Bluetooth**: Bluetooth 5.2

##### Other Ports
* **SD card reader**: SD/SDHC/SDXC support
* **Audio output**: 3.5 mm combo jack (headphones/microphone)

#### Operating System
* **Pre-installed OS**: Windows 11 Pro
* **License**: Windows 11 Pro (included)

#### Physical Characteristics
* **Dimensions**: 112 × 112 × 38 mm
* **Weight**: 500 g
* **Case material**: metal (aluminum)
* **Color**: black/silver
* **Cooling**: active (fan)

#### Power
* **Power supply**: external power adapter
* **Adapter power**: 65 W
* **Power connector**: USB-C (PD) or separate DC connector

#### Performance

##### Computational Performance
* Excellent performance for office tasks
* Good performance for web browsing and multitasking
* Support for light video and image processing
* Energy efficient for long operation

##### Graphics Performance
* Smooth 4K video playback
* Support for light and indie games
* Excellent performance for multimedia content

#### Warranty and Support
* **Warranty**: 3 years
* **Support**: official GEEKOM support
* **Online store**: [GEEKOM official site](https://www.geekom.ru/geekom-mini-pc-a-5/)

## 💾 GEEKOM A5 Advantages

* ✅ **Compact size** — takes minimal desk space
* ✅ **High performance** — AMD Ryzen 7 5825U provides excellent performance
* ✅ **Flexible connectivity** — support for up to 4 monitors simultaneously
* ✅ **Fast boot** — SSD provides fast system and app loading
* ✅ **Modern tech** — Wi-Fi 6, Bluetooth 5.2, USB-C
* ✅ **Quiet operation** — efficient cooling system
* ✅ **Easy to upgrade** — access to memory and SSD slots

## 🎯 GEEKOM A5 Use Cases

* 🏢 **Office work** — ideal for documents, spreadsheets, presentations
* 🎓 **Education** — great for students and educational tasks
* 🏠 **Home media center** — 4K video and multiple monitor support
* 💻 **Development** — suitable for web development and light coding
* 🖥️ **Home server** — excellent base for Docker, VMs, and file storage
* 📺 **Digital signage** — compact size makes it ideal for advertising screens
* 🎮 **Light gaming** — support for indie and older games

**Useful links:**

* 🌐 [Official device page](https://www.geekom.ru/mini-pc/geekom-a5)
* 📊 [Ryzen specs review in mini PCs](https://www.amd.com/ru/products/ryzen-processors)
* 🌐 [GEEKOM official site](https://www.geekom.ru/)
* 🛒 [GEEKOM A5 in store](https://www.geekom.ru/geekom-mini-pc-a-5/)
* 📖 [Documentation and support](https://www.geekom.ru/)

---

*To be continued — in future articles I'll cover DAS, filesystem, and chosen software.*
