---
title: "MikroTik hAP ax3 from scratch: full RouterOS 7 configuration walkthrough"
date: 2026-03-07T00:00:00+03:00
draft: false
summary: "A practical walkthrough of a working MikroTik hAP ax3 setup on RouterOS 7: Wi‑Fi 6, DHCP, DoH, WireGuard, split-tunnel for AI and YouTube, BGP, firewall, scripts, and maintenance."
categories: ["Technology"]
tags: ["mikrotik", "routeros", "hap-ax3", "wireguard", "doh", "bgp", "networking", "home-router"]
cover:
  image: "/images/external/mikrotik-hap-ax3-diagram.png"
  alt: "MikroTik hAP ax³ — device block diagram (official)"
  caption: "Official hAP ax³ block diagram (source: MikroTik)"
---

When you get your hands on a device with Wi‑Fi 6 (802.11ax), it’s tempting not just to plug it in and forget it, but to understand what the new standard actually gives you, how to get the most out of it, and where the usual pitfalls are. I’ve put together a walkthrough of my own working **MikroTik hAP ax3** setup on **RouterOS 7.21.3** — from the overall design and reset through Wi‑Fi, VPN, BGP, and scripts. This isn’t a dry “click here” checklist; it’s more of a story about how things are wired and why. For a step-by-step “from scratch” guide with screenshots and benchmarks, a great reference is the [article on Gregory Gost about the hAP ax3 and RouterOS 7](https://gregory-gost.ru/mikrotik-perehodim-na-routeros-7-i-wi-fi-6-802-11ax-nastroika-hap-ax3/) (in Russian).

---

## 0. Brief overview of the hAP ax3 and RouterOS 7

![MikroTik hAP ax³ block diagram — chip and interface layout](/images/external/mikrotik-hap-ax3-diagram.png "Official hAP ax³ Block Diagram, source: MikroTik")

The **hAP ax³** isn’t just “a box with antennas” — it’s a proper router with Wi‑Fi 6. Externally it follows the usual MikroTik style: black case, soft-touch finish, no frills. The image above is the official block diagram from the manufacturer (processor, radios, ports, USB). Product page with case photos and full specs: [mikrotik.com/product/hap_ax3](https://mikrotik.com/product/hap%5Fax3).

Under the hood: ARM 64-bit, **IPQ-6010** CPU (4 cores, 864–1800 MHz auto), 1 GB RAM, 128 MB NAND. Ports: one 2.5G and four gigabit Ethernet, plus USB 3.0 (up to 1.5 A) — handy for a backup stick. Wireless is advertised as **AX1800**: up to 574 Mbit/s on 2.4 GHz and 1200 Mbit/s on 5 GHz, two radios (Qualcomm QCN-5022 and QCN-5052), standards 802.11b/g/n/ax and 802.11a/n/ac/ax. So both legacy and new clients can connect, and new ones can use Wi‑Fi 6. Dimensions 251×130×39 mm, operating temperature −20 to +70 °C — more than enough for home.

**RouterOS 7** was first shown by MikroTik in 2019 at MUM Russia; the stable branch appeared in December 2021. All ARM devices now ship with v7 by default. It differs from v6 with a newer Linux kernel (5+): support for modern Wi‑Fi chips, 5G modems, and other hardware that didn’t exist on the old kernel. As of this writing there’s still no long-term branch for v7 — we run stable. One important detail: Wi‑Fi 6 on Qualcomm in ROS 7 is in a separate **wifi-qcom** package. When upgrading, you must install it together with the main package, or wireless won’t work. For full specs, board photos, and step-by-step setup, see the [Gregory Gost article](https://gregory-gost.ru/mikrotik-perehodim-na-routeros-7-i-wi-fi-6-802-11ax-nastroika-hap-ax3/) (in Russian).

---

## 1. What we’re building in the end

To avoid wandering through the sections blindly, here’s the big picture. The router is both the internet gateway (WAN via DHCP from the ISP) and the single hub for the home LAN and Wi‑Fi.

**Network and ports.** One port (`ether1`) is WAN; the other four plus Wi‑Fi are in one LAN bridge. So wired and wireless clients end up in the same subnet. Two SSIDs: a main one, say `home-wifi`, for phones, laptops, and the usual stuff; a separate `iot-guest` on 2.4 GHz for smart bulbs, sensors, the printer, and anything you don’t want mixed with main traffic. LAN is the usual `192.168.10.0/24`, router at `.1`, DHCP hands out addresses from a pool (e.g. 100–254).

**Internet and DNS.** We don’t trust the ISP for DNS: everything goes through **AdGuard DoH** on the router, and we redirect clients to it so that even with a manual DNS on a device, queries still go through our resolver.

**VPN and routing.** **WireGuard** and **L2TP/IPsec** are both set up — two options or a fallback. Some traffic (e.g. AI services and YouTube) goes over WireGuard via a separate routing table and mangle; the rest goes straight through the ISP. For bypassing blocks we use BGP subscriptions (antifilter.download and antifilter.network): routes are pulled in dynamically and traffic to the right prefixes goes over VPN.

**Security and housekeeping.** Management (SSH, Winbox) only from LAN. Firewall, DDoS protection, unnecessary services disabled. Plus scripts: backups to USB, RouterOS update checks and Telegram notifications, host reachability checks, collecting YouTube IPs from DNS cache and importing subnet lists. All of this is tied to the scheduler so it runs on its own.

Below is how to get to this setup step by step and what not to miss.

---

## 2. Where to start from scratch

If you’re starting with a box-fresh router and building the config from zero, a sensible order is:

First, hardware and base: upgrade RouterOS (Main package + **wifi-qcom** from Extra packages), rename interfaces, create the bridge, bring up Wi‑Fi (main and optionally IoT SSID). Then the LAN: addressing on the bridge, DHCP server, WAN client. After that, DNS and DoH, management access restrictions. Then VPN (WireGuard, and L2TP if you want), split-routing for the services you need, BGP and filters. Finally firewall, NAT, disabling unneeded service ports, NTP, logging, scripts, and scheduler. That way the config reads in layers and you’re less likely to break something that’s already working.

---

## 2.1. Reset and firmware update

Out of the box the router is preconfigured for a typical scenario. To build your own setup, reset the config. Connect to **Eth2** (red): on the factory config, Eth1 (green) is usually for the ISP cable, so after reset you won’t lose connectivity to your PC. Set a static IP on the PC (e.g. 192.168.88.250/24), connect via WinBox by MAC, and run:

```routeros
system reset-configuration no-defaults=yes skip-backup=yes
```

After reset the router has no IP — connect again by MAC. The default password is on the **Product information** label on the sliding tray under the case — “by the book,” no guessing.

A common mistake is to restore a backup from an old router and “tweak a bit.” OS version and hardware are different; better not to risk it. Safer: export the config from the previous device (`export file=myconfig`), save the file, and migrate settings in chunks, checking the docs. You’ll see mistakes more clearly and understand the config better.

To upgrade to the latest stable (or long-term when it exists for v7): download the **Main package** and from the **Extra packages** archive get the **wifi-qcom** package. Upload both to the router via WinBox and reboot. The router will pick them up and upgrade. After reboot, connect again and continue.

---

## 3. Disk and backup storage

The router has limited built-in storage (128 MB NAND), and you don’t want to fill it with heavy backups. Better to use a USB stick: create a partition and store both binary backups and text exports there. Example (adjust size for your stick):

```routeros
/disk
add parent=usb1 partition-number=1 partition-offset=512 partition-size=15676210688 type=partition
```

Backup and export files then live under e.g. `usb1-part1/backup/`. You don’t eat into the router’s storage, and if you reflash or replace the device, the archive is still there.

---

## 4. Interface naming

By default interfaces are ether1, ether2, etc. — easy to mix up in the config and in your head. Worth renaming them to something readable right away:

```routeros
/interface ethernet
set [ find default-name=ether1 ] name=LAN-Eth1
set [ find default-name=ether2 ] name=LAN-Eth2
set [ find default-name=ether3 ] name=LAN-Eth3
set [ find default-name=ether4 ] name=LAN-Eth4
set [ find default-name=ether5 ] name=LAN-Eth5
```

In my setup `LAN-Eth1` is actually used as WAN (ISP cable). The name is a bit misleading — something like `WAN-Eth1` would be clearer. But since it’s already in the working config I left it. If you’re building from scratch, you can choose clearer names so the interface list sorts and reads better.

---

## 5. LAN bridge

A single bridge ties all LAN interfaces and Wi‑Fi into one L2 segment:

```routeros
/interface bridge
add comment=LAN mtu=1500 name=LAN-Bridge protocol-mode=none
```

Add ports `LAN-Eth2`–`LAN-Eth5`, radios `LAN-wifi5ghz` and `LAN-wifi24ghz`, and the IoT virtual interface (`iot-guest`). Main network and “smart home” end up in the same subnet; separation is only by SSID and security profile, no VLANs. For a home setup that’s often enough; you can move IoT to a VLAN later if needed.

Adding bridge ports (create the IoT virtual interface in §8 and add it to the bridge then):

```routeros
/interface bridge port
add bridge=LAN-Bridge interface=LAN-Eth2
add bridge=LAN-Bridge interface=LAN-Eth3
add bridge=LAN-Bridge interface=LAN-Eth4
add bridge=LAN-Bridge interface=LAN-Eth5
add bridge=LAN-Bridge interface=LAN-wifi5ghz
add bridge=LAN-Bridge interface=LAN-wifi24ghz
add bridge=LAN-Bridge interface=iot-guest
```

---

## 6. Interface lists

So that firewall and NAT don’t depend on a specific port (which you might swap later), RouterOS **interface lists** are handy. I use three: `LAN` (the bridge), `WAN` (ISP port), `VPN` (WireGuard interface). All filter, NAT, raw, and mangle rules use these lists. Change a port — update list membership; the rules stay the same.

Create the lists and assign interfaces:

```routeros
/interface list
add name=LAN
add name=WAN
add name=VPN comment=VPN

/interface list member
add interface=LAN-Bridge list=LAN
add interface=LAN-Eth1 list=WAN
add interface=wireguard1 list=VPN
```

Optionally set **neighbor discovery** only for LAN: `/ip neighbor discovery-settings set discover-interface-list=LAN`.

---

## 7. Wi‑Fi 6: main home network

This is the interesting part: why we bought an AX device in the first place. In RouterOS 7, Wi‑Fi is under **WiFi** — Security, Channel, Configuration; there’s no separate “Advanced Mode,” everything is in one place.

### What 802.11ax (Wi‑Fi 6) adds

Besides higher advertised speeds, you get things that actually matter in daily use. **Beamforming** — the router shapes the beam toward the client, so reception is more stable. **WPA3** gives stronger authentication. **OFDMA** (familiar from LTE) helps when many devices are on one AP — they interfere less. **QAM-1024** vs the old QAM-256 gives more bits per hertz. Plus 802.11r/k/v: fast roaming between APs, RRM (client can ask for a list of neighboring APs), WNM (network can suggest the client move to another channel). It’s all in the hardware and drivers; the main thing is not to disable it and to pick the right channel.

### 5 GHz in Russia: UNII-1 and the DFS trap

In Russia the 5 GHz situation is special. In practice only the **UNII-1** band (5170–5250 MHz) is widely available for consumer Wi‑Fi. The other bands (UNII-2, UNII-2 Extended, UNII-3) are either not licensed for home use or used by other services. And here’s the catch: on those bands **DFS** (Dynamic Frequency Selection) is in effect. If the router “hears” radar (and radar pulses are short, on the order of a fraction of a microsecond, and can be hard to tell from noise), it must switch channel. All clients drop at once — you’re working or watching something and the connection just dies. Annoying and unpredictable. You might find a “quiet” frequency in the DFS range by trial and error, but there are no guarantees: six months fine, then one day — channel change and disconnect.

The practical takeaway for a home network: fix the channel in **UNII-1**, e.g. **5180 MHz**, and disable DFS (`skip-dfs-channels=all` or `disabled`). Then Wi‑Fi won’t jump on its own. Channel width: 20, 40, or 80 MHz. 80 MHz uses the whole UNII-1 and gives max throughput, but in a dense environment everyone else is on 5 GHz too, and a narrower channel (20 or 40 MHz) is often more stable. To see which bands are allowed for your country (e.g. Russia):

```routeros
/interface wifi radio reg-info country=Russia number=0
```

The output lists allowed ranges, e.g. 2402–2482 (2.4 GHz) and 5170–5250 (UNII-1) and so on. More on 5 GHz in Russia, DFS, and tests in the [Gregory Gost article](https://gregory-gost.ru/mikrotik-perehodim-na-routeros-7-i-wi-fi-6-802-11ax-nastroika-hap-ax3/) (in Russian).

### Security profile and configuration

First create a security profile: WPA2 and WPA3, disable PMKID and WPS, enable **management protection** (usually required for WPA3). Then channels: for 5 GHz use 5180 MHz, disable DFS, set width 20/40/80 MHz as you like; for 2.4 GHz pick a channel (e.g. 2437), 20 MHz width. In the configuration attach the channel, set country (Russia), SSID, enable 802.11r (FT), multicast-enhance, and if you want RRM/WNM with a shared steering neighbor group so clients can roam smoothly between 2.4 and 5 GHz.

In ROS 7 the order is: **Security** (auth, passphrase) → **Channel** (band, frequency, width) → **Configuration** (channel + security + SSID + country) → assign the configuration to interfaces `wifi1` and `wifi2`. Sometimes the security profile has to be set both in the configuration and on the interface — behavior varies by version. Example template below (add your passphrase and names):

```routeros
/interface wifi security
add authentication-types=wpa2-psk,wpa3-psk disable-pmkid=yes management-protection=allowed name=sec1 wps=disable

/interface wifi channel
add band=5ghz-ax frequency=5180 name=ch5 skip-dfs-channels=all width=20/40/80mhz
add band=2ghz-ax frequency=2437 name=ch24 width=20mhz

/interface wifi configuration
add channel=ch5 country=Russia mode=ap name=cfg5ghz security=sec1 ssid=home-wifi
add channel=ch24 country=Russia mode=ap name=cfg24ghz security=sec1 ssid=home-wifi

/interface wifi
set [ find default-name=wifi1 ] configuration=cfg5ghz name=LAN-wifi5ghz security=sec1 disabled=no
set [ find default-name=wifi2 ] configuration=cfg24ghz name=LAN-wifi24ghz security=sec1 disabled=no
```

### Single SSID for 2.4 and 5 GHz with roaming

If you want one SSID on both bands and the phone or laptop to switch between 2.4 and 5 GHz by itself depending on signal — that’s what 802.11r/k/v are for. Enable **802.11r** (FT, Fast BSS Transition) in security or configuration: when switching to another AP or channel, keys are already agreed, so the drop is minimal. Optionally in steering enable **802.11k** (RRM) and **802.11v** (WNM): the client gets a list of neighboring APs and hints where to move. Use the same SSID in both configurations (2.4 and 5 GHz), and set a common `steering.neighbor-group` on both interfaces (it’s created automatically, e.g. `dynamic-SSID-xxxxxxxx`). Important: when to actually switch is decided by the client; the router only provides the info. In the logs you’ll see lines like “roamed to LAN-wifi24ghz, signal strength -69”.

---

## 8. Dedicated IoT network

Smart bulbs, sensors, the printer and similar don’t have to sit in the same network as the laptops. A separate SSID (e.g. `iot-guest`) on 2.4 GHz only with its own security profile is a simple way to separate them logically. In my setup they’re still in the same L2 as the main network (no VLAN), but on a different SSID; you can restrict access via access-list by MAC or move IoT to a VLAN later if needed.

**IoT security profile** (WPA2 only, no management protection). **Virtual interface** on the same 2.4 GHz radio; add it to the bridge. **Access-list**: `action=accept` with printer/sensor MAC if you allow only known devices.

```routeros
/interface wifi security
add authentication-types=wpa2-psk disable-pmkid=yes management-protection=disabled name=sec_iot wps=disable

/interface wifi
add comment=iot-guest configuration.mode=ap disabled=no master-interface=LAN-wifi24ghz name=iot-guest security=sec_iot
```

---

## 9. Kid Control

RouterOS can limit devices by schedule and by rate. In the config there’s a Kid Control profile for one user: devices bound by MAC, access windows and limits. The firewall has a jump to the kid-control chain so that traffic is handled by the right rules.

**Profile** (e.g. weekdays 7h–21h, Sat 6h–21h, rate-limit 2M) and **devices** by MAC:

```routeros
/ip kid-control
add name=kid-user fri=7h-21h sat=6h-21h rate-limit=2M

/ip kid-control device
add mac-address=AA:BB:CC:DD:EE:01 name=Phone user=kid-user
```

---

## 10. LAN addressing and DHCP

The router has `192.168.10.1/24` on `LAN-Bridge`. DHCP pool e.g. `192.168.10.100`–`192.168.10.254`. In DHCP options we give clients the router as DNS and NTP so everyone uses our DNS and the same time. For servers, cameras, NAS, and anything that should have a fixed IP, static leases by MAC — clearer in logs and reservations don’t drift.

**IP, pool, DHCP server and network, static lease** example:

```routeros
/ip address
add address=192.168.10.1/24 interface=LAN-Bridge network=192.168.10.0 comment=Local

/ip pool
add name=dhcp_pool1 ranges=192.168.10.100-192.168.10.254

/ip dhcp-server
add address-pool=dhcp_pool1 interface=LAN-Bridge name=dhcp_Lan

/ip dhcp-server network
add address=192.168.10.0/24 dns-server=192.168.10.1 gateway=192.168.10.1 ntp-server=192.168.10.1

/ip dhcp-server lease
add address=192.168.10.10 comment=NAS mac-address=AA:BB:CC:DD:EE:FF server=dhcp_Lan
```

---

## 11. WAN and basic internet

The ISP cable is on the WAN port; we get an address via DHCP. Important: `use-peer-dns=no` and `use-peer-ntp=no` so DNS and time are set on the router, not by the ISP. Then all clients reliably use our DoH and NTP.

```routeros
/ip dhcp-client
add comment=Internet interface=LAN-Eth1 use-peer-dns=no use-peer-ntp=no
```

---

## 12. DNS via AdGuard DoH

All DNS from the router and from clients (thanks to redirect) goes through **AdGuard DoH**. In `/ip dns` set `allow-remote-requests=yes`, DoH URL `https://dns.adguard-dns.com/dns-query`, `verify-doh-cert=yes`. To avoid a chicken-and-egg on the first query, add static A records for `dns.adguard-dns.com` (94.140.14.14, 94.140.15.15) as bootstrap. NAT redirects DNS (TCP and UDP) and NTP to the router for LAN clients: even if a device is configured with another DNS, traffic still goes through ours.

**DNS and DoH** (shorter timeouts so slow queries don't hang):

```routeros
/ip dns
set allow-remote-requests=yes query-server-timeout=1s query-total-timeout=4s use-doh-server=https://dns.adguard-dns.com/dns-query verify-doh-cert=yes
```

**Bootstrap** for DoH:

```routeros
/ip dns static
add address=94.140.14.14 name=dns.adguard-dns.com type=A comment="AdGuard DoH"
add address=94.140.15.15 name=dns.adguard-dns.com type=A comment="AdGuard DoH"
```

---

## 13. WireGuard

Interface `wireguard1`, listen-port 51820, its own /24 (e.g. 10.8.0.2/24). Peer is set with `allowed-address=0.0.0.0/0` — we don’t send all traffic over WG by default. A separate routing table and mangle decide which flows get the WireGuard gateway. That gives a clean split-tunnel without putting the whole network on VPN.

---

## 14. Split-tunnel for AI and YouTube

So that only traffic to AI services and YouTube goes over VPN and the rest via the ISP, a dedicated routing table `to_wg` has a default route via `wireguard1`. Mangle marks flows using address lists `ai_wg` and `youtube_wg` with `new-routing-mark=to_wg`. The lists are filled with domains and subnets (OpenAI, YouTube, etc.); keeping them in a separate export or scripts works well. Result: browser and apps use the internet as usual, and only the chosen services go through WireGuard.

**Mangle**: `action=mark-routing chain=prerouting dst-address-list=ai_wg` or `youtube_wg` `in-interface-list=LAN new-routing-mark=to_wg passthrough=no`. **Address-list** examples: `add address=api.openai.com list=ai_wg`; `add address=youtube.com list=youtube_wg`; add subnets as needed.

---

## 15. L2TP/IPsec client

Besides WireGuard there’s an L2TP client to your VPN server (e.g. `vpn.example.com`) with IPsec. Two VPNs give a fallback and let you split tasks between tunnels.

---

## 16. BGP and antifilter

For bypassing blocks we use BGP subscriptions: two instances (antifilter.download and antifilter.network), each with its router-id and AS. Peers: one over `wireguard1`, the other over WAN. Routing filters define which prefixes to accept and which gateway to use — all the “what to take and where to send” logic lives there, so the config doesn’t turn into hundreds of static routes.

---

## 17. Firewall filter

On input: accept established/related/untracked, ICMP, allow BGP from known peers; drop invalid; at the end drop everything not from LAN. To protect SSH and Winbox from brute force, aggressive attempts from WAN go to a blacklist. Forward: accept established/related, drop invalid, drop new from WAN that isn’t dstnat, then the DDoS chain and jump to kid-control. FastTrack is off — with mangle, WireGuard, BGP, and DDoS we need every packet to go through the filter.

**Input**: accept established/related/untracked, drop invalid, accept ICMP, accept BGP from peer IPs (45.154.73.71, 45.148.244.55), add-src-to-address-list mgmt_blacklist on connection-limit 20,32 for dst-port 22,8291 from WAN, drop mgmt_blacklist, drop in-interface-list=!LAN. **Forward**: jump kid-control, accept established/related, drop invalid, drop new from WAN not dstnat, jump detect_DDoS. **detect_DDoS** chain: dst-limit return; then add to ddos-targets and ddos-attackers.

---

## 18. DDoS protection

A separate chain `detect_DDoS` adds to address lists `ddos-targets` and `ddos-attackers` when thresholds are hit. In raw we drop those pairs so the main firewall isn’t overloaded. BGP peers are excluded from DDoS handling so we don’t lose the antifilter session.

---

## 19. NAT

Masquerade on WAN — all outbound internet traffic uses the router’s address. Separate masquerade on the WireGuard interface for traffic going to the VPN. Redirect DNS (TCP/UDP) and NTP (UDP) to the router for LAN clients so all queries go through our DNS and NTP.

**NAT**: `action=masquerade chain=srcnat out-interface-list=WAN`; `out-interface-list=VPN` for WG; redirect dst-port 53 (tcp+udp) and 123 (udp) to router for in-interface-list=LAN.

---

## 20. MSS clamp

Over a VPN tunnel MTU is usually lower, and large TCP segments start fragmenting or failing. In mangle for traffic via `wireguard1` we set change-mss for TCP with `new-mss=1380` so connections don’t hit the limit and stay stable.

---

## 21. Disabling unneeded service ports

In `/ip firewall service-port`, disable ftp, tftp, h323, sip, pptp and anything else you don’t use. Fewer open ports — smaller target for random scanners and bots.

---

## 22. Restricting management services

SSH and Winbox are allowed only from `192.168.10.0/24`. Telnet, www, api, api-ssl, ftp are disabled. For a home router that’s usually enough: no management from the internet, everything available from inside.

---

## 23. NTP, logging, and system settings

Timezone `Europe/Moscow`, router identity set to something recognizable (e.g. `home-ax3`) so logs and notifications are clear. Logging enabled for the topics you need. NTP client with your servers (e.g. regional NTP pools); NTP server on so the router both syncs and serves time to the LAN. You can also map LEDs to interfaces in `/system leds` — see the [Gregory Gost article](https://gregory-gost.ru/mikrotik-perehodim-na-routeros-7-i-wi-fi-6-802-11ax-nastroika-hap-ax3/) for an example.

**Clock, identity, NTP**:

```routeros
/system clock
set time-zone-autodetect=no time-zone-name=Europe/Moscow

/system identity
set name=home-ax3

/system ntp client
set enabled=yes

/system ntp server
set enabled=yes

/system ntp client servers
add address=0.pool.ntp.org
add address=1.pool.ntp.org
```

Use your own NTP servers. **Logging**: `/system logging add topics=account` and `topics=critical`. **Cloud**: `/ip cloud set update-time=no`.

---

## 24. Scripts (from export structure)

Manual maintenance gets old fast: checking for updates, making sure the NAS is up, cleaning old backups. The config has several scripts on the scheduler that do this: backups to USB, RouterOS update check with Telegram notification, host ping with alert on failure, collecting YouTube IPs from DNS cache and importing subnet lists, plus sending log excerpts (e.g. user login/logout) to Telegram. Below are the script bodies as code. Replace placeholders (bot token, chat ID, passwords) with your own before use.

### Back_up_1

Creates a binary backup and text export in `usb1-part1/backup/`. Triggered from the Backup scheduler.

```routeros
:local currentTime [/system clock get time]
:local currentDate [/system clock get date]
:local backupFile ("usb1-part1/backup/backup-" . $currentDate . "-" . $currentTime . ".backup")
:local backupTXT ("usb1-part1/backup/backup-" . $currentDate . "-" . $currentTime . ".txt")
/system backup save name=$backupFile
/export show-sensitive file=$backupTXT
```

### Backup_2

Removes files in `usb1-part1/backup/` older than 30 days. Runs right after Back_up_1.

```routeros
{
   :local daysAgo 30
   :local filter "usb1-part1/backup/"
   :local curDate [/system clock get date]
   :local curMonth [:pick $curDate 5 7]
   :local curDay [:pick $curDate 8 10]
   :local curYear [:pick $curDate 0 4]

   :foreach i in=[/file find type=backup] do={
      :local fileDate [/file get number=$i last-modified]
      :set fileDate [:pick $fileDate 0 11]
      :local fileMonth [:pick $fileDate 5 7]
      :local fileDay [:pick $fileDate 8 10]
      :local fileYear [:pick $fileDate 0 4]
      :local sum 0
      :set sum ($sum + (($curYear - $fileYear) * 365))
      :set sum ($sum + (($curMonth - $fileMonth) * 30))
      :set sum ($sum + ($curDay - $fileDay))
      :if ($sum >= $daysAgo && [/file get number=$i name] ~ $filter) do={
         /file remove $i
      }
   }

   :foreach i in=[/file find type=script] do={
      :local fileDate [/file get number=$i last-modified]
      :set fileDate [:pick $fileDate 0 11]
      :local fileMonth [:pick $fileDate 5 7]
      :local fileDay [:pick $fileDate 8 10]
      :local fileYear [:pick $fileDate 0 4]
      :local sum 0
      :set sum ($sum + (($curYear - $fileYear) * 365))
      :set sum ($sum + (($curMonth - $fileMonth) * 30))
      :set sum ($sum + ($curDay - $fileDay))
      :if ($sum >= $daysAgo && [/file get number=$i name] ~ $filter) do={
         /file remove $i
      }
   }
}
```

### Telegram

Checks for a new RouterOS version and sends a Telegram notification if found. **Replace `YOUR_BOT_TOKEN` and `YOUR_CHAT_ID` with your values.**

```routeros
:local TGSendMessage do={
    :local tgUrl ("https://api.telegram.org/bot" . $Token . "/sendMessage?chat_id=" . $ChatID . "&text=" . $Text . "&parse_mode=html&disable_web_page_preview=True")
    /tool fetch http-method=get url=$tgUrl keep-result=no
}

:local TelegramBotToken "YOUR_BOT_TOKEN"
:local TelegramChatID "YOUR_CHAT_ID"
:local DeviceName [/system identity get name]
:local TelegramMessageText ("<b>" . $DeviceName . ":</b>  ")

:local MyVar [/system package update check-for-updates as-value]
:local Chan ($MyVar -> "channel")
:local InstVer ($MyVar -> "installed-version")
:local LatVer ($MyVar -> "latest-version")

:if ($InstVer = $LatVer) do={
    :set TelegramMessageText ($TelegramMessageText . "System is already up to date")
} else={
    :set TelegramMessageText ($TelegramMessageText . "New version " . $LatVer . " is available! [Installed: " . $InstVer . ", channel " . $Chan . "].")
    $TGSendMessage Token=$TelegramBotToken ChatID=$TelegramChatID Text=$TelegramMessageText
}

:log info $TelegramMessageText
```

### check-host-and-alert

Pings a host; if no replies, sends an alert to Telegram. **Replace `YOUR_BOT_TOKEN`, `YOUR_CHAT_ID`, and the host IP if needed.**

```routeros
# IP of the host to check (e.g. NAS or server on LAN)
:local host "192.168.10.10"

:local telegramToken "YOUR_BOT_TOKEN"
:local chatId "YOUR_CHAT_ID"
:local message ("Host " . $host . " unreachable!")

:local result [/ping $host count=3]

:if ($result = 0) do={
    /tool fetch url=("https://api.telegram.org/bot" . $telegramToken . "/sendMessage?chat_id=" . $chatId . "&text=" . $message) keep-result=no
    :log warning ("Host " . $host . " unreachable. Alert sent to Telegram.")
} else={
    :log info ("Host " . $host . " reachable (" . $result . " replies).")
}
```

### youtube dns

Collects YouTube IPs from DNS cache and adds them to address-list `youtube_dns_ips` (timeout 2d). No secrets.

```routeros
:foreach i in=[/ip dns cache find where (name~"youtube") or (name~"ytstatic") or (name~"ytimg") or (name~"googlevideo.com") or (name~"googleapis.com")] do={
  :local cacheName [/ip dns cache all get $i name]
  :local cacheType [/ip dns cache all get $i type]
  :delay delay-time=10ms
  :if ($cacheType="A") do={
    :local cacheData [/ip dns cache all get $i data]
    :if ([/ip firewall address-list find where address=$cacheData]="") do={
      :put ("add: " . $cacheName . " " . $cacheType . " " . $cacheData)
      /ip firewall address-list add address=$cacheData comment=$cacheName timeout=2d list=youtube_dns_ips
    }
  }
}
```

### youtube ip

Downloads the YouTube subnet list from iplist.opencck.org and imports it. No secrets.

```routeros
/tool fetch url="https://iplist.opencck.org/?format=mikrotik&site=youtube.com&data=cidr4" mode=https dst-path=iplist_v4_0cidr4.rsc
:delay 5s
:log info "Downloaded iplist_v4_0cidr4.rsc youtube.com"

/import file-name=iplist_v4_0cidr4.rsc
:delay 10s
:log info "New iplist_v4_0cidr4 added youtube.com"
```

### Log_allert

Selects new log entries by pattern (e.g. login/logout), optionally excludes by substring, builds text in `MSG` and runs TG_ME. Set your own filters in `IncludeMessages` and `ExcludeMessages`.

```routeros
:local IncludeMessages "logged in|logged out"
:local ExcludeMessages "user1|user2"
:local Topics "info|warning|error|critical"
:local MsgLength 100

:global LogId
:local Msg ""
:local Array [/log find where topics~$Topics message~$IncludeMessages]
:local End ([:len $Array] - 1)
:local Start ([:find $Array $LogId])

:if ([:len $Start] = 0) do={
    :set Start ($End + 1)
} else={
    :set Start ($Start + 1)
}

:if ($Start <= $End) do={
    :for i from=$Start to=$End do={
        :if (($ExcludeMessages = "") || !([/log get ($Array->$i) message] ~ $ExcludeMessages)) do={
            :set Msg ($Msg . "%0A" . [/log get ($Array->$i) time] . " " . [:pick [/log get ($Array->$i) message] 0 $MsgLength])
        }
    }
}

:set LogId ($Array->$End)

:if ($Msg != "") do={
    :global MSG
    :set MSG $Msg
    /system script run TG_ME
}
```

### TG_ME

Sends the global variable `MSG` to Telegram. **Replace `YOUR_CHAT_ID` and `YOUR_BOT_TOKEN` with your values.** Called from Telegram, check-host-and-alert, and Log_allert.

```routeros
:local ID "YOUR_CHAT_ID"
:local TKN "YOUR_BOT_TOKEN"
:global MSG

/tool fetch keep-result=no url=("https://api.telegram.org/bot" . $TKN . "/sendMessage?chat_id=" . $ID . "&text=" . [/system identity get name] . ": " . $MSG)
```


---

## 25. Scheduler

- **Backup** — every 5 days at 00:00:00: Back_up_1, then Backup_2.
- **Telegram** — daily at 16:00: Telegram script.
- **check-host** — every hour: check-host-and-alert.
- **Log_allert_daily** — daily at 22:00: Log_allert.

---

## 26. Security and practical notes

Already in place: services restricted, firewall input not open to the internet, DoH, DDoS logic, backup and cleanup, forced DNS/NTP to the router, WAN/VPN/LAN separation via interface lists.

Keep in mind: IoT is not in a separate VLAN; Telegram scripts may contain tokens and chat IDs in export — never publish a full `show-sensitive` export. For a next iteration: VLAN for IoT, a guest SSID, moving secrets out of script source, and renaming the WAN port to `WAN-Eth1`.

---

## 27. Manual configuration order

If you’re building the config by hand from scratch, a practical order is: rename interfaces → create LAN bridge and add ports → interface lists (LAN, WAN, VPN) → Wi‑Fi security, channel, configuration → enable wifi1/wifi2 → IoT SSID if needed → IP on bridge → DHCP pool and server → DHCP client on WAN → DNS and DoH, AdGuard bootstrap → WireGuard → routing table to_wg → address lists for AI/YouTube → mangle → BGP and filters → filter, raw, nat → service-port and `/ip service` → NTP, identity, logging → scripts and scheduler. At the end, `export show-sensitive` and save to an archive so you don’t lose your work.

---

## 29. Comparison with hAP ac and what you gain with ax3

A fair question: is it worth swapping an old hAP ac for an ax3, or is it “just another router”? In practice the difference is noticeable. On Gregory Gost they ran comparative tests: same scenario — iPerf3 (60 streams, 20 seconds, TCP) and a 20 GB file over SCP — first on hAP ac (RouterOS 6.49), then on hAP ax3 (RouterOS 7.15). Results look like this:

| Direction                | hAP ac       | hAP ax3      | Difference           |
|--------------------------|--------------|--------------|----------------------|
| Client → Server (sender)  | 434 Mbit/s   | 614 Mbit/s   | ~29% in favor of ax3  |
| Client → Server (receiver) | 378 Mbit/s | 595 Mbit/s   | ~36% in favor of ax3  |
| Server → Client (sender) | 340 Mbit/s   | 522 Mbit/s   | ~35% in favor of ax3  |
| Server → Client (receiver) | 335 Mbit/s | 493 Mbit/s   | ~32% in favor of ax3  |
| Download 20 GB file      | 27 MB/s      | 48 MB/s      | ~44% in favor of ax3  |
| Upload 20 GB file       | 47 MB/s      | 35 MB/s      | in this test ac was higher |

On average, Wi‑Fi gains are around 30–45%: higher speed and more stable. On 5 GHz the ax3 uses the link much better; with an ISP link up to 500 Mbit/s you can actually use it over Wi‑Fi. For detailed runs, graphs, and step-by-step setup from scratch see the [Gregory Gost article on hAP ax3 and RouterOS 7](https://gregory-gost.ru/mikrotik-perehodim-na-routeros-7-i-wi-fi-6-802-11ax-nastroika-hap-ax3/) (“Сравнительное тестирование” section, in Russian).

If you only need an access point without extra ports, **cAP ax** is an option: similar specs, and you can combine several with CAPsMAN for seamless Wi‑Fi across the home or office.

---

## Summary

You end up with more than a “Wi‑Fi box”: a full RouterOS setup under one roof — Wi‑Fi 6 with a dedicated IoT SSID and roaming between 2.4 and 5 GHz, DoH and forced DNS/NTP redirect, WireGuard and L2TP/IPsec, split-routing for AI and YouTube, BGP with antifilter, firewall, DDoS protection, USB backups, scheduler, and Telegram alerts. All of that fits in one device if you keep the config layered and avoid a heap of random rules. The article is long because the goal was not just to list items but to explain why each part is there and how it fits with the rest. For step-by-step setup from scratch, reset, 5 GHz channel choice, and real benchmarks, the [detailed hAP ax3 and RouterOS 7 article on Gregory Gost](https://gregory-gost.ru/mikrotik-perehodim-na-routeros-7-i-wi-fi-6-802-11ax-nastroika-hap-ax3/) (in Russian) is highly recommended. Good luck with the setup.
