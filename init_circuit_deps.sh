#!/bin/bash

# Initialize circom circuit dependencies
echo "Setting up circom circuit dependencies..."

# Create node package if it doesn't exist
if [ ! -f "./package.json" ]; then
    echo "Creating package.json..."
    npm init -y
fi

# Install circomlib
echo "Installing circomlib..."
npm install circomlib

# Check if circom is installed
if ! command -v circom &> /dev/null; then
    echo ""
    echo "WARNING: circom is not installed or not in your PATH."
    echo "The recommended way to install circom is using the Rust version:"
    echo ""
    echo "1. Install Rust if it's not already installed:"
    echo "   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh"
    echo ""
    echo "2. Clone the circom repository:"
    echo "   git clone https://github.com/iden3/circom.git"
    echo ""
    echo "3. Enter the circom directory and compile the code:"
    echo "   cd circom"
    echo "   cargo build --release"
    echo ""
    echo "4. Install circom in your system:"
    echo "   cargo install --path circom"
    echo ""
    echo "For more details, visit: https://docs.circom.io/getting-started/installation/"
    echo ""
fi

echo "Dependencies installed successfully!"
