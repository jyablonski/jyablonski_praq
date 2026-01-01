# Cross-Publisher Cheater Intelligence Registry

A product concept for shared anti-cheat infrastructure across the gaming industry.

______________________________________________________________________

## Executive Summary

The gaming industry lacks coordinated infrastructure for sharing cheater intelligence across publishers. Each company maintains siloed ban lists, allowing bad actors to simply migrate to new titles after detection. This document outlines a cross-publisher registry that would enable shared identification of cheaters, raising the cost of cheating and improving the multiplayer experience industry-wide.

The most viable path to market is through existing anti-cheat providers (Easy Anti-Cheat, BattlEye) who already have contractual relationships with hundreds of publishers and detection infrastructure running on user machines.

______________________________________________________________________

## The Problem

**Current State**

- Every publisher maintains independent ban lists with no data sharing
- Cheaters banned from one game face zero consequences in others
- Publishers repeatedly invest in detecting the same bad actors
- 95% of cheaters are unsophisticated and exploit this fragmentation

**Impact**

- Degraded multiplayer experience for legitimate players
- Increased anti-cheat costs across the industry
- No cumulative consequence for repeat offenders
- Cheaters treat bans as minor inconveniences rather than meaningful penalties

______________________________________________________________________

## Proposed Solution

### Core Architecture

A centralized registry operated by a trusted third party (ideally an existing anti-cheat provider) that aggregates cheater identity data from participating publishers and distributes risk signals back to the ecosystem.

### Basic Flow

1. Publisher integrates with registry (via existing anti-cheat SDK)
1. Anti-cheat detects cheating locally or server-side
1. Publisher reports flagged identity to central registry with metadata:
   - Identity cluster (hashed email, hardware fingerprint, phone if available)
   - Cheat type detected
   - Confidence level
   - Detection methodology tier
1. Registry stores record and updates identity graph
1. Other publishers query registry at key moments:
   - Account creation
   - Matchmaking queue entry
   - Ranked/competitive mode access
1. Each publisher decides independently how to act on returned risk signals

______________________________________________________________________

## Identity Resolution

The core technical challenge is linking identities across games when cheaters use different emails and attempt hardware spoofing.

### Layered Identity Graph

Rather than storing discrete identifiers, the system builds identity clusters linking related signals:

| Layer | Identifier Type | Evasion Difficulty | Notes |
| ---------- | ------------------------------------------- | ------------------ | --------------------------------- |
| Email | Account email address | Trivial | Burner emails are free |
| Hardware | CPU, GPU, disk serials, BIOS ID, RAM config | Moderate | Spoofing possible but error-prone |
| Phone | Verified phone number | Moderate-High | Requires new SIM or VOIP |
| Behavioral | Mouse movement, timing patterns, play style | High | Difficult to consciously mask |

### Identity Matching Logic

When a new account appears, the system checks each layer:

- **No matches**: Clean account, no flag
- **Single layer match** (e.g., same HWID): High probability same person, flag for review
- **Multiple layer matches**: Near-certain same person, propagate flags
- **Phone match**: Strong link to prior identity

The more layers that match existing flagged clusters, the higher confidence that this is a returning cheater.

### Hardware Fingerprinting Depth

Beyond simple HWID, comprehensive fingerprinting can include:

- CPU serial number
- GPU identifier
- Disk serial numbers
- RAM configuration
- Monitor EDID
- USB device history
- BIOS identifiers

Sophisticated cheaters can spoof individual components, but consistently spoofing all identifiers without errors is difficult. A single slip links their identities permanently.

______________________________________________________________________

## Classification Tiers

Not all detections carry equal weight. A tiered classification system allows consuming publishers to set appropriate thresholds.

| Tier | Definition | Example Sources | Recommended Action |
| ---------- | --------------------------------------------------------------------------------- | ----------------------------------------------------- | ----------------------------------------- |
| Verified | Detection process audited, documented low false-positive rate, legally defensible | Valve VAC, Riot Vanguard, audited EAC implementations | Act on single flag |
| Standard | Reputable detection methods, no formal audit | Mid-size studio using EAC/BattlEye defaults | Review manually or require 2+ flags |
| Unverified | Self-reported, no process validation | Indie developer with custom detection | Informational only, require corroboration |

### Confidence Scoring Heuristics

- 1 unverified flag: Noise, likely ignore
- 1 verified flag: Actionable
- 3+ standard flags across different publishers: Treat as verified
- Pattern of flags followed by new accounts on same hardware: Escalate confidence
- Recent flags weighted more heavily than old flags

______________________________________________________________________

## Publisher Integration

### Consuming Risk Signals

Publishers maintain full autonomy over how to act on registry data. Options include:

- **Hard block**: Deny account creation or game access
- **Soft restriction**: Allow play but exclude from ranked/competitive modes
- **Shadowban**: Allow play but match only with other flagged accounts
- **Monitoring**: Allow normal play but flag for enhanced server-side detection
- **Ignore**: Use registry data only for analytics

