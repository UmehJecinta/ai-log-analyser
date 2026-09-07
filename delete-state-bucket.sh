#!/bin/bash
# delete-state-bucket.sh
# Run this AFTER terraform destroy
# Deletes the S3 state bucket cleanly

set -e

BUCKET_NAME="ai-log-analyser-tfstate-jecinta"
REGION="us-east-1"

echo "Deleting all object versions..."
aws s3api delete-objects \
  --bucket $BUCKET_NAME \
  --delete "$(aws s3api list-object-versions \
  --bucket $BUCKET_NAME \
  --query '{Objects: Versions[].{Key:Key,VersionId:VersionId}}' \
  --output json)" 2>/dev/null || true

echo "Deleting all delete markers..."
aws s3api delete-objects \
  --bucket $BUCKET_NAME \
  --delete "$(aws s3api list-object-versions \
  --bucket $BUCKET_NAME \
  --query '{Objects: DeleteMarkers[].{Key:Key,VersionId:VersionId}}' \
  --output json)" 2>/dev/null || true

echo "Deleting remaining objects..."
aws s3 rm s3://$BUCKET_NAME --recursive 2>/dev/null || true

echo "Deleting bucket..."
aws s3api delete-bucket \
  --bucket $BUCKET_NAME \
  --region $REGION

echo "S3 bucket deleted successfully!"
echo "Next time run: ./bootstrap.sh"