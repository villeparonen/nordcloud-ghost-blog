
# Ghost Blog – AWS Architecture for Drone Shuttles Ltd.

This project provides a Proof of Concept (PoC) for deploying the Ghost blogging platform on AWS. It is designed to meet the requirements of Drone Shuttles Ltd., a company undergoing digital modernization as part of a major product launch and increased marketing activity.

The solution is fully automated using AWS CloudFormation and focuses on high availability, scalability, security, observability, and developer experience. All components are defined as Infrastructure as Code (IaC), ensuring consistency across deployments and environments.


# Key Requirements
From the business case:
- Must be highly available and scalable to handle up to 4x traffic spikes.
- Zero downtime deployments to support multiple DevOps teams.
- Multi-environment support (e.g., dev, test, prod).
- Observability and operational tooling for developers and security teams.
- Disaster recovery and resilience in case of regional or component failure.
- Ability to delete all blog posts using a serverless function.


# Architecture
👷 Infrastructure Components: 
- ECS Fargate	Runs Ghost as a containerized service with auto-scaling and zero server management.
- Application Load Balancer (ALB)	Routes HTTP traffic to Ghost, with health checks and failover capabilities.
- CloudFront	Adds a secure HTTPS layer and improves performance via CDN caching.
- Aurora Serverless (MySQL)	Cost-optimized and scalable database backend for Ghost content.
- S3	Stores Lambda code packages and could be extended for Ghost media.
- Secrets Manager	Securely stores Ghost admin credentials and API keys.
- Lambda	Serverless function to delete all blog posts, with Secrets Manager integration.
- CloudWatch Logs & VPC Flow Logs	Provides observability into system behavior and security events.


# 🌍 Multi-Environment Strategy
All resources are parameterized with the Environment variable (dev, test, prod), allowing the same templates to deploy separate environments with isolated resources and stacks.


# 🔐 Security Design
- No hardcoded secrets; all sensitive data is managed via AWS Secrets Manager.
- ALB and ECS tasks use security groups to restrict access.,
- IAM roles are tightly scoped (least privilege principle).
- HTTPS is enforced through CloudFront, keeping ALB internal (optional).
- VPC endpoints ensure secure private access to Secrets Manager.


# 🧪 Observability
- CloudWatch Logs for Lambda, ECS, and ALB provide insight into behavior.
- Health checks ensure automated recovery if containers or instances fail.


# Ghost Blog Infrastructure – Deployment Overview

This repository defines a modular CloudFormation-based infrastructure for running a [Ghost](https://ghost.org/) blog on AWS. The stack includes ECS Fargate, RDS Aurora, ALB, CloudFront, and a Lambda function.

---

## 🔁 Deployment Order

### 1. `network.yaml`
**Creates core networking components.**
Includes:
- VPC, subnets (public & private)
- Internet Gateway, NAT Gateway
- Route tables
- Security Groups
- Secrets Manager VPC Endpoint

**Exports:**
- `GhostVPCId`
- `GhostPublicSubnet1Id`, `GhostPublicSubnet2Id`
- `GhostPrivateSubnet1Id`, `GhostPrivateSubnet2Id`
- `GhostALBSecurityGroupId`
- `GhostSecretsManagerVPCEndpointSGId`

➡️ _Why:_ All other components depend on networking.

---

### 2. `rds.yaml`
**Aurora MySQL cluster for Ghost blog.**

**Uses:**
- Private subnets from `network.yaml`

**Exports:**
- `GhostAuroraEndpoint`

➡️ _Why:_ The database must exist before ECS service starts.

---

### 3. `ecs.yaml`
**Creates ECS cluster and IAM roles.**

**Exports:**
- `ECSClusterName`
- `ECSExecutionRoleArn`
- `ECSTaskRoleArn`

➡️ _Why:_ ECS service requires cluster and roles.

---

### 4. `alb.yaml`
**Application Load Balancer (ALB)** with:
- Target Group
- ACM Certificate for HTTPS
- HTTP → HTTPS redirect

**Uses:**
- Public subnets
- ALB Security Group

**Exports:**
- `GhostALBArn`
- `GhostTargetGroupArn`
- `GhostALBDNS`
- `GhostSSLCertificateArn`

➡️ _Why:_ ECS service and CloudFront depend on ALB.

---

### 5. `cloudfront.yaml`
**CloudFront Distribution for CDN and HTTPS termination.**

**Uses:**
- ALB DNS name as origin

➡️ _Why:_ Handles HTTPS and adds caching.

---

### 6. `ecs-service.yaml`
**Deploys the Ghost ECS Fargate service.**

**Uses:**
- `GhostAuroraEndpoint`
- `ECSClusterName`
- `GhostTargetGroupArn`
- `GhostALBDNS`
- `GhostSecretsManagerVPCEndpointSGId`

➡️ _Why:_ Depends on all previous components.

---

## 🛠 Notes

- Secrets Manager stores Ghost admin API key (accessed via VPC endpoint)
- NAT Gateway enables ECS tasks to access the public internet
- HTTPS is enabled with ACM, even without a custom domain
- CloudFront handles HTTPS + caching
- All templates are reusable and support environments like `dev`, `test`, `prod`
- Deployment order must be strictly followed
- Deploy this with running deploy-all.sh script that deploys all stacks for given environment in correct order. Run it with command:  ./deploy-all.sh dev