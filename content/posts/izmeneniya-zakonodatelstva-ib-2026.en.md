---
title: "Changes in Russian information security legislation in 2026"
slug: "izmeneniya-zakonodatelstva-ib-2026"
date: 2026-02-14T00:00:00+03:00
draft: false
summary: "What’s changing in 2026: FSTEC Order No.117 replacing No.17, CII (critical information infrastructure), personal data, licensing. Why costs will rise and how to get ready."
categories: ["Information Security", "Legislation"]
tags: ["information-security", "FSTEC", "order-117", "CII", "personal-data", "legislation", "2026", "compliance", "russia"]
cover:
  image: "/images/izmeneniya-2026/cover.jpg"
  alt: "Cybersecurity and data protection"
  caption: "Regulatory changes in information security (photo: [FLY:D](https://unsplash.com/photos/photo-1563013544-824ae1b704d3) / Unsplash)"
---

## Changes in Russian information security legislation in 2026

2026 rewrites the rules for information protection in Russia. Below is a summary of changes from January, a side-by-side look at FSTEC Order No.117 versus No.17, and what it means for organizations in practice.

*Note: This overview covers Russian federal regulations. Acronyms used: CII — Critical Information Infrastructure (КИИ); FSTEC — Federal Service for Technical and Export Control; GIS — State Information System (ГИС); PD — Personal Data (ПДн).*

---

### Overview of regulatory changes in January 2026

#### Critical information infrastructure (CII)

**Sector-specific categorization rules for CII objects in nuclear energy**

On January 16, 2026, the Russian Government adopted Decree No.4 approving sector-specific rules for categorizing CII objects in the nuclear energy sector.

Key provisions:

- Representatives of the State Corporation "Rosatom" may be included in the categorization commission.
- Certain significance indicators from the list approved by Decree No.127 of 08.02.2018 (positions 4, 10, 10¹–10⁷, 14) do not apply to nuclear sector CII objects.
- Additional input data include: technical and design documentation, service agreements, operation and maintenance documents, scenarios of possible cyberattacks and incidents, and information from employee questionnaires.
- Methods for calculating indicators: expert assessment, analogy method, attack and incident modeling, and risk-based calculation.

The calculation takes into account physical effects of accidents (fires, toxic releases), defense procurement parameters, and other factors.

**Sector-specific categorization rules for CII objects in banking and financial markets**

On February 6, 2026, the Russian Government adopted Decree No.92 "On approval of sector-specific rules for categorizing CII objects in the banking sector and other sectors of the financial market." The document enters into force on February 15, 2026.

**What it is and why it matters**

Short version: banks, insurers, pension funds, exchanges, payment systems and other financial market participants have to find their information systems that count as critical infrastructure and assign significance categories. The rules used to be general across sectors. Now the financial sector has its own — what counts as significant and how to measure it.

**Who is covered**

CII subjects in the banking and financial market sector include:

- Central Bank of Russia;
- credit institutions (banks);
- non-credit financial organizations (insurance, microfinance, pension funds, etc.);
- national payment system participants;
- payment infrastructure service operators;
- digital ruble platform operator;
- credit bureaus;
- professional financial market service providers;
- government bodies and their subordinate organizations performing banking and financial market functions.

**How to tell whether a system is a CII object**

An organization inventories its information systems and checks them against sector-specific lists of typical CII objects. On the list — categorize it. Not on the list but a failure could cause serious damage — categorize it anyway and propose adding it to the list.

**Which systems are assessed and by which indicators**

The document spells out which system types map to which significance indicators. For example:

- **Central Bank money transfer systems** — indicators 6 and 10 (volume of operations, functional significance).
- **Remote banking systems** (internet banking, mobile banking) — indicator 10.
- **Automated banking systems** — indicator 10.
- **Payment processing systems** — indicator 10.
- **Clearing systems** (settlements between participants) — indicator 10¹ (volume of executed obligations in rubles).
- **Securities custody and accounting systems** — indicator 10² (number of securities).
- **Pension fund systems** (pension savings and reserves accounting) — indicator 10³.
- **Insurance systems** (policy, payment, loss accounting) — indicator 10⁴.
- **Information exchange systems for e-payment operations** — indicator 10⁵.
- **Microfinance organization systems** (microloan accounting) — indicator 10⁶.
- **Credit bureaus** — indicator 10⁷ (number of credit histories).
- **Data centers** providing resources for significant CII objects (except Central Bank, banks, etc.) — indicators 6 and 7.

For each system category, the document provides formulas for calculating indicator values — based on transaction volume, assets, number of clients, etc.

**Commission and reporting**

The organization establishes a categorization commission, conducts the assessment, and assigns categories. Information is submitted to FSTEC. Additionally:

- **To the Ministry of Finance** — government bodies, state unitary enterprises, state institutions, and organizations that are not banks, payment systems, etc.
- **To the Bank of Russia** — credit institutions, non-credit financial organizations, payment system participants, professional market participants.

Annually, by the 10th business day of the year, an updated list of significant CII objects and a decision on category revision (or no revision) must be submitted.

