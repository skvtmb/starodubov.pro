---
title: "Fintech Compliance: My Experience with Regulations"
date: 2025-01-11T00:00:00+03:00
draft: false
summary: "How I worked through Bank of Russia requirements, GOST standards and PCI DSS, and what came out of it."
categories: ["Fintech", "Compliance"]
tags: ["compliance", "fintech", "information-security", "regulations", "bank-of-russia", "pci-dss", "152-fz", "gost-57580"]
---

# Fintech compliance: my experience with regulations

When I joined fintech, the first thing I had to figure out was which requirements actually apply to us. Turned out there are quite a few, and almost each one needs its own approach.

Below — the regulatory requirements I actually worked with, and how my compliance system came together. Personal experience, not an official guide.

## Where I started

The company already had a security foundation, but fragmented. Something done here, something patched there. No system.

First thing I did was sit down and write all applicable requirements into one list. That's when it got interesting.

## Bank of Russia regulations

The Bank of Russia is the main regulator for financial organizations. The requirements are tough, but once you read them carefully, the logic is there.

### Regulation No. 683-P

The key one on information protection in banking. Goal: stop unauthorized money transfers.

Main requirements:
- information protection system
- access control to banking systems
- monitoring and incident response
- regular audits and checks

The requirements are detailed, but in practice every measure finds use.

### Regulation No. 787-P

Information protection in the Central Bank's payment system. Focus on payment data and process continuity.

### Regulation No. 821-P

The order of information protection for money transfers. Detailed steps for every stage of payment processing.

While implementing this I sat closely with the developers — a lot of it has to go into the architecture, not be bolted on later.

### STO BR BFBO-1.8-2024

Standard on security for remote identification and authentication. Applies to online banking and any remote services.

The emphasis is on fraud protection during customer identification.

### STO BR IBS

Comprehensive standard on banking information security:
- security risk management
- information protection at all levels
- incident management
- secure development

This isn't a checklist anymore, it's a whole system. You build processes, set up monitoring, train people.

## GOST R 57580.1-2017: basic protection measures

The standard "Financial Operations Security. Information Protection of Financial Organizations" defines the basic set of organizational and technical measures.

### Protection levels

The standard sets several protection levels with different requirements. You first need to figure out which level applies to your company.

For that you analyze: data volume, system criticality, risks. The analysis isn't quick, but without it you can't move at all.

### Organizational and technical measures

The standard describes a connected system of requirements.

**Organizational measures:**
- assigning owners
- policies and procedures
- staff training
- control and monitoring

**Technical measures:**
- information protection tools
- access control
- monitoring
- backups

Measures have to work together. Only technical or only organizational won't cover anything.

### Choosing protection measures

You don't have to implement everything at once. Assess risks first, then pick adequate measures. That way you don't overspend, and the required protection level still holds.

### Implementation completeness

A measure has to be finished. A policy written for the inspector doesn't protect anything. Better to do less, properly.

### Protection across the lifecycle

Protection is needed everywhere: from design to decommissioning.

In practice that means close work with development: SSDLC, code review, security testing.

The hardest part is mindset. Developers are used to thinking about features, not security. Over time it becomes part of the team culture.

## PCI DSS: working with cards

International standard for anyone processing payment cards. Strict but reasonable:

- **perimeter protection** — firewalls, network segmentation
- **data protection** — encryption, storage limits
- **access management** — tight access control
- **monitoring** — tracking actions on card data
- **testing** — regular vulnerability checks
- **policies** — documented processes

The most painful part is limiting data storage. You can't keep full card numbers and CVVs longer than needed. I had to rework part of the system.

After that it gets calmer. Data is in place, monitoring is wired up, the system holds together.

## 152-FZ: personal data

The personal data law applies to anyone processing PII. In fintech it bites especially hard, because the customer data is financial.

Main requirements:
- consent for processing
- security guarantees
- regulator notification
- data subject rights

Requirements themselves are basic, but you have to actually do them. Real data protection, not paperwork for the inspector.

## How I built the compliance system

Once I understood the requirements, I moved to practical work. Didn't try to do everything at once, made a plan first.

### Stage 1: audit

Audited the current state: what exists, what actually works, what's only on paper. Took about a month.

Turned out some requirements were met, but not systematically. A measure for one requirement wasn't reused for another. Needed unification.

### Stage 2: prioritization

Set priorities:
- **critical** — can stop the business or trigger fines
- **high** — hits reputation and customer trust
- **medium and low** — picked up on the side

### Stage 3: implementation

Rolled things out gradually. First the basic measures that close several requirements at once. Then the specific ones.

Rule: no checkbox compliance. Each measure has to actually work.

### Stage 4: training

The most important part is training people. Without understanding "why", the system doesn't hold.

I trained different groups differently: developers, operators, management. Each one needs its own language.

## Result

Six months in there was a working compliance system. Not perfect, but alive:
- critical requirements covered
- processes configured
- people understand what they do and why

The main thing: it's not formal. Every measure has a practical use. You can see the effect in numbers: fewer incidents, clean audits.

## Key takeaways

**Don't be afraid of regulations.**  
Requirements look scary, but the logic is there. Each one solves a real problem.

**A systematic approach matters.**  
You can't close requirements one by one. A single measure often closes several.

**Practice beats theory.**  
You can write a mountain of documents, but if they don't work, it's wasted time. Better less, properly.

**Communication matters.**  
Explain the "why". Once people see the goal, they execute better.

**Compliance is a process.**  
Not a one-off project. You have to keep monitoring, improving, adapting.

## Conclusion

Regulations keep changing. You have to track changes and adapt the system.

If you're just starting with fintech compliance: read the requirements, run an audit, set priorities. Move step by step.

---

*In the next article I'll share practical cases of implementing security standards.*
