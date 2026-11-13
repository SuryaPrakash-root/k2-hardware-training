#!/bin/bash

# Install hardware training dependencies

set -e

echo "=== Installing Hardware Training Dependencies ==="
echo ""

# Check if running on Apple Silicon
if [[ $(uname -m) != "arm64" ]]; then
    echo "This script is for Apple Silicon Macs only"
    exit 1
fi

echo "Running on Apple Silicon"

# Check if Python 3.12 is available
if ! command -v python3.12 &> /dev/null; then
    echo "Python 3.12 is required"
    echo "Install with: brew install python@3.12"
    exit 1
fi

echo "Python 3.12 found"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3.12 -m venv ~/k2-hardware-training/venv

# Activate virtual environment
source ~/k2-hardware-training/venv/bin/activate

echo "Virtual environment created"

# Install MLX and training dependencies
echo ""
echo "Installing training dependencies..."
pip install --upgrade pip
pip install mlx mlx-lm datasets transformers torch

echo ""
echo "Training dependencies installed"

# Test installation
echo ""
echo "Testing installation..."
python -c "import mlx; print('MLX imported successfully')"
python -c "import mlx_lm; print('mlx-lm imported successfully')"
python -c "import datasets; print('datasets imported successfully')"

echo ""
echo "=== Installation Complete ==="
echo ""
echo "To use:"
echo "  source ~/k2-hardware-training/venv/bin/activate"
echo "  python ~/k2-hardware-training/train.py"
