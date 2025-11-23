# Org Chart

Sample Org Chart for a Tech Company

## Overview

StreamFlix is a video streaming platform with 50M subscribers generating $10B annual revenue through subscriptions ($8B) and advertising ($2B). Our engineering organization consists of 6 teams supporting 2 user-facing applications and 8 backend services.

```mermaid
graph TD
    %% Block D - Revenue Streams (Top)
    subgraph D["Revenue Streams"]
        SUB["Subscription Revenue<br/>$8B annually"]
        ADS["Advertising Revenue<br/>$2B annually"]
    end

    %% Block C - User Facing Applications
    subgraph C["User-Facing Applications"]
        WEB["Web Application<br/>(React + Next.js)"]
        MOBILE["Mobile Apps<br/>(iOS + Android)"]
    end

    %% Block B - Backend Services with Ownership
    subgraph B["Backend Services"]
        subgraph B1["Bravo Team Services"]
            AUTH["Authentication Service"]
            USER["User Management Service"]
        end
        subgraph B2["Charlie Team Services"]
            SUB_SVC["Subscription Service"]
            PAYMENT["Payment Processing"]
        end
        subgraph B3["Delta Team Services"]
            CONTENT["Content Management"]
            STREAM["Video Streaming Engine"]
        end
        subgraph B4["Echo Team Services"]
            ADS_SVC["Ad Serving Platform"]
        end
        subgraph B5["Foxtrot Team Services"]
            ANALYTICS["Analytics & Metrics"]
        end
    end

    %% Block A - Teams (Bottom)
    subgraph A["Engineering Teams"]
        ALPHA["Alpha Team<br/>Frontend Platform<br/>Uses: All Services"]
        BRAVO["Bravo Team<br/>User Identity & Auth<br/>Uses: Analytics"]
        CHARLIE["Charlie Team<br/>Subscriptions & Billing<br/>Uses: User Mgmt, Analytics"]
        DELTA["Delta Team<br/>Content & Media<br/>Uses: Auth, Analytics"]
        ECHO["Echo Team<br/>Advertising Platform<br/>Uses: User Mgmt, Content, Analytics"]
        FOXTROT["Foxtrot Team<br/>Data & Analytics<br/>Uses: All Service Data"]
    end

    %% Sequential Links Between Blocks
    A --> B
    B --> C
    C --> D

    %% Styling
    classDef revenueStyle fill:#e1f5fe,stroke:#01579b,stroke-width:3px,color:#000
    classDef appStyle fill:#f3e5f5,stroke:#4a148c,stroke-width:3px,color:#000
    classDef serviceStyle fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px,color:#000
    classDef teamStyle fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000

    class SUB,ADS revenueStyle
    class WEB,MOBILE appStyle
    class AUTH,USER,SUB_SVC,PAYMENT,CONTENT,STREAM,ADS_SVC,ANALYTICS serviceStyle
    class ALPHA,BRAVO,CHARLIE,DELTA,ECHO,FOXTROT teamStyle
```

## Team Overview

## Alpha Team - Frontend Platform

Mission: Deliver exceptional user experiences across all client applications

### Responsibilities

- Web application (React/Next.js) development and maintenance
- Mobile applications (iOS/Android) development and maintenance
- Frontend performance optimization and A/B testing
- User interface consistency and design system implementation
- Client-side analytics and user behavior tracking

### Team Composition

- Team Lead
- 2 Senior Frontend Engineers
- 2 Mobile Engineers
- Product Designer
- Product Manager

### Key Metrics

- User conversion rates
- Application load times
- Mobile app store ratings
- Frontend error rates

---

## Bravo Team - DevOps, Infrastructure & SRE

Mission: Ensure reliable, scalable, and secure infrastructure for all platform services

### Responsibilities

- Infrastructure as Code (Terraform, CloudFormation, Kubernetes)
- CI/CD pipeline management and deployment automation
- Service reliability engineering and incident response
- Infrastructure monitoring, alerting, and observability
- Security infrastructure and compliance tooling
- Cost optimization and resource management
- Database administration and backup strategies
- Network architecture and load balancing

### Team Composition

- Team Lead
- 3 Senior SRE Engineers

### Key Metrics

- Platform uptime (99.99% SLA)
- Deployment success rate
- Mean time to recovery (MTTR)
- Infrastructure cost efficiency
- Security incident response time

### Services Supported

- All teams' infrastructure needs
- Shared monitoring and alerting systems
- Deployment pipelines for all services
- Security scanning and compliance tools

---

## Charlie Team - Subscriptions & Billing

