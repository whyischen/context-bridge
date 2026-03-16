#!/bin/bash

# Exit on any error
set -e

# Check if version parameter is provided
if [ -z "$1" ]; then
    echo "❌ Error: Version parameter is required"
    echo "Usage: ./publish.sh <version>"
    echo "Example: ./publish.sh 0.1.6"
    exit 1
fi

VERSION=$1

# Validate version format (basic check: should be like X.Y.Z)
if ! [[ $VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "❌ Error: Invalid version format. Expected format: X.Y.Z (e.g., 0.1.6)"
    exit 1
fi

echo "=== ContextBridge PyPI Publish Script ==="
echo "📌 Target version: $VERSION"

# Update root setup.py
echo "📝 Updating root setup.py..."
sed -i.bak "s/version=\"[^\"]*\"/version=\"$VERSION\"/" setup.py
rm -f setup.py.bak

# Update skill version.py
echo "📝 Updating skill version.py..."
sed -i.bak "s/__version__ = \"[^\"]*\"/__version__ = \"$VERSION\"/" skills/local-context-bridge/version.py
rm -f skills/local-context-bridge/version.py.bak

# Update skill manifest.json
echo "📝 Updating skill manifest.json..."
# Update skill version
sed -i.bak "s/\"version\": \"[^\"]*\"/\"version\": \"$VERSION\"/" skills/local-context-bridge/manifest.json
# Update cbridge-agent dependency version
sed -i.bak "s/\"cbridge-agent\": {/\"cbridge-agent\": {/" skills/local-context-bridge/manifest.json
sed -i.bak "s/\"version\": \"[^\"]*\",\n.*\"required\": true,/\"version\": \"$VERSION\",\n    \"required\": true,/" skills/local-context-bridge/manifest.json
rm -f skills/local-context-bridge/manifest.json.bak

# Use Python for more reliable JSON update
python3 << EOF
import json

manifest_path = "skills/local-context-bridge/manifest.json"
with open(manifest_path, 'r', encoding='utf-8') as f:
    manifest = json.load(f)

manifest["version"] = "$VERSION"
manifest["dependencies"]["cbridge-agent"]["version"] = "$VERSION"

with open(manifest_path, 'w', encoding='utf-8') as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)
    f.write('\n')

print(f"✅ Updated manifest.json to version $VERSION")
EOF

echo "🧹 Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info

echo "📦 Installing build dependencies..."
python -m pip install --upgrade setuptools wheel twine build

echo "📦 Building package (sdist and bdist_wheel)..."
python -m build

echo "🔍 Checking package bundle with twine..."
python -m twine check dist/*

echo "🚀 Uploading to PyPI..."
python -m twine upload dist/*

echo "✅ Publish complete! Version $VERSION published to PyPI"
