# AI Log Analyser

Paste application or server logs and get instant AI-powered root cause analysis — what went wrong, where, and how to fix it.

## Stack

**App:** React · FastAPI · PostgreSQL · AWS Bedrock (Claude 3 Haiku)

**Infrastructure:** AWS EKS · RDS · ECR · VPC · Terraform

**DevOps:** Docker · GitHub Actions · Helm · ArgoCD · Prometheus · Grafana

## Run Locally

```bash
docker-compose up --build
```
Open `http://localhost:3000`

## Deploy to AWS

```bash
# 1. Create state bucket
./bootstrap.sh

# 2. Provision everything (EKS, RDS, ECR, ArgoCD, Prometheus, ALB Controller)
cd terraform && terraform init && terraform apply

# 3. Connect kubectl
aws eks update-kubeconfig --region us-east-1 --name ai-log-analyser-dev-cluster --profile aws

# 4. Push code to trigger CI/CD pipeline (builds and pushes images to ECR)
git push origin master

# 5. Get RDS endpoint
cd terraform && terraform output -raw rds_endpoint

# 6. Deploy app with Helm (use RDS endpoint from step 5)
cd .. && helm install ai-log-analyser ./helm/ai-log-analyser \
  --set database.host=YOUR_RDS_ENDPOINT \
  --set 'database.password=YOUR_DB_PASSWORD'

# 7. Apply ArgoCD application (do this AFTER helm install)
kubectl apply -f argocd/application.yaml

# 8. Get app URL
kubectl get ingress
```

## Access Dashboards (Local)

**ArgoCD:**
```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443
```
Open `https://localhost:8080` → click "Proceed to localhost (unsafe)"

Get password:
```bash
kubectl get secret argocd-initial-admin-secret -n argocd \
  -o jsonpath='{.data.password}' | base64 -d
```
Login: username `admin`

**Grafana:**
```bash
kubectl port-forward svc/prometheus-grafana 3001:80 -n monitoring
```
Open `http://localhost:3001` · Login: `admin` / `prom-operator`

## Destroy

**Important — run in this exact order to avoid errors:**

```bash
# 1. Remove application and ALB first
helm uninstall ai-log-analyser

# 2. Wait 30 seconds for ALB to be fully deleted
sleep 30

# 3. Verify ALB is gone before proceeding
aws elbv2 describe-load-balancers \
  --region us-east-1 \
  --query 'LoadBalancers[*].LoadBalancerName' \
  --output text

# 4. Destroy all AWS infrastructure
cd terraform && terraform destroy

# 5. Delete S3 state bucket
cd .. && ./delete-state-bucket.sh
```

**Verify everything is deleted:**
```bash
aws eks list-clusters --region us-east-1
aws rds describe-db-instances --region us-east-1 --query 'DBInstances[*].DBInstanceIdentifier'
aws elbv2 describe-load-balancers --region us-east-1 --query 'LoadBalancers[*].LoadBalancerName'
aws s3 ls
```

All commands should return empty.

## Security

- No hardcoded credentials anywhere
- OIDC + IRSA for secure pod-to-AWS authentication
- EKS nodes and RDS in private subnets
- Kubernetes Secrets for sensitive data
- IAM least privilege throughout