Mission: Drive subscription revenue through reliable billing and payment systems

### Responsibilities

- Subscription service (plan management, billing cycles, upgrades/downgrades)
- Payment processing (credit cards, PayPal, international payments)
- Revenue optimization (pricing experiments, retention campaigns)
- Financial reporting and subscription analytics
- Payment compliance (PCI DSS, international regulations)

### Team Composition

- Team Lead
- 3 Senior Backend Engineers
- Data Engineer
- Product Manager

### Key Metrics

- Monthly recurring revenue (MRR)
- Payment failure rates
- Subscription churn rates
- Revenue per user (ARPU)

---

## Delta Team - Content & Media

Mission: Deliver high-quality content streaming experiences at global scale

### Responsibilities

- Content management system (metadata, catalogs, search)
- Video streaming engine (transcoding, CDN optimization, adaptive bitrate)
- Content recommendation algorithms
- Video quality monitoring and optimization
- Content ingestion and processing pipelines

### Team Composition

- Team Lead
- 3 Senior Backend Engineers
- 2 Data Scientists
- Product Manager

### Key Metrics

- Video start success rates
- Streaming quality scores
- Content discovery engagement
- CDN cache hit rates

---

## Echo Team - Advertising Platform

Mission: Maximize advertising revenue while maintaining user experience quality

### Responsibilities

- Ad serving platform (targeting, bidding, inventory management)
- Ad performance tracking and optimization
- Advertiser dashboard and self-service tools
- Ad quality and content safety filtering
- Revenue optimization and yield management

### Team Composition

- Team Lead: Victoria Singh (Principal Engineer)
- Backend Engineers: Christopher Lee, Natasha Volkov
- Ad Tech Engineer: Benjamin Clark
- Data Scientist: Dr. Maria Gonzalez
- Product Manager: Andrew Mitchell

### Key Metrics

- Ad revenue per user
- Ad completion rates
- Advertiser satisfaction scores
- Ad loading performance

---

## Foxtrot Team - Data & Analytics

Mission: Enable data-driven decisions across all business functions

### Responsibilities

- Analytics and metrics service (data collection, processing, reporting)
- Data pipeline architecture and ETL processes
- Business intelligence dashboards and reporting
- Machine learning platform and model deployment
- Data quality monitoring and governance

### Team Composition

- Team Lead
- 2 Data Engineers
- 2 Analytics Engineer
- ML Platform Engineer
- Product Manager: Michelle Davis

### Key Metrics

- Data pipeline reliability
- Query performance and availability
- Model prediction accuracy
- Business metric reporting SLA

---

## Cross-Team Responsibilities

### On-Call Rotation

Each team maintains 24/7 on-call coverage for their services with escalation procedures to team leads and principal engineers.

### Quarterly Business Reviews

Teams present service performance, business impact metrics, and roadmap alignment to executive leadership.

### Inter-Team Dependencies

- Alpha Team integrates with all backend services
- Foxtrot Team receives data from all other teams
- Security and compliance requirements span all teams

### Shared Infrastructure

- All teams contribute to shared libraries and platform services
- Common deployment pipelines and monitoring standards
- Shared documentation and knowledge base maintenance

---

## Revenue Impact Mapping

### Subscription Revenue ($8B)

- Primary: Charlie Team (billing optimization)
- Secondary: Alpha Team (conversion), Delta Team (content satisfaction)

### Advertising Revenue ($2B)

- Primary: Echo Team (ad platform optimization)
- Secondary: Alpha Team (ad integration), Delta Team (content context), Foxtrot Team (targeting data)

### Cost Optimization

- Infrastructure: Bravo Team (cloud costs, resource efficiency, scaling optimization)
- Operations: Bravo Team (platform reliability, reduced downtime costs), All teams (service reliability)

## Architecture

