---
title: "Fintech Compliance: My Experience with Regulations"
date: 2025-01-11T00:00:00+03:00
draft: false
summary: "How I navigated Bank of Russia requirements, GOST standards, and PCI DSS, and what came of it"
categories: ["Fintech", "Compliance"]
tags: ["compliance", "fintech", "information-security", "regulations", "bank-of-russia", "pci-dss", "152-fz", "gost-57580"]
---

# Fintech Compliance: My Experience with Regulations

When I started working in fintech, the first thing I needed to figure out was: which requirements apply to us? It turned out there were quite a few regulations, and each required its own approach.

I'll share the regulatory requirements I worked with and how I built a compliance system. This is personal experience, not an official guide.

## Where I Started

The company already had some security foundations, but fragmented: something implemented here, something covered there. There was no systematic approach.

First, I compiled a list of all applicable requirements. That's where things got interesting.

## Bank of Russia Regulations

The Bank of Russia is the main regulator for financial organizations. The requirements are serious, but once you understand them — they're logical.

### Regulation No. 683-P

The key regulation on information protection in banking. The goal is to prevent unauthorized money transfers.

Main requirements:
- Information protection system
- Access control to banking systems
- Monitoring and incident response
- Regular audits and checks

The requirements are detailed, but in practice each measure finds its application.

### Regulation No. 787-P

Requirements for information protection in the Central Bank's payment system. Focus on protecting payment data and process continuity.

### Regulation No. 821-P

Procedure for information protection in money transfers. Detailed protection at each stage of payment processing.

When implementing, I had to work closely with developers — many requirements are built into the architecture.

### STO BR BFBO-1.8-2024

Standard on security for remote identification and authentication. Relevant for online banking and remote services.

Emphasis on protection against fraud in customer identification.

### STO BR IBS

Comprehensive standard on information security of banking systems:
- Security risk management
- Information protection at all levels
- Incident management
- Secure development

This is a whole system, not just a set of requirements. You need to build processes, configure monitoring, train people.

## GOST R 57580.1-2017: Basic Protection Measures

The standard "Financial Operations Security. Information Protection of Financial Organizations" defines the basic set of organizational and technical measures.

### Protection Levels

The standard defines several protection levels with different requirements. You need to determine the applicable level for your company.

This requires analyzing: data volume, system criticality, risks. It's not quick, but you can't move forward without this analysis.

### Organizational and Technical Measures

The standard describes a system of interconnected requirements.

**Organizational measures:**
- Assigning responsible persons
- Policies and procedures
- Staff training
- Control and monitoring

**Technical measures:**
- Information protection tools
- Access control
- Monitoring
- Backup

Important: measures must work together. You can't implement only technical or only organizational measures.

### Choosing Protection Measures

You don't need to implement everything at once. First assess risks, then choose adequate measures. This avoids excessive investment while maintaining the necessary protection level.

### Implementation Completeness

Measures must be fully implemented. Formally creating a policy doesn't mean you're protected. Better to do less, but well.

### Protection at All Lifecycle Stages

The standard requires protection at all stages: from design to decommissioning.

This means close work with development: implementing secure development practices, code analysis, security testing.

One of the hardest areas — developers are used to focusing on functionality. But gradually security becomes part of the culture.

## PCI DSS: Working with Cards

International standard for those who process payment cards. Requirements are strict but logical:

- **Perimeter protection** — firewalls, network segmentation
- **Data protection** — encryption, storage limits
- **Access management** — strict access control
- **Monitoring** — tracking actions with card data
- **Testing** — regular vulnerability assessments
- **Policies** — documenting processes

The hardest part — limiting data storage. You can't store full card numbers and CVV longer than necessary. I had to rework part of the system.

But when everything works — you feel calmer. Data is protected, monitoring is configured, the system is resilient.

## 152-FZ: Personal Data

The personal data law applies to everyone who processes it. Especially important in fintech — we work with customers' financial data.

Main requirements:
- Consent for processing
- Security assurance
- Regulator notification
- Data subject rights

The requirements are basic, but need to be implemented properly. It's important to actually protect data, not just formally.

## How I Built the Compliance System

After understanding the requirements, I started practical work. I didn't try to cover everything at once — I made a plan.

### Stage 1: Audit

Conducted an audit of the current state: what exists, what works, what's only on paper. This took a month.

Turned out some requirements were met, but not systematically. Measures for one requirement weren't used for another. Unification was needed.

### Stage 2: Prioritization

Defined priorities:
- **Critical** — can lead to business suspension or fines
- **High** — affect reputation and customer trust
- **Medium and low** — on a residual basis

### Stage 3: Implementation

Started implementing gradually. First basic measures that cover multiple requirements. Then specific ones.

Important: don't do it "for the checkbox." Each measure must actually work.

### Stage 4: Training

Most important — training employees. Without understanding "why," the system doesn't work.

Conducted training for different groups: developers, operators, management. Each with its own approach.

## Result

After six months there was a compliance system that actually worked. Not perfect, but functional:
- Critical requirements covered
- Processes configured
- People understand what and why they're doing

The main thing — the system isn't formal. Each measure has practical application. The result is visible: incidents decreased, audits pass successfully.

## Key Takeaways

**Don't fear regulations**  
Requirements seem complex, but they're logical. Each solves a specific problem.

**Systematic approach is critical**  
You can't cover requirements individually. One measure can cover multiple requirements.

**Practice over theory**  
You can write lots of documents, but if they don't work — it's useless. Better less, but quality.

**Communication matters**  
Explain to people "why." When they understand the goal — they perform better.

**Compliance is a process**  
Not a one-time event. Need to constantly monitor, improve, adapt.

## Conclusion

Regulations are constantly updated — need to track changes and adapt the system.

If you're starting to work with fintech compliance: study the requirements, conduct an audit, define priorities. Move gradually.

---

*In the next article I'll share practical cases of implementing security standards.*
