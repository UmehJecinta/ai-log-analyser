# AI Log Analyser

A DevOps tool that uses AI to analyse application and server logs — 
paste your logs and get back what went wrong, where it went wrong, 
and how to fix it.

Built as a portfolio project to demonstrate a production-grade 
DevOps stack from infrastructure to deployment.

## What's inside

**Application**
- React frontend with a clean UI for pasting logs and viewing results
- FastAPI backend that handles requests and stores analysis history
- AI microservice powered by AWS Bedrock (Claude 3 Haiku)
- PostgreSQL database for storing log sessions and results

**Infrastructure and tooling**
- AWS EKS for running containers in production
- AWS RDS for the managed PostgreSQL database
- AWS ECR for storing Docker images
- Terraform for provisioning all AWS infrastructure as code
- Docker and Docker Compose for local development
- GitHub Actions for CI/CD — builds and pushes images on every push
- ArgoCD for GitOps — automatically deploys when Helm chart changes
- Prometheus for scraping and storing metrics from all pods
- Grafana for visualising metrics on real-time dashboards
- AlertManager for sending alerts when something breaks

## How to run locally

Make sure Docker Desktop is running, then:

```bash
docker-compose up --build
```

Open your browser at `http://localhost:3000`

## How to deploy to AWS

**Step 1 — Create the Terraform state bucket:**
```bash
./bootstrap.sh
```

**Step 2 — Provision AWS infrastructure:**
```bash
cd terraform
terraform init
terraform apply
```

**Step 3 — Connect kubectl to the cluster:**
```bash
aws eks update-kubeconfig \
  --region us-east-1 \
  --name ai-log-analyser-dev-cluster \
  --profile aws
```

**Step 4 — Install ArgoCD on the cluster:**
```bash
kubectl create namespace argocd
kubectl apply -n argocd -f \
  https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

**Step 5 — Deploy the application:**
```bash
helm install ai-log-analyser ./helm/ai-log-analyser \
  --set database.password=YOUR_DB_PASSWORD \
  --set database.host=YOUR_RDS_ENDPOINT
```

**Step 6 — Apply the ArgoCD application manifest:**
```bash
kubectl apply -f argocd/application.yaml
```

**Step 7 — Install Prometheus and Grafana:**
```bash
helm repo add prometheus-community \
  https://prometheus-community.github.io/helm-charts

helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace
```

**Step 8 — Access Grafana dashboard:**
```bash
kubectl port-forward svc/prometheus-grafana 3000:80 -n monitoring
```

Open `http://localhost:3000` in your browser.
Default login: username `admin` password `prom-operator`

## How to destroy everything

```bash
cd terraform && terraform destroy
cd .. && ./delete-state-bucket.sh
```

## Security notes

- No credentials hardcoded anywhere in the codebase
- AWS credentials injected via environment variables locally
- Kubernetes Secrets used for sensitive data in production
- Terraform state encrypted at rest in S3
- IAM roles follow least privilege principle
- GitHub Secrets used for CI/CD pipeline credentials