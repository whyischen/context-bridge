#!/bin/bash

# Exit on any error
set -e

echo "=== ContextBridge PyPI Publish Script ==="

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

echo "✅ Publish complete! Package published to PyPI"
