---
title: "Anycubic Kobra 3: a 3D printer that turned out more useful than I thought"
date: 2025-02-11T00:00:00+03:00
draft: false
summary: "Bought a 3D printer just to try it. Turned out very useful. Birthday lizards, filament, a broken sensor, a 300-ruble fix."
categories: ["Technology"]
tags: ["3d-printing", "anycubic", "kobra-3", "filament", "repair", "thermistor", "ntc", "review"]
cover:
  image: "/images/anycubic-kobra-3/kobra3.jpg"
  alt: "Anycubic Kobra 3 — 3D printer"
  caption: "Anycubic Kobra 3 — fast and useful for everyday use (image: [store.anycubic.com](https://store.anycubic.com/products/anycubic-kobra-3))"
---

[![Anycubic Kobra 3](/images/anycubic-kobra-3/kobra3.jpg "Anycubic Kobra 3")](https://store.anycubic.com/products/anycubic-kobra-3)

> Image of Anycubic Kobra 3 — [store.anycubic.com](https://store.anycubic.com/products/anycubic-kobra-3).

I bought the Anycubic Kobra 3 just to try it. See how useful the thing actually is. Turned out, very useful. I didn't expect to print this much.

For my kid's birthday I printed a pile of plastic lizards. The kids loved them, grabbed them all in a minute. Tiny thing, lots of joy.

## Where the money goes

Then I noticed: like in that meme, money just disappears somewhere. Turns out it all goes on filament. The printer runs, you print constantly, spools run out one after another. So if you're thinking "bought a printer, done" — get ready to keep ordering plastic.

## Which filament for what

Quick rundown of what's good for what:

### PLA
* **Temperature**: 190–220 °C  
* **Use for**: toys, gifts, organizers, various small things  
* **Pros**: prints easily, no smell, eco-friendly  
* **Cons**: deforms in heat and sun, brittle  

### PETG
* **Temperature**: 230–250 °C  
* **Use for**: holders, mounts, things that need to be sturdier  
* **Pros**: strong, not afraid of moisture  
* **Cons**: harder to tune  

### ABS
* **Temperature**: 230–250 °C  
* **Use for**: enclosures, auto parts, etc.  
* **Pros**: strong, cheap  
* **Cons**: smells when printing, needs enclosed chamber  

### TPU
* **Temperature**: 220–240 °C  
* **Use for**: cases, anything flexible and soft  
* **Pros**: bends, doesn't wear  
* **Cons**: need to print slowly  

### ASA
* **Temperature**: 240–260 °C  
* **Use for**: outdoor items, things in the sun  
* **Pros**: withstands weather and UV  
* **Cons**: like ABS — smell and conditions  

If you're just starting, take PLA and PETG. Least hassle.

## The bed thermistor died

After about 400 hours of printing, the bed temperature sensor gave up. Printer threw **"Hotbed NTC abnormal"** (code 10123).

### What the sensor is

It's an **NTC 100k thermistor** (type B3950). Standard part on almost any FDM printer's bed, Kobra 3 included.

![NTC 100k thermistor for 3D printer heated bed](/images/anycubic-kobra-3/ntc-thermistor.jpg "NTC 100k thermistor — replacement for Anycubic Kobra 3 bed sensor")

*Similar sensor (source: [Prusa3D](https://www.prusa3d.com/product/thermistor-ntc-100k-115-mm/))*

### How I fixed it

Ordered one off Ozon for 300 rubles, arrived fast. Swap took about 15 minutes: unscrew the bed, replace the sensor, screw it back. Printing again.

If you hit the same thing, search for "NTC 100k B3950 thermistor for 3D printer." Just check that the connector fits your board.

## Bottom line

Kobra 3 is genuinely useful around the house. The real cost is filament, not the printer. Even the sensor failure was 300 rubles and 15 minutes. Worth keeping a spare thermistor around.
