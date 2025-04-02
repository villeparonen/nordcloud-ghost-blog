#!/bin/bash
set -e

LAYER_NAME="ghost-layer-pyjwt"
BUILD_DIR="layer"
ZIP_FILE="layer.zip"

# Clean old builds
rm -rf "$BUILD_DIR" "$ZIP_FILE"
mkdir -p "$BUILD_DIR/python"

# Fix: Use Windows-compatible path inside Docker
docker run --rm -v "${PWD//\\/\/}/$BUILD_DIR":/build amazonlinux:2 bash -c "\
  yum install -y python3 python3-pip && \
  python3 -m ensurepip && \
  python3 -m pip install pyjwt cryptography -t /build/python"

# Check that files exist
echo "✅ Contents of layer/python:"
ls -la "$BUILD_DIR/python"

# Zip contents
cd "$BUILD_DIR"
zip -r "../$ZIP_FILE" . > /dev/null
cd ..

# Check that zip is not empty
unzip -l "$ZIP_FILE"

# Publish Layer
aws lambda publish-layer-version \
  --layer-name "$LAYER_NAME" \
  --zip-file "fileb://$ZIP_FILE" \
  --compatible-runtimes python3.12 \
  --description "Layer with pyjwt and cryptography"


# chmod +x lambda/build-layer.sh
# ./lambda/build-layer.sh