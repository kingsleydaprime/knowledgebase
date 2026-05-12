#!/bin/bash

# ─── Colors ───────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ─── Header ───────────────────────────────────────
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}       SYSTEM INFORMATION       ${NC}"
echo -e "${GREEN}================================${NC}"

# ─── Basic Info ───────────────────────────────────
echo -e "\n${YELLOW}Basic Info:${NC}"
echo "Hostname:    $(hostname)"
echo "User:        $USER"
echo "Date:        $(date)"
echo "Uptime:      $(uptime -p)"

# ─── CPU ──────────────────────────────────────────
echo -e "\n${YELLOW}CPU:${NC}"
echo "Model:       $(grep 'model name' /proc/cpuinfo | head -1 | awk -F: '{print $2}' | xargs)"
echo "Cores:       $(nproc)"
echo "Load avg:    $(cat /proc/loadavg | awk '{print $1, $2, $3}')"

# ─── Memory ───────────────────────────────────────
echo -e "\n${YELLOW}Memory:${NC}"
free -h | awk 'NR==2{printf "Used: %s / Total: %s (Free: %s)\n", $3, $2, $4}'

# ─── Disk ─────────────────────────────────────────
echo -e "\n${YELLOW}Disk:${NC}"
df -h / | awk 'NR==2{printf "Used: %s / Total: %s (%s used)\n", $3, $2, $5}'

# ─── Top 5 processes by CPU ───────────────────────
echo -e "\n${YELLOW}Top 5 Processes (CPU):${NC}"
ps aux --sort=-%cpu | awk 'NR==1 || NR<=6 {printf "%-10s %-6s %-6s %s\n", $1, $2, $3, $11}'

# ─── Network ──────────────────────────────────────
echo -e "\n${YELLOW}Network Interfaces:${NC}"
ip -br addr | awk '{print $1, $3}'

echo -e "\n${GREEN}================================${NC}"
