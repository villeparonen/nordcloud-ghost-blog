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