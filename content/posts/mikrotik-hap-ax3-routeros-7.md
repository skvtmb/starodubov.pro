---
title: "MikroTik hAP ax3 с нуля: полный разбор конфигурации на RouterOS 7"
date: 2026-03-07T00:00:00+03:00
draft: false
summary: "Разбор рабочей конфигурации роутера MikroTik hAP ax3 на RouterOS 7: Wi‑Fi 6, DHCP, DoH, WireGuard, split-tunnel для AI и YouTube, BGP, firewall, скрипты и обслуживание."
categories: ["Технологии"]
tags: ["mikrotik", "routeros", "hap-ax3", "wireguard", "doh", "bgp", "сеть", "домашний-роутер"]
cover:
  image: "https://cdn.mikrotik.com/web-assets/product_files/C53UiG5HPaxD2HPaxD_240530.png"
  alt: "MikroTik hAP ax³ — блок-схема устройства (Block Diagram)"
  caption: "Официальная блок-схема hAP ax³ (источник: MikroTik)"
---

Когда в руки попадает устройство с Wi‑Fi 6 (802.11ax), а не просто «ещё один роутер», хочется не только включить его и забыть, а разобраться: что именно даёт новый стандарт, как правильно выжать из него пользу и не наступить на типичные грабли. Я собрал в одном месте разбор своей рабочей конфигурации **MikroTik hAP ax3** на **RouterOS 7.21.3** — от схемы и сброса до Wi‑Fi, VPN, BGP и скриптов. Это не сухая инструкция «нажмите сюда», а скорее рассказ о том, как всё устроено и почему сделано именно так. Если нужна пошаговая настройка «с нуля» с картинками и тестами — отличный ориентир: [статья на Gregory Gost про hAP ax3 и RouterOS 7](https://gregory-gost.ru/mikrotik-perehodim-na-routeros-7-i-wi-fi-6-802-11ax-nastroika-hap-ax3/).

---

## 0. Кратко об устройстве hAP ax3 и RouterOS 7

![Блок-схема MikroTik hAP ax³ — расположение чипов и интерфейсов](https://cdn.mikrotik.com/web-assets/product_files/C53UiG5HPaxD2HPaxD_240530.png "Официальный Block Diagram hAP ax³, источник: MikroTik")

**hAP ax³** — это уже не «коробочка с антеннами», а полноценный роутер с Wi‑Fi 6. Внешне он продолжает линейку MikroTik: чёрный корпус, приятная soft-touch поверхность, ничего лишнего. На схеме выше — официальная блок-схема платы (Block Diagram) с сайта производителя: расположение процессора IPQ-6010, радиомодулей, портов и USB. Страница продукта с фотографиями корпуса и спецификацией: [mikrotik.com/product/hap_ax3](https://mikrotik.com/product/hap%5Fax3).

Под крышкой — ARM 64-bit, процессор **IPQ-6010** (4 ядра, авточастота 864–1800 МГц), 1 ГБ RAM и 128 МБ NAND. Порты: один на 2.5G и четыре гигабитных Ethernet, плюс USB 3.0 (до 1.5 А) — удобно для флешки с бэкапами. Беспроводная часть заявлена как **AX1800**: до 574 Mbit/s на 2.4 ГГц и до 1200 Mbit/s на 5 ГГц, два радиомодуля (Qualcomm QCN-5022 и QCN-5052), стандарты 802.11b/g/n/ax и 802.11a/n/ac/ax. То есть и старые устройства подключатся, и новые смогут использовать Wi‑Fi 6. Габариты 251×130×39 мм, рабочая температура от −20 до +70 °C — для дома с запасом.

**RouterOS 7** компания MikroTik впервые показала в 2019 году на MUM в России; стабильной ветка стала в декабре 2021-го. Сейчас на всех ARM-устройствах по умолчанию уже седьмая версия. От шестой её отличает новое ядро Linux (5+): поддержка современных Wi‑Fi чипов, 5G-модемов и другой периферии, которой не было на старом ядре. На момент написания статьи у v7 по-прежнему нет ветки long-term — живём на stable. Важный нюанс: Wi‑Fi 6 на чипах Qualcomm в ROS 7 вынесен в отдельный пакет **wifi-qcom**. При обновлении прошивки его нужно ставить вместе с основным пакетом, иначе беспроводная часть не заработает. Подробная спецификация, фото платы и пошаговая настройка — в [статье Gregory Gost](https://gregory-gost.ru/mikrotik-perehodim-na-routeros-7-i-wi-fi-6-802-11ax-nastroika-hap-ax3/).

---

## 1. Что мы в итоге строим

Чтобы не блуждать по разделам впустую, сразу обозначу общую картину. Роутер выступает и как точка входа в интернет (WAN по DHCP от провайдера), и как единый центр для домашней сети и Wi‑Fi.

**Сеть и порты.** Один порт (`ether1`) — WAN, четыре остальных плюс Wi‑Fi объединены в один LAN bridge. То есть и проводные устройства, и беспроводные оказываются в одной подсети. Два SSID: основной, условно `home-wifi`, для телефонов, ноутбуков и всего привычного; отдельный `iot-guest` на 2.4 ГГц — для умных лампочек, датчиков, принтера и прочего, что не хочется мешать с основным трафиком. Локальная сеть — классические `192.168.10.0/24`, роутер на `.1`, DHCP раздаёт адреса из пула (например 100–254).

**Интернет и DNS.** DNS не доверяем провайдеру: всё идёт через **AdGuard DoH** на роутере, а клиентов принудительно перенаправляем на него, чтобы даже при ручной настройке DNS на устройстве запросы шли через наш фильтр.

**VPN и маршрутизация.** Подняты **WireGuard** и **L2TP/IPsec** — два варианта на выбор или в запас. Часть трафика (например AI-сервисы и YouTube) уходит через WireGuard по отдельной routing table и mangle, остальное — напрямую через провайдера. Для обхода блокировок используются BGP-подписки (antifilter.download и antifilter.network): маршруты подтягиваются динамически, трафик к нужным префиксам уходит через VPN.

**Безопасность и обслуживание.** Доступ к управлению (SSH, Winbox) только из LAN. Firewall, DDoS-защита, отключённые лишние сервисы. Плюс скрипты: резервные копии на USB, проверка обновлений RouterOS и уведомления в Telegram, мониторинг доступности хоста, сбор IP для YouTube из DNS-кэша и импорт списков подсетей. Всё это завязано на scheduler, чтобы работало само.

Дальше — как к этой схеме прийти по шагам и что важно не упустить.

---

## 2. С чего начать с нуля

Если брать роутер «из коробки» и собирать конфиг с нуля, логичный порядок такой:

Сначала железо и база: обновить RouterOS (Main package + **wifi-qcom** из Extra packages), переименовать интерфейсы, собрать bridge, поднять Wi‑Fi (основной и при необходимости IoT SSID). Потом сеть: адресация на bridge, DHCP-сервер, WAN-клиент. Затем DNS и DoH, ограничение доступа к управлению. После этого — VPN (WireGuard, при желании L2TP), split-routing для нужных сервисов, BGP и фильтры. В конце — firewall, NAT, отключение лишних service-port, NTP, логирование, скрипты и scheduler. Так конфиг читается по слоям и меньше шансов что-то сломать в уже работающем.

---

## 2.1. Сброс и обновление прошивки

Роутер из коробки уже настроен под типовой сценарий. Чтобы собрать свою схему, конфигурацию лучше сбросить. Подключаться удобнее к порту **Eth2** (красный): у заводской конфигурации в Eth1 (зелёный) обычно предполагается кабель провайдера, и после сброса вы не потеряете связь с ПК. На компьютере выставляем статический IP, например 192.168.88.250/24, заходим в WinBox по MAC-адресу и выполняем:

```routeros
system reset-configuration no-defaults=yes skip-backup=yes
```

После сброса у роутера не будет IP — подключаемся снова по MAC. Заводской пароль написан на наклейке **Product information** на выдвижной площадке под корпусом — «всё как у взрослых», ничего не придумываем.

Частая ошибка — попытаться залить бэкап со старого роутера и «чуть подправить». Версия ОС и железо другие, лучше не рисковать. Разумнее экспортировать конфиг с предыдущего устройства (`export file=myconfig`), сохранить файл и переносить настройки по частям, сверяясь с документацией. Так и ошибки виднее, и понимание конфига выше.

Обновление до актуальной stable (или long-term, когда она появится для v7): скачиваем **Main package** и из архива **Extra packages** достаём пакет **wifi-qcom**. Оба файла перетаскиваем в WinBox на роутер и перезагружаем. Роутер сам подхватит пакеты и обновится. После перезагрузки снова заходим и продолжаем настройку.

---

## 3. Диск и хранение резервных копий

Встроенной памяти у роутера немного (128 МБ NAND), и таскать туда тяжёлые backup’ы не хочется. Удобнее сразу завести флешку: разбить её как отдельный раздел и складывать туда и бинарные backup’ы, и текстовые export’ы. Пример создания раздела (размер под свой носитель):

```routeros
/disk
add parent=usb1 partition-number=1 partition-offset=512 partition-size=15676210688 type=partition
```

Файлы резервных копий и экспортов тогда лежат, например, в `usb1-part1/backup/`. И место не жрём с роутера, и при перепрошивке или смене устройства архив под рукой.

---

## 4. Именование интерфейсов

По умолчанию интерфейсы называются ether1, ether2 и т.д. — в конфиге и в головах быстро путаешься. Имеет смысл сразу переименовать их во что читаемое:

```routeros
/interface ethernet
set [ find default-name=ether1 ] name=LAN-Eth1
set [ find default-name=ether2 ] name=LAN-Eth2
set [ find default-name=ether3 ] name=LAN-Eth3
set [ find default-name=ether4 ] name=LAN-Eth4
set [ find default-name=ether5 ] name=LAN-Eth5
```

В моей схеме `LAN-Eth1` по факту используется как WAN (кабель провайдера). Название, конечно, сбивает с толку — идеальнее было бы что-то вроде `WAN-Eth1`. Но раз уж в рабочем конфиге имя прижилось, я его не трогал. Если настраиваете с нуля, можно сразу задать осмысленные имена: так и в списке интерфейсов всё будет сортироваться понятнее.

---

## 5. Bridge для локальной сети

Один общий bridge объединяет все LAN-интерфейсы и Wi‑Fi в один L2-сегмент:

```routeros
/interface bridge
add comment=LAN mtu=1500 name=LAN-Bridge protocol-mode=none
```

В него добавляются порты `LAN-Eth2`…`LAN-Eth5`, радиомодули `LAN-wifi5ghz` и `LAN-wifi24ghz`, а также виртуальный интерфейс для IoT (`iot-guest`). И основная сеть, и «умный дом» оказываются в одной подсети; разделение только по SSID и security profile, без VLAN. Для домашнего сценария этого часто хватает: устройства видят друг друга, при необходимости можно вынести IoT в отдельный VLAN позже.

Добавление портов в bridge (виртуальный интерфейс IoT создаётся в §8 и тогда же добавляется в bridge):

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

## 6. Списки интерфейсов

Чтобы не привязывать firewall и NAT к конкретным портам (которые потом можно перекинуть), в RouterOS удобно пользоваться **interface list**. Я завёл три: `LAN` (в нём bridge), `WAN` (порт с провайдером), `VPN` (интерфейс WireGuard). Все правила фильтрации, NAT, raw и mangle ссылаются на эти списки. Поменял порт — обновил членство в списке, правила остаются теми же.

Создание списков и привязка интерфейсов (член списка = интерфейс, по которому потом фильтруем):

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

Дополнительно имеет смысл включить **neighbor discovery** только для LAN — чтобы WinBox и прочие утилиты видели роутер в списке соседей только с внутренней сети: `/ip neighbor discovery-settings set discover-interface-list=LAN`.

---

## 7. Wi‑Fi 6: основная домашняя сеть

Здесь самое интересное: ради чего вообще брали устройство с AX. Настройки в RouterOS 7 разнесены по меню **WiFi** — Security, Channel, Configuration; отдельного «Advanced Mode» больше нет, все опции на виду.

### Что даёт стандарт 802.11ax (Wi‑Fi 6)

Помимо заявленных скоростей, полезны вещи, которые реально чувствуются в быту. **Beamforming** — роутер «подстраивает» луч под клиента, приём и передача стабильнее. **WPA3** даёт более стойкую аутентификацию. **OFDMA** (то, что давно есть в LTE) помогает, когда к одной точке висит куча устройств — они меньше мешают друг другу. Модуляция **QAM-1024** против прежней QAM-256 даёт прирост бит на герц. Плюс 802.11r/k/v: быстрый роуминг между точками, RRM (клиент может запрашивать список соседних AP), WNM (сеть может подсказывать клиенту перейти на другой канал). Всё это уже заложено в железе и драйверах; главное — не отключать лишнего и правильно выбрать канал.

### 5 ГГц в России: UNII-1 и грабли с DFS

С 5 ГГц в нашей стране ситуация особая. По факту для гражданского Wi‑Fi широко доступен только диапазон **UNII-1** (5170–5250 МГц). Остальные диапазоны (UNII-2, UNII-2 Extended, UNII-3) либо не лицензированы под бытовой Wi‑Fi, либо используются другими службами. И вот тут подвох: на этих частотах работает **DFS** (Dynamic Frequency Selection). Если роутер «услышит» радар (а радарные импульсы короткие, порядка долей микросекунды, и их бывает сложно отличить от помех), он обязан сменить канал. В итоге все клиенты разом теряют связь — сидишь, работаешь или смотришь фильм, и в один момент всё обрывается. Неприятно и непредсказуемо. Найти «тихую» частоту в DFS-диапазоне методом тыка можно, но гарантий нет: полгода всё ок, потом в один день — смена канала и обрыв.

Практичный вывод для домашней сети: зафиксировать канал в **UNII-1**, например **5180 МГц**, и отключить DFS (`skip-dfs-channels=all` или `disabled`). Тогда Wi‑Fi не будет самопроизвольно перепрыгивать. Ширина канала — 20, 40 или 80 MHz. 80 MHz занимает весь UNII-1 и даёт максимум скорости, но в плотной застройке все соседи тоже сидят на 5 ГГц, и узкий канал (20 или 40 MHz) часто оказывается стабильнее. Узнать, какие диапазоны разрешены для страны, можно так (для России):

```routeros
/interface wifi radio reg-info country=Russia number=0
```

В выводе будут указаны допустимые диапазоны, например 2402–2482 (2.4 ГГц) и 5170–5250 (UNII-1) и далее. Подробнее про 5 ГГц в РФ, DFS и тесты — в [статье Gregory Gost](https://gregory-gost.ru/mikrotik-perehodim-na-routeros-7-i-wi-fi-6-802-11ax-nastroika-hap-ax3/).

### Профиль безопасности и конфигурация

Сначала создаём профиль безопасности: WPA2 и WPA3, отключаем PMKID и WPS, включаем **management protection** (для WPA3 он, как правило, обязателен). Потом — каналы: для 5 ГГц берём 5180 МГц, отключаем DFS, ширину 20/40/80 MHz по вкусу; для 2.4 ГГц — свой channel (например 2437), ширина 20 MHz. В конфигурации привязываем канал, страну (Russia), SSID, включаем 802.11r (FT), multicast-enhance и при необходимости RRM/WNM с общим steering neighbor group, чтобы клиенты могли плавно переключаться между 2.4 и 5 ГГц.

В ROS 7 логика такая: **Security** (аутентификация, passphrase) → **Channel** (band, frequency, width) → **Configuration** (channel + security + SSID + country) → вешаем configuration на интерфейсы `wifi1` и `wifi2`. Иногда security-профиль приходится указывать и в configuration, и прямо на интерфейсе — в разных версиях ведут себя по-разному. Ниже пример шаблона (passphrase и имена подставьте свои):

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

### Один SSID для 2.4 и 5 ГГц с роумингом

Если хочется один и тот же SSID для обоих диапазонов и чтобы телефон или ноутбук сам переключался между 2.4 и 5 ГГц в зависимости от уровня сигнала — это как раз то, для чего придуманы 802.11r/k/v. Включаем **802.11r** (FT, Fast BSS Transition) в security или configuration: при переключении на другую точку или канал ключи уже согласованы, разрыв минимальный. Дополнительно в steering можно включить **802.11k** (RRM) и **802.11v** (WNM): клиент получает список соседних AP и подсказки, куда перейти. Один и тот же SSID задаём в обеих configuration (2.4 и 5 ГГц), у обоих интерфейсов указываем общий `steering.neighbor-group` (он создаётся автоматически, вида `dynamic-SSID-xxxxxxxx`). Важно: когда именно переключаться — решает само клиентское устройство, роутер только даёт информацию. В логах потом можно увидеть строки вроде «roamed to LAN-wifi24ghz, signal strength -69».

---

## 8. Отдельная IoT сеть

Умные лампочки, датчики, принтер и прочая мелочь не обязательно должны сидеть в той же сети, что и ноутбуки. Отдельный SSID (например `iot-guest`) только на 2.4 ГГц с собственным security profile — простой способ логически отгородить их. В моей схеме они по-прежнему в одном L2 с основной сетью (без VLAN), но уже в отдельном SSID; при необходимости доступ можно ограничить через access-list по MAC или вынести IoT в отдельный VLAN.

**Security profile для IoT** — обычно только WPA2 (многие устройства ещё не поддерживают WPA3), без management protection. Отдельный профиль даёт свой пароль и при желании — другие настройки:

```routeros
/interface wifi security
add authentication-types=wpa2-psk disable-pmkid=yes management-protection=disabled name=sec_iot wps=disable
# passphrase задайте своим
```

**Виртуальный интерфейс** — «вторая точка доступа» на том же радиомодуле 2.4 ГГц, со своим SSID. Указываем master-interface (основной Wi‑Fi 2.4 ГГц), имя виртуального интерфейса и привязываем security:

```routeros
/interface wifi
add comment=iot-guest configuration.mode=ap disabled=no master-interface=LAN-wifi24ghz name=iot-guest security=sec_iot
```

В **bridge port** добавляем этот виртуальный интерфейс, чтобы трафик IoT шёл в тот же LAN-Bridge. **Access-list** по MAC нужен, если хотите явно разрешать только известные устройства (например принтер): тогда на интерфейсе IoT и при необходимости на основном 2.4 ГГц добавляете правило `action=accept` с `mac-address=AA:BB:CC:DD:EE:FF` (подставьте MAC принтера или датчика). Остальные по умолчанию могут быть reject или не подключаться без пароля — зависит от политики.

---

## 9. Kid Control

RouterOS умеет ограничивать устройства по расписанию и по скорости (rate-limit). В конфиге заведён профиль Kid Control для одного из пользователей: к нему привязаны устройства по MAC, заданы окна доступа и лимиты. В firewall добавлен jump в цепочку kid-control, чтобы трафик этих устройств обрабатывался по своим правилам.

**Профиль** — имя пользователя, дни/часы доступа и лимит скорости. Например: пн–пт (fri) 7:00–21:00, сб (sat) 6:00–21:00, лимит 2 Mbit/s:

```routeros
/ip kid-control
add name=kid-user fri=7h-21h sat=6h-21h rate-limit=2M
```

**Устройства** привязываются к профилю по MAC (и при желании имя для удобства):

```routeros
/ip kid-control device
add mac-address=AA:BB:CC:DD:EE:01 name=Phone user=kid-user
add mac-address=AA:BB:CC:DD:EE:02 name=Tablet user=kid-user
```

В **firewall filter** в цепочке forward в начале добавлен jump в цепочку `kid-control`, где по connection mark или по адресам устройств применяются ограничения. Так трафик с этих MAC обрабатывается по правилам Kid Control (расписание и rate-limit).

---

## 10. Адресация LAN и DHCP

Роутер получает адрес `192.168.10.1/24` на `LAN-Bridge`. Пул DHCP — например `192.168.10.100`–`192.168.10.254`. В опциях DHCP клиентам отдаём адрес роутера как DNS и NTP, чтобы все ходили через наш DNS и единое время. Для серверов, камер, NAS и прочего, что должно быть по постоянному IP, настроены статические lease по MAC — так и в логах понятнее, и резервирование не съезжает.

**IP на bridge** и **пул**:

```routeros
/ip address
add address=192.168.10.1/24 interface=LAN-Bridge network=192.168.10.0 comment=Local

/ip pool
add name=dhcp_pool1 ranges=192.168.10.100-192.168.10.254
```

**DHCP-сервер** — привязка к интерфейсу LAN-Bridge и пулу; **сеть** — та же подсеть, шлюз и DNS/NTP указываем на роутер, чтобы клиенты получали их через опции DHCP:

```routeros
/ip dhcp-server
add address-pool=dhcp_pool1 interface=LAN-Bridge name=dhcp_Lan

/ip dhcp-server network
add address=192.168.10.0/24 dns-server=192.168.10.1 gateway=192.168.10.1 ntp-server=192.168.10.1
```

**Статические lease** — по MAC закрепляем постоянный IP за камерой, NAS, умным устройством (comment для удобства):

```routeros
/ip dhcp-server lease
add address=192.168.10.10 comment=NAS mac-address=AA:BB:CC:DD:EE:FF server=dhcp_Lan
add address=192.168.10.70 comment=Camera mac-address=11:22:33:44:55:66 server=dhcp_Lan
```

---

## 11. WAN и базовый интернет

Кабель провайдера подключён к порту WAN; адрес получаем по DHCP. Важно: `use-peer-dns=no` и `use-peer-ntp=no`, чтобы DNS и время задавались на роутере, а не подставлялись от провайдера. Тогда все клиенты гарантированно идут через наш DoH и NTP.

Конкретно:

```routeros
/ip dhcp-client
add comment=Internet interface=LAN-Eth1 use-peer-dns=no use-peer-ntp=no
```

Роутер получит IP, маску и шлюз от провайдера, но не будет подставлять полученные от него DNS и NTP — их мы задаём в `/ip dns` и через NTP client на роутере.

---

## 12. DNS через AdGuard DoH

Все DNS-запросы с роутера и с клиентов (благодаря redirect) идут через **AdGuard DoH**. В `/ip dns` включаем `allow-remote-requests=yes`, прописываем DoH-URL `https://dns.adguard-dns.com/dns-query`, `verify-doh-cert=yes`. Чтобы при первом запросе не упереться в «курицу и яйцо», добавляем статические A-записи для `dns.adguard-dns.com` (94.140.14.14, 94.140.15.15) — bootstrap. В NAT настроен redirect DNS (TCP и UDP) и NTP на роутер для клиентов из LAN: даже если на устройстве прописать другой DNS, трафик всё равно пойдёт через наш.

**Настройка DNS и DoH** (таймауты уменьшаем, чтобы долгие запросы не висели):

```routeros
/ip dns
set allow-remote-requests=yes query-server-timeout=1s query-total-timeout=4s use-doh-server=https://dns.adguard-dns.com/dns-query verify-doh-cert=yes
```

**Bootstrap для DoH** — пока резолвера ещё нет, роутер должен знать IP AdGuard; добавляем две A-записи (у AdGuard два адреса):

```routeros
/ip dns static
add address=94.140.14.14 name=dns.adguard-dns.com type=A comment="AdGuard DoH"
add address=94.140.15.15 name=dns.adguard-dns.com type=A comment="AdGuard DoH"
```

После этого первый запрос к `dns.adguard-dns.com` пойдёт по одной из этих записей, и DoH заработает без «курицы и яйца».

---

## 13. WireGuard

Поднят интерфейс `wireguard1`, listen-port 51820, своя подсеть (например 10.8.0.2/24). Peer настроен с `allowed-address=0.0.0.0/0` — по умолчанию весь трафик через WG не гоняем. Кто куда идёт, решаем через отдельную routing table и mangle: помечаем нужные потоки и направляем их в таблицу с default gateway через WireGuard. Так получается аккуратный split-tunnel без перевода всей сети в VPN.

**Интерфейс** (private-key и peer добавляются своими — ключи в статью не подставляем):

```routeros
/interface wireguard
add listen-port=51820 mtu=1420 name=wireguard1
# private-key= и адрес на интерфейсе задаются при настройке
```

**Отдельная routing table** для трафика в VPN — в неё потом добавляется default route через wireguard1:

```routeros
/routing table
add fib name=to_wg
```

**IP на WireGuard** и **peer**: у роутера свой адрес в подсети туннеля (например 10.8.0.2/24); peer с `allowed-address=0.0.0.0/0`, `endpoint-address` и `endpoint-port` — адрес вашего WG-сервера, `persistent-keepalive=25s` — чтобы туннель не засыпал за NAT. Маршрут по умолчанию в таблице `to_wg` задаётся отдельным правилом: `dst-address=0.0.0.0/0 gateway=wireguard1 routing-table=to_wg`. Весь трафик, помеченный mangle в эту таблицу, пойдёт через WG.

---

## 14. Split-tunnel для AI и YouTube

Чтобы только трафик к AI-сервисам и YouTube шёл через VPN, а остальное — через провайдера, заведена отдельная routing table `to_wg` с default route через `wireguard1`. В mangle по address-list `ai_wg` и `youtube_wg` ставится mark-routing с `new-routing-mark=to_wg`. Списки пополняются доменами и подсетями (OpenAI, YouTube и т.п.); удобно вести их в отдельном export или скриптами (см. ниже). В итоге браузер и приложения ходят в интернет как обычно, а запросы к выбранным сервисам уходят через WireGuard.

**Mangle** — помечаем маршрутизацию для трафика из LAN, у которого destination попал в списки `ai_wg` или `youtube_wg`:

```routeros
/ip firewall mangle
add action=mark-routing chain=prerouting comment="Route AI via WireGuard" dst-address-list=ai_wg in-interface-list=LAN new-routing-mark=to_wg passthrough=no
add action=mark-routing chain=prerouting comment="Route YouTube via WireGuard" dst-address-list=youtube_wg in-interface-list=LAN new-routing-mark=to_wg passthrough=no
```

**Address-list** `ai_wg` и `youtube_wg` содержат домены (openai.com, api.openai.com, chatgpt.com, youtube.com, googlevideo.com и т.д.) и подсети (например 172.64.150.0/24, 173.194.0.0/16 для Google/YouTube). Домены резолвятся в IP при первом запросе; подсети добавляются вручную или скриптами. Примеры записей (остальные по тому же принципу):

```routeros
/ip firewall address-list
add address=api.openai.com list=ai_wg comment="AI split"
add address=openai.com list=ai_wg comment="AI split"
add address=youtube.com list=youtube_wg comment="YouTube split"
add address=142.250.150.0/24 list=youtube_wg comment="YouTube split"
```

---

## 15. L2TP/IPsec клиент

Помимо WireGuard настроен L2TP-клиент к своему VPN-серверу (например `vpn.example.com`) с IPsec. Две технологии — и запас на случай проблем с одной, и возможность раскидывать разные задачи по разным туннелям.

**Профиль PPP** для L2TP: трафик туннеля помечаем для interface-list=VPN (чтобы применять к нему свои правила и NAT), включаем сжатие и шифрование, change-tcp-mss — чтобы не ломать MTU по туннелю:

```routeros
/ppp profile
add bridge-learning=no change-tcp-mss=yes interface-list=VPN name=l2tp use-compression=yes use-encryption=yes use-mpls=no use-upnp=no
```

**L2TP-клиент**: адрес сервера, логин и пароль (и при необходимости IPsec secret) — свои; keepalive чтобы соединение не рвалось:

```routeros
/interface l2tp-client
add allow=mschap2 allow-fast-path=yes connect-to=vpn.example.com keepalive-timeout=30 name=L2TP-VPN profile=l2tp use-ipsec=yes user=your_l2tp_user
```

Пароль задаётся в **Secrets** (`/ppp secret`). IPsec: в **IPsec proposal** можно оставить aes-128-cbc; в **IPsec profile** — dh-group и enc-algorithm под ваш сервер. После подключения интерфейс L2TP появится в списке, и маршруты через него настраиваются по необходимости.

---

## 16. BGP и антифильтр

Для обхода блокировок используются BGP-подписки: два instance (antifilter.download и antifilter.network), свои router-id и AS. Подключение к пирам: один через `wireguard1`, второй через WAN. Routing filters определяют, какие префиксы принимать и через какой шлюз их отдавать — вся логика «что принимать и куда слать» сосредоточена в фильтрах, конфиг не превращается в сотни статических маршрутов.

**Instance** — по одному на подписку, свой router-id (обычно ваш внешний IP или произвольный уникальный в сети; в примере — документационный адрес, подставьте свой):

```routeros
/routing bgp instance
add as=64999 name=bgp-instance-1 router-id=203.0.113.1 comment="antifilter.download"
add as=64999 name=antifilter.network router-id=203.0.113.1 comment="antifilter.network"
```

**Template** — hold-time и keepalive для стабильной сессии, input filter задаёт, какие префиксы принять и с каким gateway (wireguard1 или WAN):

```routeros
/routing bgp template
add as=64999 hold-time=4m input.filter=bgp_in keepalive-time=1m multihop=yes name=tpl_antifilter_download routing-table=main
add as=64999 hold-time=4m input.filter=antifilter-in keepalive-time=1m multihop=yes name=tpl_antifilter_network routing-table=main output.network=bgp-networks
```

**Connection** — привязка к instance и template, адрес пира (у antifilter это публичные IP, например 45.154.73.71 и 45.148.244.55), remote AS. Один пир доступен через wireguard1 — для него добавляем статический маршрут до его IP через wireguard1; второй — через WAN (gateway провайдера). **Routing filter** в input задаёт правило вида: принять префиксы с нужными BGP communities и установить им gateway wireguard1 (или WAN). Детали фильтров смотрите в документации antifilter.download и antifilter.network.

---

## 17. Firewall filter

На input: принимаем established/related/untracked, ICMP, разрешаем BGP от известных peer; invalid дропаем; всё, что не из LAN, в конце дропаем. Для защиты от перебора по SSH и Winbox агрессивные попытки с WAN попадают в blacklist. Forward: established/related — accept, invalid — drop, с WAN без dstnat новое — drop, затем цепочка DDoS и jump в kid-control. FastTrack отключён — из-за mangle, WireGuard, BGP и DDoS нужен полный проход пакетов через фильтр.

**Input**: порядок правил — сначала разрешаем «нормальные» состояния и ICMP, потом BGP от IP пиров (чтобы не потерять сессию), затем защита портов 22 и 8291 — при превышении лимита соединений добавляем в blacklist и дропаем, в конце дроп всего не из LAN:

```routeros
/ip firewall filter
add action=accept chain=input connection-state=established,related,untracked comment="accept established,related,untracked"
add action=drop chain=input connection-state=invalid comment="drop invalid"
add action=accept chain=input protocol=icmp comment="accept ICMP"
add action=accept chain=input dst-port=179 protocol=tcp src-address=45.154.73.71 comment="BGP peer antifilter.download"
add action=accept chain=input dst-port=179 protocol=tcp src-address=45.148.244.55 comment="BGP peer antifilter.network"
add action=add-src-to-address-list address-list=mgmt_blacklist address-list-timeout=1d chain=input connection-limit=20,32 connection-state=new dst-port=22,8291 in-interface-list=WAN protocol=tcp comment="blacklist on limit"
add action=drop chain=input dst-port=22,8291 in-interface-list=WAN protocol=tcp src-address-list=mgmt_blacklist comment="drop blacklisted"
add action=drop chain=input in-interface-list=!LAN comment="drop all not from LAN"
```

**Forward**: jump в kid-control, затем accept established/related, drop invalid, drop новое с WAN не dstnat, jump в detect_DDoS для нового трафика с WAN (и при желании такой же jump для input на порты 22,80,443,8291). **Цепочка detect_DDoS**: при нормальной частоте — return; при превышении — add-dst-to-address-list ddos-targets и add-src-to-address-list ddos-attackers (timeout 10m).

---

## 18. DDoS-защита

Отдельная цепочка `detect_DDoS` по порогам добавляет в address-list `ddos-targets` и `ddos-attackers`. В raw эти пары дропаются, чтобы не нагружать основной firewall. BGP peer из DDoS-обработки исключены, иначе можно потерять сессию с антифильтром.

**Raw** — обрабатывается до filter; сначала разрешаем трафик до BGP peer (чтобы их не занести в DDoS по ошибке), затем дроп по паре attackers → targets:

```routeros
/ip firewall raw
add action=accept chain=prerouting dst-port=179 protocol=tcp src-address=45.148.244.55 comment="Bypass DDoS for BGP antifilter.network"
add action=accept chain=prerouting dst-port=179 protocol=tcp src-address=45.154.73.71 comment="Bypass DDoS for BGP antifilter.download"
add action=drop chain=prerouting dst-address-list=ddos-targets in-interface-list=WAN src-address-list=ddos-attackers comment="DDoS drop attackers->targets"
```

Цепочка **detect_DDoS** в filter при превышении dst-limit добавляет адреса в `ddos-targets` и `ddos-attackers`; raw затем режет трафик между ними без нагрузки на основные правила.

---

## 19. NAT

Masquerade на WAN — весь исходящий трафик в интернет уходит с адресом роутера. Отдельно masquerade на интерфейсе WireGuard для трафика, уходящего в VPN. Redirect DNS (TCP/UDP) и NTP (UDP) на роутер для клиентов из LAN — чтобы все запросы шли через наш DNS и NTP.

```routeros
/ip firewall nat
add action=masquerade chain=srcnat out-interface-list=WAN ipsec-policy=out,none comment="masquerade WAN"
add action=masquerade chain=srcnat out-interface-list=VPN comment="WG_NAT"
add action=redirect chain=dstnat dst-address-type=!local dst-port=53 in-interface-list=LAN protocol=tcp comment="Redirect DNS TCP to router"
add action=redirect chain=dstnat dst-address-type=!local dst-port=53 in-interface-list=LAN protocol=udp comment="Redirect DNS UDP to router"
add action=redirect chain=dstnat dst-address-type=!local dst-port=123 in-interface-list=LAN protocol=udp comment="Redirect NTP UDP to router"
```

`ipsec-policy=out,none` в masquerade WAN — чтобы не маскарадить трафик, уже уходящий в IPsec. Redirect перехватывает запросы клиентов к внешним 53 и 123 портам и отправляет их на роутер.

---

## 20. MSS-clamp

По VPN туннелю MTU обычно меньше, и большие TCP-сегменты начинают фрагментироваться или рваться. В mangle для трафика через `wireguard1` ставится change-mss для TCP с `new-mss=1380` — тогда соединения не упираются в лимит и работают стабильнее.

```routeros
/ip firewall mangle
add action=change-mss chain=forward new-mss=1380 out-interface=wireguard1 protocol=tcp tcp-flags=syn tcp-mss=1381-65535
```

Правило срабатывает только для SYN с MSS больше 1380 — подменяем на 1380, чтобы по туннелю не уходили слишком большие сегменты.

---

## 21. Отключение ненужных service-port

В `/ip firewall service-port` отключены ftp, tftp, h323, sip, pptp и прочее, чем не пользуемся. Меньше открытых портов — меньше поверхность для случайных сканеров и ботов.

```routeros
/ip firewall service-port
set ftp disabled=yes
set tftp disabled=yes
set h323 disabled=yes
set sip disabled=yes
set pptp disabled=yes
```

---

## 22. Ограничение сервисов управления

SSH и Winbox разрешены только с подсети `192.168.10.0/24`. Telnet, www, api, api-ssl, ftp отключены. Для домашнего роутера этого обычно достаточно: с улицы до управления не добраться, изнутри сети — всё под рукой.

```routeros
/ip service
set ssh address=192.168.10.0/24
set winbox address=192.168.10.0/24
set telnet disabled=yes
set www disabled=yes
set api disabled=yes
set api-ssl disabled=yes
set ftp disabled=yes
```

Подставьте свою LAN-подсеть в `address`; с других адресов SSH и Winbox будут недоступны.

---

## 23. NTP, логирование и системные параметры

Часовой пояс — `Europe/Moscow`, identity роутера задаётся своим именем (например `home-ax3`), чтобы в логах и уведомлениях было понятно, какое устройство пишет. Логирование включено по нужным topic’ам. NTP client — со своими серверами (например российские NTP-пулы), NTP server на роутере включён: он и сам синхронизируется, и раздаёт время клиентам в LAN. При желании можно настроить светодиоды (например привязка к интерфейсам в `/system leds`) — в [статье Gregory Gost](https://gregory-gost.ru/mikrotik-perehodim-na-routeros-7-i-wi-fi-6-802-11ax-nastroika-hap-ax3/) есть пример.

Конкретные команды:

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
add address=0.ru.pool.ntp.org
add address=1.ru.pool.ntp.org
```

Серверы NTP — пример (российская зона pool.ntp.org); подставьте свои. Логирование по темам, например account и critical: `/system logging add topics=account` и `topics=critical`. Обновление времени через облако MikroTik можно отключить: `/ip cloud set update-time=no`.

---

## 24. Скрипты (по данным из export)

Ручное обслуживание роутера быстро надоедает: проверять обновления, смотреть, жив ли NAS, чистить старые бэкапы. В конфиге заведены несколько скриптов, которые висят на scheduler и делают это сами: бэкапы на USB, проверка новой версии RouterOS с уведомлением в Telegram, пинг хоста с алертом при недоступности, сбор IP для YouTube из DNS-кэша и импорт списков подсетей, плюс выгрузка логов (например вход/выход пользователей) в Telegram. Ниже — тела скриптов в виде кода. Вместо секретов (токен бота, chat ID, пароли) стоят плейсхолдеры: подставьте свои значения перед использованием.

### Back_up_1

Создаёт бинарный backup и текстовый export в `usb1-part1/backup/`. Запускается из scheduler Backup.

```routeros
:local currentTime [/system clock get time]
:local currentDate [/system clock get date]
:local backupFile ("usb1-part1/backup/backup-" . $currentDate . "-" . $currentTime . ".backup")
:local backupTXT ("usb1-part1/backup/backup-" . $currentDate . "-" . $currentTime . ".txt")
/system backup save name=$backupFile
/export show-sensitive file=$backupTXT
```

### Backup_2

Удаляет файлы в `usb1-part1/backup/` старше 30 дней. Запускается сразу после Back_up_1.

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

Проверяет наличие новой версии RouterOS и при наличии отправляет уведомление в Telegram. **Замените `YOUR_BOT_TOKEN` и `YOUR_CHAT_ID` на свои.**

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

Проверяет доступность хоста пингом; при отсутствии ответов шлёт alert в Telegram. **Замените `YOUR_BOT_TOKEN`, `YOUR_CHAT_ID` и при необходимости IP хоста.**

```routeros
# IP проверяемого хоста (например NAS или сервер в LAN)
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

Собирает IP YouTube из DNS-кэша и добавляет их в address-list `youtube_dns_ips` (timeout 2d). Секретов нет.

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

Скачивает список подсетей YouTube с iplist.opencck.org и импортирует в RouterOS. Секретов нет.

```routeros
/tool fetch url="https://iplist.opencck.org/?format=mikrotik&site=youtube.com&data=cidr4" mode=https dst-path=iplist_v4_0cidr4.rsc
:delay 5s
:log info "Downloaded iplist_v4_0cidr4.rsc youtube.com"

/import file-name=iplist_v4_0cidr4.rsc
:delay 10s
:log info "New iplist_v4_0cidr4 added youtube.com"
```

### Log_allert

Выбирает новые записи логов по маске (например вход/выход), при необходимости исключает по подстроке, формирует текст в `MSG` и вызывает TG_ME. Подставьте свои фильтры в `IncludeMessages` и `ExcludeMessages`.

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

Отправляет глобальную переменную `MSG` в Telegram. **Замените `YOUR_CHAT_ID` и `YOUR_BOT_TOKEN` на свои.** Вызывается из Telegram, check-host-and-alert, Log_allert.

```routeros
:local ID "YOUR_CHAT_ID"
:local TKN "YOUR_BOT_TOKEN"
:global MSG

/tool fetch keep-result=no url=("https://api.telegram.org/bot" . $TKN . "/sendMessage?chat_id=" . $ID . "&text=" . [/system identity get name] . ": " . $MSG)
```

---

## 25. Scheduler

- **Backup** — каждые 5 дней в 00:00:00: Back_up_1, затем Backup_2.
- **Telegram** — ежедневно в 16:00: скрипт Telegram.
- **check-host** — каждый час: check-host-and-alert.
- **Log_allert_daily** — ежедневно в 22:00: Log_allert.

---

## 26. Безопасность и практические замечания

Уже хорошо: сервисы ограничены, firewall input не открыт наружу, DoH, DDoS, backup и очистка, принудительный DNS/NTP на роутер, разделение WAN/VPN/LAN через interface list.

Стоит помнить: IoT без отдельного VLAN; в скриптах Telegram в export попадают токены и chat ID — полный `show-sensitive` нельзя публиковать. Для следующей итерации можно рассмотреть: VLAN для IoT, отдельный guest SSID, вынос секретов из script source, переименование WAN-порта в `WAN-Eth1`.

---

## 27. Порядок настройки вручную

Если собирать конфиг вручную с нуля, удобно идти так: переименовать интерфейсы → создать LAN-Bridge и добавить порты → interface list (LAN, WAN, VPN) → Wi‑Fi security, channel, configuration → включить wifi1/wifi2 → при необходимости IoT SSID → IP на bridge → DHCP pool и server → DHCP client на WAN → DNS и DoH, bootstrap для AdGuard → WireGuard → routing-table to_wg → address-list для AI/YouTube → mangle → BGP и фильтры → filter, raw, nat → service-port и `/ip service` → NTP, identity, логи → скрипты и scheduler. В конце — `export show-sensitive` и сохранение в архив, чтобы не потерять наработки.

---

## 29. Сравнение с hAP ac и что даёт переход на ax3

Резонный вопрос: стоит ли менять старый hAP ac на ax3, или это «просто ещё один роутер». На практике разница ощутимая. На Gregory Gost проводили сравнительные тесты: тот же сценарий — iPerf3 (60 потоков, 20 секунд, TCP) и передача файла 20 ГБ по SCP — сначала на hAP ac (RouterOS 6.49), потом на hAP ax3 (RouterOS 7.15). Результаты такие:

| Направление              | hAP ac          | hAP ax3         | Разница              |
|--------------------------|-----------------|-----------------|----------------------|
| Client → Server (sender) | 434 Mbit/s      | 614 Mbit/s      | ~29% в пользу ax3    |
| Client → Server (receiver) | 378 Mbit/s    | 595 Mbit/s      | ~36% в пользу ax3    |
| Server → Client (sender) | 340 Mbit/s      | 522 Mbit/s      | ~35% в пользу ax3    |
| Server → Client (receiver) | 335 Mbit/s    | 493 Mbit/s      | ~32% в пользу ax3    |
| Скачивание файла 20 ГБ   | 27 MB/s         | 48 MB/s         | ~44% в пользу ax3    |
| Загрузка файла 20 ГБ     | 47 MB/s         | 35 MB/s         | в этом тесте выше ac |

В среднем по Wi‑Fi прирост 30–45%: и скорость выше, и картина стабильнее. На 5 ГГц ax3 утилизирует канал заметно лучше; при линке провайдера до 500 Mbit/s по Wi‑Fi можно по-настоящему его использовать. Детальные замеры, графики и пошаговую настройку с нуля смотрите в [статье Gregory Gost про hAP ax3 и RouterOS 7](https://gregory-gost.ru/mikrotik-perehodim-na-routeros-7-i-wi-fi-6-802-11ax-nastroika-hap-ax3/) (раздел «Сравнительное тестирование»).

Если нужна именно точка доступа без лишних портов — можно присмотреться к **cAP ax**: характеристики близкие, несколько таких устройств можно объединить через CAPsMAN и сделать бесшовный Wi‑Fi по квартире или офису.

---

## Итог

В итоге получается не «коробочка с Wi‑Fi», а полноценная RouterOS-конфигурация под одну крышу: Wi‑Fi 6 с отдельным IoT SSID и роумингом между 2.4 и 5 ГГц, DoH и принудительный redirect DNS/NTP, WireGuard и L2TP/IPsec, split-routing для AI и YouTube, BGP с антифильтром, firewall, DDoS-защита, резервные копии на USB, scheduler и оповещения в Telegram. Всё это реально собрать в одном устройстве, если разложить конфиг по слоям и не превращать его в свалку правил. Статья получилась длинной именно потому, что хотелось не просто перечислить пункты, а объяснить, зачем каждый кусок и как он связан с остальным. Для пошаговой настройки «с нуля», сброса, выбора каналов 5 ГГц и живых бенчмарков очень рекомендую [подробную статью по hAP ax3 и RouterOS 7 на Gregory Gost](https://gregory-gost.ru/mikrotik-perehodim-na-routeros-7-i-wi-fi-6-802-11ax-nastroika-hap-ax3/) — там и скриншоты, и консольные команды, и тесты в цифрах. Удачной настройки.