### Configuration Interface

Publishers would access a dashboard to:

- Set threshold policies (e.g., "block on any Verified flag, review Standard flags manually")
- Query specific accounts
- View flagged user details and flag history
- Configure integration points (account creation, matchmaking, etc.)
- Export analytics on flag volume and types

______________________________________________________________________

## Data and Privacy Considerations

### Regulatory Landscape

- **GDPR** (EU): Requires lawful basis for processing, data subject rights, cross-border transfer compliance
- **CCPA** (California): Consumer rights to access and deletion
- **Regional variations**: Additional requirements in specific jurisdictions

### Recommended Legal Structure

The cleanest approach is **contractual privity through publishers**:

1. Registry never collects data directly from users
1. Publishers share data under their existing Terms of Service (which typically grant broad rights for anti-cheat purposes)
1. Registry operates as a data processor, not controller
1. Users' legal relationship remains with the original publisher

This structure requires:

- Publishers to have ToS that support data sharing for anti-cheat
- Clear data processing agreements between registry and each publisher
- Defensible position that registry is not an independent data controller

### Risk Mitigation

- Store hashed identifiers where possible (contested but defensible)
- Implement appeals process to demonstrate good faith
- Define data retention policies with automatic expiration
- Maintain audit logs for all flag events
- Establish clear liability and indemnification structure with publishers

______________________________________________________________________

## Appeals and Corrections

### The Challenge

Incorrect flags have real consequences—users lose access to games they paid for. Without a credible appeals process, the system faces:

- Defamation exposure
- Tortious interference claims
- Consumer protection complaints
- Reputational damage

### Proposed Process

1. User submits appeal through original publisher
1. Publisher reviews detection evidence
1. If publisher overturns, they notify registry to update/remove flag
1. Registry propagates correction to other publishers who acted on the flag

### Safeguards

- Multiple independent flags from different publishers make false-positive claims less credible
- Audit trail documents detection methodology and evidence
- Time-limited flags that expire without corroboration
- Statistical monitoring for publishers with anomalously high flag rates

______________________________________________________________________

## Path to Market

### Why Anti-Cheat Providers Are Best Positioned

Easy Anti-Cheat (Epic) and BattlEye already have:

- Contracts with hundreds of publishers
- Detection infrastructure running on user machines
- Legal cover through existing agreements
- Cross-game visibility within their client base
- Established trust relationships

The leap from "per-game detection" to "cross-game intelligence sharing" is primarily a product decision, not a technical or legal one.

### Strategic Value

For anti-cheat providers:

- **Stickiness**: Publishers dependent on shared intelligence layer cannot easily switch providers
- **Differentiation**: "Use our anti-cheat and access cross-game intelligence" is a compelling sales pitch
- **Premium tier opportunity**: Offer as upsell to existing customers

For publishers:

- **Reduced detection burden**: Leverage industry-wide intelligence instead of starting from scratch
- **Improved player experience**: Catch repeat offenders before they impact the game
- **Cost efficiency**: Shared infrastructure vs. independent investment

### Alternative Paths

- **Platform-level implementation**: Valve (Steam), Microsoft (Xbox), Sony (PlayStation) could implement within their ecosystems without third-party coordination
- **Regulatory mandate**: Governments could require identity verification or ban portability (more likely in EU/Asia than US)
- **Industry consortium**: Publishers voluntarily coordinate, though competitive dynamics make this difficult

______________________________________________________________________

## Limitations and Scope

### What This Solves

- High-volume, unsophisticated cheaters who rely on ecosystem fragmentation
- Repeat offenders who cycle through games after bans
- Basic evasion attempts (new emails, simple hardware swaps)

### What This Doesn't Solve

- Sophisticated cheaters using dedicated hardware, fresh VMs, new phone numbers per account
- Commercial cheat operations (require legal action, infiltration of cheat dev communities)
- First-time cheaters with no prior flags
- Cheating in games from non-participating publishers

### Acceptable Tradeoff

The 95% of cheaters who are lazy or unsophisticated cause the most damage to player experience. Catching them represents the highest-value opportunity. Sophisticated evasion will always be possible, but making it expensive and unreliable significantly raises the barrier.

______________________________________________________________________

## Summary

The gaming industry will likely converge on shared anti-cheat intelligence within the next 10-20 years. The current fragmented approach is obviously inefficient, and coordination problems tend to resolve through either consolidation or standardization.

The most probable path is not a purpose-built registry, but rather existing anti-cheat providers (EAC, BattlEye) building cross-game reputation scoring into their offerings—either as a differentiator or in response to publisher demand.

The core components are straightforward:

- Multi-layer identity graphs
- Tiered classification with confidence scoring
- Publisher-controlled consumption of risk signals
- Appeals process and data governance

The barriers are organizational and legal, not technical. Whoever moves first captures significant strategic value through increased stickiness and market differentiation.
