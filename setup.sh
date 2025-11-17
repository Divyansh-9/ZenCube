#!/bin/bash
# ZenCube Quick Setup Script
# Creates virtual environment and installs minimal dependencies

set -e

echo "=================================================="
echo "   ZenCube Project Setup (Minimal Install)"
echo "=================================================="
echo ""

# Check if venv already exists
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment 'venv' already exists."
    read -p "Remove and recreate? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🗑️  Removing existing venv..."
        rm -rf venv
    else
        echo "❌ Setup cancelled."
        exit 0
    fi
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install minimal requirements
echo "📥 Installing minimal dependencies (GUI only)..."
pip install -r requirements-minimal.txt

echo ""
echo "=================================================="
echo "✅ Setup Complete!"
echo "=================================================="
echo ""
echo "To activate the virtual environment:"
echo "  source venv/bin/activate"
echo ""
echo "To run the GUI:"
echo "  python zencube/zencube_modern_gui.py"
echo ""
echo "To install full ML features later:"
echo "  pip install -r requirements.txt"
echo ""
echo "To deactivate when done:"
echo "  deactivate"
echo ""
