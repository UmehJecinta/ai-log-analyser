#!/bin/bash
# bootstrap.sh - Run ONCE before terraform init
# Creates S3 state bucket with versioning, encryption and public access block

set -e

BUCKET_NAME="ai-log-analyser-tfstate-jecinta"
REGION="us-east-1"

echo "Creating S3 state bucket: $BUCKET_NAME"

aws s3api create-bucket \
  --bucket $BUCKET_NAME \
  --region $REGION

echo "Enabling versioning..."
aws s3api put-bucket-versioning \
  --bucket $BUCKET_NAME \
  --versioning-configuration Status=Enabled

echo "Enabling encryption..."
aws s3api put-bucket-encryption \
  --bucket $BUCKET_NAME \
  --server-side-encryption-configuration \
  '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'

echo "Blocking public access..."
aws s3api put-public-access-block \
  --bucket $BUCKET_NAME \
  --public-access-block-configuration \
  "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

echo ""
echo "Bootstrap complete! Now run:"
echo "cd terraform && terraform init && terraform apply"