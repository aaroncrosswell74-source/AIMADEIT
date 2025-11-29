#!/bin/bash

# ===============================
# LUX EMPIRE SETUP RUNNER - WSL/LINUX
# Fully automated, bulletproof
# ===============================

# 1. Set PostgreSQL password environment variable
export PGPASSWORD="HbUvetaEzzHiQEhVCVGijpeSDsPAFRtF"

# 2. Path to your empire setup SQL script
SQL_SCRIPT="/mnt/c/Users/bc_ri/Desktop/FOLDRIDERS UNIVERSE/AIMADEIT/setup_empire_safe.sql"

# 3. Connection string
DB_CONN="postgresql://postgres@tramway.proxy.rlwy.net:12322/railway"

# 4. Execute the SQL script
echo "🚀 DEPLOYING LUX EMPIRE DATABASE..."
psql $DB_CONN -f "$SQL_SCRIPT"

# 5. Show completion message
echo ""
echo "============================="
echo "🎉 LUX EMPIRE SETUP COMPLETE"
echo "============================="
echo ""