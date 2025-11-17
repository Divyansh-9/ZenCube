#!/bin/bash
# ZenCube Cleanup Script
# Run this anytime to remove bloat and keep project under 100 MB
# Usage: ./cleanup.sh

set -e

echo "=================================================="
echo "   ZenCube Project Cleanup"
echo "=================================================="
echo ""

# Show current size
echo "📊 Current project size:"
du -sh .
echo ""

# Confirm
read -p "Remove venv, test outputs, and cache? (y/n): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Cleanup cancelled."
    exit 0
fi

echo ""
echo "🧹 Cleaning up..."
echo ""

# Track what was removed
TOTAL_REMOVED=0

# Remove virtual environments
if [ -d "venv" ]; then
    SIZE=$(du -sh venv 2>/dev/null | cut -f1)
    echo "  🗑️  Removing venv/ ($SIZE)..."
    rm -rf venv
    TOTAL_REMOVED=1
fi

if [ -d ".venv" ]; then
    SIZE=$(du -sh .venv 2>/dev/null | cut -f1)
    echo "  🗑️  Removing .venv/ ($SIZE)..."
    rm -rf .venv
    TOTAL_REMOVED=1
fi

# Remove test output files
if [ -f "test_output.dat" ]; then
    SIZE=$(du -h test_output.dat 2>/dev/null | cut -f1)
    echo "  🗑️  Removing test_output.dat ($SIZE)..."
    rm -f test_output.dat
    TOTAL_REMOVED=1
fi

# Remove all .dat files larger than 10MB
echo "  🔍 Scanning for large .dat files..."
find . -name "*.dat" -type f -size +10M 2>/dev/null | while read file; do
    SIZE=$(du -h "$file" | cut -f1)
    echo "  🗑️  Removing: $file ($SIZE)"
    rm -f "$file"
    TOTAL_REMOVED=1
done

# Remove Python cache
echo "  🗑️  Removing Python cache..."
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Remove build artifacts
if [ -d "build" ]; then
    echo "  🗑️  Removing build/ directory..."
    rm -rf build
fi

if [ -d "dist" ]; then
    echo "  🗑️  Removing dist/ directory..."
    rm -rf dist
fi

# Remove .pytest_cache
if [ -d ".pytest_cache" ]; then
    echo "  🗑️  Removing .pytest_cache/..."
    rm -rf .pytest_cache
fi

echo ""
echo "=================================================="
echo "✅ Cleanup Complete!"
echo "=================================================="
echo ""

# Show new size
echo "📦 Project size after cleanup:"
du -sh .
echo ""

# Show file counts
FILES=$(find . -type f | wc -l)
DIRS=$(find . -type d | wc -l)
echo "📊 File count: $FILES files, $DIRS directories"
echo ""

echo "💡 Tips:"
echo "  - Run ./setup.sh to recreate venv when needed"
echo "  - Use ./cleanup.sh anytime to remove bloat"
echo "  - Large files are auto-removed before git commits"
echo ""
