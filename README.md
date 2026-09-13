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

## Grafana

```bash
kubectl port-forward svc/prometheus-grafana 3000:80 -n monitoring
```
Open `http://localhost:3000` · Login: `admin` / `prom-operator`

## Destroy

```bash
cd terraform && terraform destroy
cd .. && ./delete-state-bucket.sh
```

## Security

- No hardcoded credentials anywhere
- OIDC + IRSA for secure pod-to-AWS authentication
- EKS nodes and RDS in private subnets
- Kubernetes Secrets for sensitive data
- IAM least privilege throughout