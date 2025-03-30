#!/bin/bash
set -e

# Move to script directory
cd "$(dirname "$0")"

ENVIRONMENT=${1:-dev}
ZIP_FILE="delete-all-posts.zip"
SOURCE_FILE="delete-all-posts.py"
BUILD_DIR="build"
VENV_DIR=".venv_lambda"

echo "Building Lambda deployment package..."

# Ensure pip exists, install if not
if ! command -v pip &> /dev/null; then
  echo "pip not found. Trying to install using ensurepip..."
  python3 -m ensurepip --upgrade || py -3 -m ensurepip --upgrade
fi

# Create virtual environment
python3 -m venv "$VENV_DIR" || py -3 -m venv "$VENV_DIR"
source "$VENV_DIR/Scripts/activate" 2>/dev/null || source "$VENV_DIR/bin/activate"

echo "Installing Python dependencies (requests)..."
pip install --quiet requests -t "$BUILD_DIR"

# Copy Lambda source code
mkdir -p "$BUILD_DIR"
cp "$SOURCE_FILE" "$BUILD_DIR/"

# Create deployment package
cd "$BUILD_DIR"
zip -r "../$ZIP_FILE" . > /dev/null
cd ..

# Sanity check
if [ ! -s "$ZIP_FILE" ]; then
  echo "ERROR: ZIP file is empty! Aborting."
  exit 1
fi

echo "Uploading ZIP to S3..."
BUCKET_NAME=$(aws cloudformation list-exports \
  --query "Exports[?Name=='${ENVIRONMENT}-GhostLambdaCodeBucketName'].Value" \
  --output text)

if [ -z "$BUCKET_NAME" ]; then
  echo "ERROR: Failed to find exported S3 bucket for Lambda code."
  exit 1
fi

aws s3 cp "$ZIP_FILE" "s3://$BUCKET_NAME/delete-all-posts.zip"

echo "Deploying Lambda CloudFormation stack..."
aws cloudformation deploy \
  --stack-name "${ENVIRONMENT}-ghost-delete-posts-lambda" \
  --template-file lambda-delete-posts.yaml \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides \
    Environment="${ENVIRONMENT}"

# Cleanup
deactivate
rm -rf "$BUILD_DIR" "$VENV_DIR"

echo "Lambda deployed successfully."



# #Zip Python code.
# Upload it to the S3 bucket (based on exported value).
# Deploy the CloudFormation stack using that code.
# ./lambda/deploy-lambda.sh dev
