# AI Log Analyser

Paste application or server logs and get instant AI-powered root cause analysis — what went wrong, where, and how to fix it.

## Stack

**App:** React · FastAPI · PostgreSQL · AWS Bedrock (Claude 3 Haiku)

**Infrastructure:** AWS EKS · RDS · ECR · VPC · Terraform

**DevOps:** Docker · GitHub Actions · Helm · ArgoCD · Prometheus · Grafana

## Run Locally

**1. Create `.env` file:**
```bash
touch .env
```

Add these values:
```bash
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
DB_PASSWORD=your_database_password
```

**2. Start the app:**
```bash
docker-compose up --build
```
Open `http://localhost:3000`

---

## Deploy to AWS

### Step 1 — Before terraform apply

Create Terraform state bucket:
```bash
./bootstrap.sh
```

---

### Step 2 — Terraform apply

```bash
cd terraform
terraform init
terraform validate
terraform apply
cd ..
```

This provisions everything:
- VPC, subnets, Internet Gateway, NAT Gateway
- EKS cluster and worker nodes
- RDS PostgreSQL database
- ECR image repositories
- IAM roles with least privilege
- OIDC + IRSA for secure pod authentication
- ArgoCD
- AWS Load Balancer Controller
- Prometheus + Grafana

---

### Step 3 — After terraform apply

**Connect kubectl to the cluster:**
```bash
aws eks update-kubeconfig \
  --region us-east-1 \
  --name ai-log-analyser-dev-cluster \
  --profile aws
```

**Verify nodes are ready:**
```bash
kubectl get nodes
```
> Both nodes should show `Ready` before proceeding.

**Push code to trigger CI/CD pipeline:**
```bash
git push origin master
```
> Wait for the pipeline to show ✅ green on the Actions tab before proceeding.

**Get RDS endpoint:**
```bash
cd terraform && terraform output -raw rds_endpoint && cd ..
```
> Copy the endpoint — you need it in the next step.

**Deploy application with Helm:**
```bash
helm install ai-log-analyser ./helm/ai-log-analyser \
  --set database.host=YOUR_RDS_ENDPOINT \
  --set 'database.password=YOUR_DB_PASSWORD'
```

**Apply ArgoCD application (MUST be after helm install):**
```bash
kubectl apply -f argocd/application.yaml
```

**Verify all pods are running:**
```bash
kubectl get pods
```
> All pods should show `1/1 Running` before proceeding.

**Get application URL:**
```bash
kubectl get ingress
```
> Copy the ADDRESS and open it in your browser.

---

## Access Dashboards (Local)

### ArgoCD

```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443
```
Open `https://localhost:8080` → click **Proceed to localhost (unsafe)**

Get admin password:
```bash
kubectl get secret argocd-initial-admin-secret \
  -n argocd \
  -o jsonpath='{.data.password}' | base64 -d
```
Login: username `admin` · password from command above

### Grafana

```bash
kubectl port-forward svc/prometheus-grafana 3001:80 -n monitoring
```
Open `http://localhost:3001` · Login: `admin` / `prom-operator`

---

## Destroy

### Step 1 — Before terraform destroy

**Stop ArgoCD from syncing:**
```bash
kubectl delete -f argocd/application.yaml
```

**Uninstall application:**
```bash
helm uninstall ai-log-analyser
```

**Get ALB ARN:**
```bash
aws elbv2 describe-load-balancers \
  --region us-east-1 \
  --query 'LoadBalancers[*].LoadBalancerArn' \
  --output text
```

**Delete ALB (use ARN from above):**
```bash
aws elbv2 delete-load-balancer \
  --load-balancer-arn YOUR_ALB_ARN \
  --region us-east-1
```

**Wait 30 seconds then confirm ALB is deleted:**
```bash
sleep 30
aws elbv2 describe-load-balancers \
  --region us-east-1 \
  --query 'LoadBalancers[*].LoadBalancerName' \
  --output text
```
> Should return empty. If not — wait and check again.

**Get VPC ID:**
```bash
aws ec2 describe-vpcs \
  --region us-east-1 \
  --filters "Name=tag:Name,Values=ai-log-analyser-dev-vpc" \
  --query 'Vpcs[*].VpcId' \
  --output text
```

**List security groups in VPC (use VPC ID from above):**
```bash
aws ec2 describe-security-groups \
  --region us-east-1 \
  --filters "Name=vpc-id,Values=YOUR_VPC_ID" \
  --query 'SecurityGroups[?GroupName!=`default`].[GroupId,GroupName]' \
  --output table
```

**Delete each k8s security group shown above:**
```bash
aws ec2 delete-security-group \
  --group-id YOUR_SECURITY_GROUP_ID \
  --region us-east-1
```
> Repeat for each security group. Skip the `default` one.

---

### Step 2 — Terraform destroy

```bash
cd terraform && terraform destroy
```
Type `yes` to confirm.

---

### Step 3 — After terraform destroy

**Delete S3 state bucket:**
```bash
cd .. && ./delete-state-bucket.sh
```

**Verify everything is gone:**
```bash
aws eks list-clusters --region us-east-1

aws rds describe-db-instances \
  --region us-east-1 \
  --query 'DBInstances[*].DBInstanceIdentifier'

aws elbv2 describe-load-balancers \
  --region us-east-1 \
  --query 'LoadBalancers[*].LoadBalancerName'

aws iam list-roles \
  --query 'Roles[?contains(RoleName, `ai-log-analyser`)].RoleName'

aws s3 ls
```
> All should return empty.

---

## 🔒 Security

- No credentials hardcoded anywhere in the codebase
- OIDC + IRSA for secure pod-to-AWS authentication
- EKS nodes and RDS deployed in private subnets
- All traffic routed through ALB — only internet-facing component
- Kubernetes Secrets for sensitive runtime data
- IAM roles follow least privilege principle
- GitHub Secrets for CI/CD pipeline credentials
- Terraform state encrypted at rest in S3