```mermaid
graph TB
    %% Users and CDN
    subgraph Internet["Internet"]
        USERS["Users<br/>(Web + Mobile)"]
    end

    subgraph CDN["Content Delivery"]
        CF["CloudFront CDN<br/>(Global Edge Locations)"]
        S3_STATIC["S3 Static Assets<br/>(Videos, Images, JS/CSS)"]
    end

    %% Load Balancing and API Gateway
    subgraph LoadBalancing["Load Balancing Layer"]
        ALB["Application Load Balancer<br/>(Multiple AZs)"]
        API_GW["API Gateway<br/>(Rate Limiting, Auth)"]
    end

    %% Application Layer
    subgraph ApplicationLayer["Application Services (Auto Scaling Groups)"]
        subgraph WebServices["Web Services"]
            WEB1["Web App Instance 1<br/>(EC2/ECS)"]
            WEB2["Web App Instance 2<br/>(EC2/ECS)"]
            WEB3["Web App Instance N<br/>(EC2/ECS)"]
        end

        subgraph BackendServices["Backend Microservices"]
            AUTH_SVC["Auth Service<br/>(ECS Fargate)"]
            USER_SVC["User Service<br/>(ECS Fargate)"]
            SUB_SVC["Subscription Service<br/>(ECS Fargate)"]
            CONTENT_SVC["Content Service<br/>(ECS Fargate)"]
            STREAM_SVC["Streaming Service<br/>(ECS Fargate)"]
            ADS_SVC["Ad Service<br/>(ECS Fargate)"]
            ANALYTICS_SVC["Analytics Service<br/>(ECS Fargate)"]
        end
    end

    %% Caching Layer
    subgraph CachingLayer["Caching Layer"]
        REDIS_CLUSTER["ElastiCache Redis Cluster<br/>(Sessions, API Cache)"]
        REDIS_AZ1["Redis Node AZ-1"]
        REDIS_AZ2["Redis Node AZ-2"]
        REDIS_AZ3["Redis Node AZ-3"]
    end

    %% Database Layer
    subgraph DatabaseLayer["Database Layer"]
        subgraph Primary["Primary Databases"]
            RDS_MAIN["RDS PostgreSQL<br/>(Multi-AZ Master)"]
            RDS_READ1["Read Replica 1"]
            RDS_READ2["Read Replica 2"]
        end

        subgraph Analytics["Analytics Storage"]
            REDSHIFT["Redshift Cluster<br/>(Data Warehouse)"]
            S3_DATA["S3 Data Lake<br/>(Raw Analytics)"]
        end
    end

    %% Message Queues and Async Processing
    subgraph AsyncProcessing["Async Processing"]
        SQS["SQS Queues<br/>(Video Processing, Notifications)"]
        KINESIS["Kinesis Data Streams<br/>(Real-time Analytics)"]
        LAMBDA["Lambda Functions<br/>(Event Processing)"]
    end

    %% Monitoring and Security
    subgraph Infrastructure["Infrastructure & Monitoring"]
        WAF["AWS WAF<br/>(Security Filtering)"]
        CLOUDWATCH["CloudWatch<br/>(Metrics & Logs)"]
        VPC["VPC with Private Subnets<br/>(Security Isolation)"]
    end

    %% Flow Connections
    USERS --> CF
    CF --> S3_STATIC
    CF --> WAF
    WAF --> ALB
    ALB --> API_GW
    API_GW --> WEB1
    API_GW --> WEB2
    API_GW --> WEB3

    WEB1 --> AUTH_SVC
    WEB2 --> USER_SVC
    WEB3 --> CONTENT_SVC

    AUTH_SVC --> REDIS_CLUSTER
    USER_SVC --> REDIS_CLUSTER
    SUB_SVC --> REDIS_CLUSTER

    REDIS_CLUSTER --> REDIS_AZ1
    REDIS_CLUSTER --> REDIS_AZ2
    REDIS_CLUSTER --> REDIS_AZ3

    AUTH_SVC --> RDS_MAIN
    USER_SVC --> RDS_READ1
    SUB_SVC --> RDS_MAIN
    CONTENT_SVC --> RDS_READ2

    ANALYTICS_SVC --> KINESIS
    KINESIS --> S3_DATA
    S3_DATA --> REDSHIFT

    STREAM_SVC --> SQS
    SQS --> LAMBDA

    %% Styling
    classDef userStyle fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef cdnStyle fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef appStyle fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef cacheStyle fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef dbStyle fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    classDef infraStyle fill:#f1f8e9,stroke:#689f38,stroke-width:2px
    classDef asyncStyle fill:#e0f2f1,stroke:#00695c,stroke-width:2px

    class USERS,CF,S3_STATIC userStyle
    class ALB,API_GW,WAF cdnStyle
    class WEB1,WEB2,WEB3,AUTH_SVC,USER_SVC,SUB_SVC,CONTENT_SVC,STREAM_SVC,ADS_SVC,ANALYTICS_SVC appStyle
    class REDIS_CLUSTER,REDIS_AZ1,REDIS_AZ2,REDIS_AZ3 cacheStyle
    class RDS_MAIN,RDS_READ1,RDS_READ2,REDSHIFT,S3_DATA dbStyle
    class SQS,KINESIS,LAMBDA asyncStyle
    class CLOUDWATCH,VPC infraStyle
```