**Practical implications**

For banks and financial organizations the document provides an algorithm: which systems to treat as critical, how to rank them, where to report. From there protection measures under Federal Law 187-FZ and FSTEC Order No.117 follow.

**Document links**

- [Government Decree No.92 of 06.02.2026](https://normativ.kontur.ru/document?moduleId=1&documentId=504397) — full text on Kontur.Normativ
- [Official publication](http://publication.pravo.gov.ru/document/0001202602070010) — Official internet portal of legal information (published 07.02.2026)

#### Personal Data

**Biometrics in access control systems**

On January 24, draft amendments to Federal Law No.572-FZ of 29.12.2022 on the use of biometric personal data were published. The changes concern physical and logical access control systems (ACS):

- Expanded possibility to use own accredited systems with vectors from the unified biometric system — not only for employees but also for visitors, affiliated persons, and subsidiaries.
- Differentiated requirements for CII objects by significance category: in controlled zones of categories 1 and 2, accredited government systems and own systems (with accreditation) are permitted; in category 3 and uncategorized objects — systems of other accredited organizations.

**Criminal liability for automated processing of personal data**

On January 27, draft amendments to Article 272.1 of the Criminal Code were published. A new offense appears — "automated processing" of unlawfully obtained personal data. Prosecution becomes possible for the processing itself, regardless of what is done with it next. The target is deepfakes used for fraud and blackmail.

#### Administrative liability in telecommunications

On January 15, draft amendments to the Administrative Offenses Code were published:

- Liability for concluding telecommunications service agreements in unauthorized or non-compliant locations.
- Increased fines under Art. 13.29(4) for legal entities — from 500,000 to 1 million rubles.
- Liability for telecom operators for non-compliance with verification node requirements of the "Antifraud" GIS (including ongoing interaction) — fines for legal entities from 600,000 to 1 million rubles.
- Extended statute of limitations under Art. 13.33 (electronic signature) to 1 year.

The bill may enter into force on September 1, 2026.

#### FSTEC Russia

**Certification of informatization objects**

On January 26, a draft FSTEC order amending the certification procedure (Order No.77 of 29.04.2021) was published. The draft aligns with Order No.117 of 11.04.2025. Key points:

- Requirements extend to information systems of government bodies, state unitary enterprises, and state institutions.
- Periodic control may be conducted by own information protection units (after notifying FSTEC).
- New certification testing methods, including modeling of current threats.
- **Mandatory penetration testing** for GIS and government information systems of protection classes 1 and 2 that have internet connectivity or interact with external systems (with exceptions for systems operating only via VPN or encrypted networks).
- Data center infrastructure for digital transformation of public administration is subject to mandatory certification.
- Security control — by vulnerability analysis and penetration testing per FSTEC methodology of 25.11.2025. A report (protocol) is submitted to FSTEC at least once every 3 years.

**Licensing of development and production of information protection tools**

On January 29, a draft Government decree amending the licensing regulation (Decree No.171 of 03.03.2012) was published:

- Direct prohibition for sole proprietors with foreign citizenship and legal entities whose heads are foreign citizens.
- Reduced required experience for heads to 5 years (previously 7).
- Increased minimum number of engineers: at least 5 for technical protection tools, at least 10 for development and production of software protection tools.
- Mandatory use of predominantly domestically produced equipment and software located in Russia.
- Presence of certified (attested) information system for processing confidential information at the place of activity.
- **Mandatory production control system** per GOST R 56939-2024 "Information protection. Secure software development. General requirements."

**Licensing of technical information protection activities**

On January 29, draft amendments to the TIP licensing regulation (Decree No.79 of 03.02.2012) were published:

- Same restrictions for foreign sole proprietors and legal entities with foreign heads.
- New staffing requirements: for security monitoring — at least 15 engineers (5 with 3+ years experience); for certification testing — at least 9 engineers (3 with 3+ years); for other services — at least 5 engineers with 3+ years experience.
- Mandatory use of predominantly domestic equipment and software in Russia.
- Production quality control system for most types of activities.

---

### FSTEC Order No.117 vs No.17: what’s different

As of March 1, 2026, Order No.17 is out and No.117 is in. This isn’t a cosmetic update — the underlying regulatory logic changes.

#### From checklist to risk-based model

**No.17** set a fixed list of requirements. Categorization and choice of measures came from the system type, not from actual threats and consequences.

**No.117** asks you to build protection from a threat model, risks and operating conditions. Two systems of the same type may need different protection levels depending on what happens during an incident. The regulator looks not only at whether measures are in place, but at how well they’re justified and how effective they are.

#### Terminology and scope

No.117 reworks the terminology. Terms align with Federal Laws 149-FZ, 187-FZ, and subordinate acts. The information security system is now treated as a whole — organizational, software and technical measures together, not separately.

#### Classification and protection levels

**No.17:** the protection class effectively defined an exhaustive set of measures.

**No.117:** levels are derived from damage analysis, current threats and architecture. Information security risks are weighed, not just formal criteria.

#### Threat and attacker model

**No.17:** threat models were often formal and mainly used during design and certification.

**No.117:** the focus is on threats from remote access, supply chains and human factors. The model has to reflect real attack scenarios.

#### Organizational measures

**No.17:** organizational measures often boiled down to a stack of regulations and orders.

**No.117:** the information security policy is a working document with roles, responsibilities, and decision-making procedures. Requirements for staff training and internal control are stronger.

#### Technical and software measures

**No.17:** emphasis on having certified protection tools from a list.

**No.117:** focus on outcome — the ability to prevent and detect incidents. Combined solutions are allowed if you can justify effectiveness. Monitoring and logging matter much more.

#### New focus areas

No.117 calls out separately:

- protection of web applications and APIs;
- protection of remote access (mandatory strong authentication, VPN, configuration control of remote workstations);
- security when working with contractors;
- protection of virtualization and cloud environments;
- IoT, container, and orchestration technologies.

#### Infrastructure and contractors

**No.17** focused on the GIS perimeter. IT infrastructure components outside the perimeter could stay uncertified.

**No.117** extends requirements to the whole IT infrastructure on which GIS run. Contractors must provide certification under the same threat model and class as the customer. That fundamentally changes supply chain requirements.

#### Incident response

**No.117** sharpens the processes for detection, analysis and remediation of incidents. Event correlation and integrity control tools are required.

---

### Why costs will rise

#### Expanded scope

Requirements now apply not only to GIS but also to information systems of government bodies, state unitary enterprises, state institutions and municipal bodies. The definition of GIS itself is broader — any government system where state data is processed.

#### New mandatory measures

- Mandatory penetration testing for GIS of classes 1 and 2 with internet access.
- Remote access protection with configuration control, VPN, antivirus, and additional tools.
- Protection of web applications and APIs.
- Virtualization requirements: certified solutions or overlay protection tools.
- Mandatory certification of data center infrastructure for digital transformation of public administration.

#### Contractors

Contractors have to build certified segments and meet the same requirements as the customer. For many that means new work — consulting, infrastructure upgrades. The pool of suppliers who can pull this off shrinks, and prices go up.

#### Market estimates

By market participants’ estimates, implementing solutions in 2025 could save up to 30%. From 2026, expect:

- 25–30% cost increase from changes in tax and certification regulation;
- higher certification costs under the new requirements;
- rising license and certification prices.

#### Responsibility

No.117 effectively expands management responsibility. Errors in threat assessment can lead to regulatory and financial risks. Responsibility no longer sits only with the information security department.

---

### Other 2026 trends

#### Federal Law 152-FZ (personal data)

- Stricter fines (up to millions of rubles).
- Stronger localization requirements for Russian citizens' personal data.
- New consent and notification rules for data subjects (from September 1, 2025).

#### Federal Law 187-FZ (CII)

- Exclusion of sole proprietors from CII subjects.
- Expanded powers of the Russian Government.
- Requirements for use of domestic software on significant objects.
- Extension of requirements to contractors and suppliers.

#### Antifraud platform and biometrics

- From March 1, 2026 — launch of GIS to combat cyber fraud (Federal Law 41-FZ).
- Microfinance organizations must authenticate borrowers by biometrics when concluding consumer loan agreements in electronic form.

#### Draft law: fines for CII operation violations

Introduction of Art. 13.12.2 of the Administrative Offenses Code is under consideration: fines for individuals 5–10 thousand rubles, for officials 10–50 thousand rubles, for legal entities 100–500 thousand rubles for violation of CII object operation rules.

---

### What to do

1. **Run a legal audit** — line current measures up against No.117 and check whether they’re justified by threats and consequences.
2. **Refresh the threat model** — make sure it covers remote access, supply chains and human factors, with realistic attack scenarios.
3. **Rewrite local regulations** — security policies and procedures need to match the terminology and logic of No.117.
4. **Pin down responsibility** — roles and authority for security, but also for department heads, IT, and top management.
5. **Check incident readiness** — procedures for detection, recording, analysis and decision-making.
6. **Don’t delay** — certifications under No.17 done before March 1, 2026 remain valid. New projects should be planned for No.117 from the start.

---

*Sources: [USSC review January 2026](https://hub.zlonov.ru/laws/reviews/2026-01-USSC-review), [Klerk.Ru on Order 117](https://www.klerk.ru/blogs/fedresurs/678022/), [Anti-Malware.ru on GIS requirements](https://www.anti-malware.ru/analytics/Technology_Analysis/FSTEC-Order-No-117), [Computerra on 2026 IS trends](https://www.computerra.ru/335033/novye-trebovaniya-regulyatorov-i-trendy-zakonodatelstva-v-informatsionnoj-bezopasnosti-2026/), [Lidings on CII changes 2025–2026](https://www.lidings.com/ru/media/legalupdates/cii2025-2026/), [D-Russia on Decree 92](https://d-russia.ru/utverzhdeny-osobennosti-kategorirovaniya-obektov-kii-v-bankovskoy-sfere.html)*
