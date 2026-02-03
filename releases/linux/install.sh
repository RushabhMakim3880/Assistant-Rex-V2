#!/bin/bash

# R.E.X. / Cyber-REX Installation Script for Kali Linux
# Installs Python, Node.js, Nmap, and project dependencies.

set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}[*] Starting R.E.X. Installation for Kali Linux...${NC}"

# 1. Update System
echo -e "${BLUE}[*] Updating package lists...${NC}"
sudo apt-get update

# 2. Install System Dependencies
echo -e "${BLUE}[*] Installing system dependencies (Python, Node.js, Nmap)...${NC}"
# curl is usually there, ensure python3-venv and python3-pip
sudo apt-get install -y python3 python3-pip python3-venv nodejs npm nmap git curl

# Check Node version
NODE_VER=$(node -v)
echo -e "${GREEN}[+] Node.js version: $NODE_VER${NC}"

# 3. Setup Python Backend
echo -e "${BLUE}[*] Setting up Python backend...${NC}"

if [ ! -d "venv" ]; then
    echo "    Creating virtual environment..."
    python3 -m venv venv
fi

echo "    Activating virtual environment..."
source venv/bin/activate

echo "    Installing Python requirements..."
pip install -r requirements.txt

# 4. Setup Node.js Frontend
echo -e "${BLUE}[*] Setting up Node.js frontend...${NC}"
npm install

echo -e "${GREEN}[+] Installation Complete!${NC}"
echo -e "${GREEN}[+] You can now run R.E.X. with: npm run dev${NC}"
