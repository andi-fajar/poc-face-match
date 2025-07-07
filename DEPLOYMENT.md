# AWS Deployment Guide 🚀

Complete deployment guide for Face Matching POC on AWS EC2 and ECS.

## Table of Contents
- [Minimum Requirements](#minimum-requirements)
- [Deployment Options](#deployment-options)
  - [Option 1: EC2 with Docker Compose](#option-1-ec2-with-docker-compose-recommended)
  - [Option 2: ECS Fargate](#option-2-ecs-fargate-managed)
  - [Option 3: ECS on EC2](#option-3-ecs-on-ec2-hybrid)
- [Production Considerations](#production-considerations)
- [Cost Estimation](#cost-estimation)
- [Troubleshooting](#troubleshooting)

## Minimum Requirements

### System Specifications

#### **EC2 Instance Requirements:**
- **Instance Type**: `t3.medium` (minimum) or `t3.large` (recommended)
- **vCPUs**: 2-4 vCPUs minimum
- **Memory**: 4-8 GB RAM
  - DeepFace library: ~1-2 GB
  - TensorFlow models: ~2-3 GB
  - 9 preloaded models: ~2-3 GB
  - System overhead: ~1 GB
- **Storage**: 20-30 GB EBS volume
  - Docker images: ~3-5 GB
  - Model weights: ~5-10 GB
  - System files: ~5-10 GB
- **OS**: Amazon Linux 2023 or Ubuntu 22.04 LTS

#### **ECS Task Requirements:**
- **Task Memory**: 4096-8192 MiB
- **Task CPU**: 2048-4096 CPU units
- **Frontend Container**: 512 MiB memory, 256 CPU units
- **Backend Container**: 3584-7680 MiB memory, 1792-3840 CPU units

#### **Network Requirements:**
- **Security Groups**: 
  - Port 80 (HTTP)
  - Port 443 (HTTPS)
  - Port 22 (SSH for management)
- **VPC**: Default VPC or custom VPC with internet gateway

---

## Deployment Options

### Option 1: EC2 with Docker Compose (Recommended)

**Best for**: POC, development, small-scale production

#### Step 1: Launch EC2 Instance

```bash
# Create EC2 instance via AWS CLI
aws ec2 run-instances \
  --image-id ami-0c7217cdde317cfec \
  --instance-type t3.large \
  --key-name your-key-pair \
  --security-group-ids sg-xxxxxxxxx \
  --subnet-id subnet-xxxxxxxxx \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=face-matching-poc}]'
```

#### Step 2: Connect and Setup

```bash
# Connect to instance
ssh -i your-key.pem ec2-user@your-instance-ip

# Update system
sudo yum update -y

# Install Docker
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ec2-user

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Logout and login again for group changes
exit
```

#### Step 3: Deploy Application

```bash
# Clone repository
git clone https://github.com/your-username/poc-face-match.git
cd poc-face-match

# Build and run
docker-compose up --build -d

# Check status
docker-compose ps
docker-compose logs -f
```

#### Step 4: Configure Security Group

```bash
# Allow HTTP traffic
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxxxxxx \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0

# Allow HTTPS traffic
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxxxxxx \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0
```

---

### Option 2: ECS Fargate (Managed)

**Best for**: Production, auto-scaling, serverless

#### Step 1: Build and Push Images

```bash
# Create ECR repositories
aws ecr create-repository --repository-name face-matching-backend
aws ecr create-repository --repository-name face-matching-frontend

# Get login token
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com

# Build and tag images
docker build -t face-matching-backend ./backend
docker build -t face-matching-frontend ./frontend

docker tag face-matching-backend:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/face-matching-backend:latest
docker tag face-matching-frontend:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/face-matching-frontend:latest

# Push images
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/face-matching-backend:latest
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/face-matching-frontend:latest
```

#### Step 2: Create ECS Cluster

```bash
# Create cluster
aws ecs create-cluster --cluster-name face-matching-cluster --capacity-providers FARGATE
```

#### Step 3: Create Task Definitions

**Backend Task Definition** (`backend-task.json`):
```json
{
  "family": "face-matching-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "2048",
  "memory": "4096",
  "executionRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "123456789012.dkr.ecr.us-east-1.amazonaws.com/face-matching-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "essential": true,
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/face-matching-backend",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

**Frontend Task Definition** (`frontend-task.json`):
```json
{
  "family": "face-matching-frontend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "frontend",
      "image": "123456789012.dkr.ecr.us-east-1.amazonaws.com/face-matching-frontend:latest",
      "portMappings": [
        {
          "containerPort": 80,
          "protocol": "tcp"
        }
      ],
      "essential": true,
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/face-matching-frontend",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

#### Step 4: Register Task Definitions

```bash
aws ecs register-task-definition --cli-input-json file://backend-task.json
aws ecs register-task-definition --cli-input-json file://frontend-task.json
```

#### Step 5: Create Services

```bash
# Create backend service
aws ecs create-service \
  --cluster face-matching-cluster \
  --service-name backend-service \
  --task-definition face-matching-backend \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxxxxxxxx],securityGroups=[sg-xxxxxxxxx],assignPublicIp=ENABLED}"

# Create frontend service  
aws ecs create-service \
  --cluster face-matching-cluster \
  --service-name frontend-service \
  --task-definition face-matching-frontend \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxxxxxxxx],securityGroups=[sg-xxxxxxxxx],assignPublicIp=ENABLED}"
```

---

### Option 3: ECS on EC2 (Hybrid)

**Best for**: Cost optimization, persistent workloads

#### Step 1: Launch ECS-Optimized EC2

```bash
# Launch ECS-optimized instance
aws ec2 run-instances \
  --image-id ami-0c02fb55956c7d316 \
  --instance-type t3.large \
  --key-name your-key-pair \
  --security-group-ids sg-xxxxxxxxx \
  --subnet-id subnet-xxxxxxxxx \
  --user-data file://ecs-user-data.sh \
  --iam-instance-profile Name=ecsInstanceRole
```

**ECS User Data** (`ecs-user-data.sh`):
```bash
#!/bin/bash
echo ECS_CLUSTER=face-matching-cluster >> /etc/ecs/ecs.config
echo ECS_AVAILABLE_LOGGING_DRIVERS='["json-file","awslogs"]' >> /etc/ecs/ecs.config
```

#### Step 2: Register Instance to Cluster

The instance will automatically register to the cluster specified in user data.

#### Step 3: Deploy Services

Use the same task definitions and service creation commands as Option 2, but with `launch-type EC2` instead of `FARGATE`.

---

## Production Considerations

### Load Balancer Setup

#### Application Load Balancer

```bash
# Create ALB
aws elbv2 create-load-balancer \
  --name face-matching-alb \
  --subnets subnet-xxxxxxxxx subnet-yyyyyyyyy \
  --security-groups sg-xxxxxxxxx

# Create target groups
aws elbv2 create-target-group \
  --name frontend-targets \
  --protocol HTTP \
  --port 80 \
  --vpc-id vpc-xxxxxxxxx \
  --target-type ip

aws elbv2 create-target-group \
  --name backend-targets \
  --protocol HTTP \
  --port 8000 \
  --vpc-id vpc-xxxxxxxxx \
  --target-type ip

# Create listeners
aws elbv2 create-listener \
  --load-balancer-arn arn:aws:elasticloadbalancing:... \
  --protocol HTTP \
  --port 80 \
  --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:...
```

### HTTPS/SSL Setup

```bash
# Request SSL certificate
aws acm request-certificate \
  --domain-name your-domain.com \
  --validation-method DNS

# Create HTTPS listener
aws elbv2 create-listener \
  --load-balancer-arn arn:aws:elasticloadbalancing:... \
  --protocol HTTPS \
  --port 443 \
  --certificates CertificateArn=arn:aws:acm:... \
  --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:...
```

### Persistent Storage

#### EFS for Model Weights

```bash
# Create EFS file system
aws efs create-file-system \
  --performance-mode generalPurpose \
  --tags Key=Name,Value=face-matching-models

# Create mount targets
aws efs create-mount-target \
  --file-system-id fs-xxxxxxxxx \
  --subnet-id subnet-xxxxxxxxx \
  --security-groups sg-xxxxxxxxx
```

### Monitoring and Logging

#### CloudWatch Setup

```bash
# Create log groups
aws logs create-log-group --log-group-name /ecs/face-matching-backend
aws logs create-log-group --log-group-name /ecs/face-matching-frontend

# Create CloudWatch dashboard
aws cloudwatch put-dashboard \
  --dashboard-name "FaceMatchingPOC" \
  --dashboard-body file://dashboard.json
```

### Auto Scaling

#### ECS Service Auto Scaling

```bash
# Register scalable target
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --resource-id service/face-matching-cluster/backend-service \
  --scalable-dimension ecs:service:DesiredCount \
  --min-capacity 1 \
  --max-capacity 10

# Create scaling policy
aws application-autoscaling put-scaling-policy \
  --service-namespace ecs \
  --resource-id service/face-matching-cluster/backend-service \
  --scalable-dimension ecs:service:DesiredCount \
  --policy-name cpu-scaling \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration file://scaling-policy.json
```

---

## Cost Estimation

### Monthly Costs (US East 1)

#### EC2 Deployment
- **t3.large (24/7)**: ~$67/month
- **EBS gp3 (30GB)**: ~$2.40/month
- **Data Transfer**: ~$5-20/month
- **Total**: ~$75-90/month

#### ECS Fargate Deployment
- **Backend (4GB, 2vCPU, 24/7)**: ~$60/month
- **Frontend (1GB, 0.5vCPU, 24/7)**: ~$15/month
- **ALB**: ~$22/month
- **Data Transfer**: ~$5-20/month
- **Total**: ~$102-117/month

#### Cost Optimization Tips
1. **Use Spot Instances**: Save up to 70% on EC2 costs
2. **Schedule Scaling**: Scale down during off-hours
3. **Reserved Instances**: Save 30-75% for predictable workloads
4. **EFS Infrequent Access**: Reduce storage costs by 85%

---

## Troubleshooting

### Common Issues

#### 1. Memory Issues
```bash
# Check memory usage
docker stats

# Increase ECS task memory
aws ecs update-service --cluster face-matching-cluster --service backend-service --task-definition face-matching-backend:2

# Monitor CloudWatch metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name MemoryUtilization \
  --dimensions Name=ServiceName,Value=backend-service \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-01T23:59:59Z \
  --period 300 \
  --statistics Average
```

#### 2. Model Loading Failures
```bash
# Check backend logs
docker-compose logs backend

# Verify model download
docker exec -it backend_container ls -la /root/.deepface/weights/

# Check disk space
df -h
```

#### 3. Network Connectivity
```bash
# Test backend health
curl http://your-instance-ip:8000/health

# Check security groups
aws ec2 describe-security-groups --group-ids sg-xxxxxxxxx

# Test internal connectivity
docker exec -it frontend_container curl http://backend:8000/health
```

#### 4. Performance Issues
```bash
# Monitor CPU usage
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --dimensions Name=ServiceName,Value=backend-service \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-01T23:59:59Z \
  --period 300 \
  --statistics Average

# Scale up resources
aws ecs update-service \
  --cluster face-matching-cluster \
  --service backend-service \
  --desired-count 2
```

### Debugging Commands

```bash
# ECS service status
aws ecs describe-services --cluster face-matching-cluster --services backend-service

# Task details
aws ecs describe-tasks --cluster face-matching-cluster --tasks task-id

# Container logs
aws logs get-log-events --log-group-name /ecs/face-matching-backend --log-stream-name ecs/backend/task-id

# EC2 instance health
aws ec2 describe-instance-status --instance-ids i-xxxxxxxxx
```

---

## Support

For deployment issues:
1. Check [GitHub Issues](https://github.com/your-username/poc-face-match/issues)
2. Review AWS documentation for specific services
3. Monitor CloudWatch logs and metrics

---

**Created by [@andi-fajar](https://github.com/andi-fajar) & [Claude.ai](https://claude.ai)**