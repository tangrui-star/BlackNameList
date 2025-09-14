# Blacklist Management System Development Environment Setup Script
# Add MySQL and Python script paths to environment variables

Write-Host "Configuring development environment..." -ForegroundColor Green

# Get current user PATH environment variable
$userPath = [Environment]::GetEnvironmentVariable("PATH", "User")

# MySQL path
$mysqlPath = "C:\Program Files\MySQL\MySQL Server 9.1\bin"

# Python scripts path (if needed)
$pythonScriptsPath = "$env:APPDATA\Python\Python313\Scripts"

# Check if MySQL path exists
if (Test-Path $mysqlPath) {
    Write-Host "MySQL path exists: $mysqlPath" -ForegroundColor Green
    
    # Check if already in PATH
    if ($userPath -notlike "*$mysqlPath*") {
        Write-Host "Adding MySQL path to environment variables..." -ForegroundColor Yellow
        $newPath = $userPath + ";" + $mysqlPath
        [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
        Write-Host "MySQL path added to environment variables" -ForegroundColor Green
    } else {
        Write-Host "MySQL path already in environment variables" -ForegroundColor Green
    }
} else {
    Write-Host "MySQL path does not exist: $mysqlPath" -ForegroundColor Red
}

# Check Python scripts path
if (Test-Path $pythonScriptsPath) {
    Write-Host "Python scripts path exists: $pythonScriptsPath" -ForegroundColor Green
    
    # Check if already in PATH
    if ($userPath -notlike "*$pythonScriptsPath*") {
        Write-Host "Adding Python scripts path to environment variables..." -ForegroundColor Yellow
        $newPath = $userPath + ";" + $pythonScriptsPath
        [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
        Write-Host "Python scripts path added to environment variables" -ForegroundColor Green
    } else {
        Write-Host "Python scripts path already in environment variables" -ForegroundColor Green
    }
} else {
    Write-Host "Python scripts path does not exist: $pythonScriptsPath" -ForegroundColor Red
}

Write-Host "`nEnvironment configuration complete! Please restart your command prompt for changes to take effect." -ForegroundColor Cyan
Write-Host "After restarting, you can verify the installation with these commands:" -ForegroundColor Cyan
Write-Host "  mysql --version" -ForegroundColor White
Write-Host "  python --version" -ForegroundColor White
Write-Host "  node --version" -ForegroundColor White
Write-Host "  vue --version" -ForegroundColor White
