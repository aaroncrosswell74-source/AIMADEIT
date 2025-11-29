@echo off
REM =========================
REM Master Universe Setup + Starter Data
REM =========================
echo 🚀 DEPLOYING FULL UNIVERSE...
"C:\Program Files\PostgreSQL\13\bin\psql.exe" "postgresql://postgres:HbUvetaEzzHiQEhVCVGijpeSDsPAFRtF@tramway.proxy.rlwy.net:12322/railway" -f "C:\Users\bc_ri\Desktop\FOLDRIDERS UNIVERSE\AIMADEIT\setup_universe_live.sql"
echo.
echo 🎉 UNIVERSE DEPLOYMENT COMPLETE!
echo.
pause