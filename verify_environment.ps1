# Environment Verification Script for Blacklist Management System
# Check if all required development tools are properly installed

Write-Host "=== Blacklist Management System Environment Verification ===" -ForegroundColor Cyan
Write-Host ""

# Function to check command availability
function Test-Command {
    param($Command, $Description)
    
    try {
        $version = & $Command --version 2>$null
        if ($LASTEXITCODE -eq 0 -or $version) {
            Write-Host "✓ $Description" -ForegroundColor Green
            if ($version) {
                $versionLine = $version | Select-Object -First 1
                Write-Host "  Version: $versionLine" -ForegroundColor Gray
            }
            return $true
        } else {
            Write-Host "✗ $Description" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "✗ $Description" -ForegroundColor Red
        Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Check Python
$pythonOk = Test-Command "python" "Python"

# Check pip
$pipOk = Test-Command "pip" "pip (Python Package Manager)"

# Check Node.js
$nodeOk = Test-Command "node" "Node.js"

# Check npm
$npmOk = Test-Command "npm" "npm (Node Package Manager)"

# Check Vue CLI
$vueOk = Test-Command "vue" "Vue CLI"

# Check MySQL
$mysqlOk = Test-Command "mysql" "MySQL"

# Check Git
$gitOk = Test-Command "git" "Git"

Write-Host ""
Write-Host "=== Python Package Check ===" -ForegroundColor Cyan

# Check Python packages
$requiredPackages = @(
    "fastapi",
    "uvicorn", 
    "sqlalchemy",
    "pymysql",
    "pandas",
    "openpyxl",
    "fuzzywuzzy",
    "loguru"
)

foreach ($package in $requiredPackages) {
    try {
        $result = python -c "import $package; print($package.__version__)" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ $package" -ForegroundColor Green
        } else {
            Write-Host "✗ $package" -ForegroundColor Red
        }
    } catch {
        Write-Host "✗ $package" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "=== Summary ===" -ForegroundColor Cyan

$allOk = $pythonOk -and $pipOk -and $nodeOk -and $npmOk -and $vueOk -and $mysqlOk -and $gitOk

if ($allOk) {
    Write-Host "✓ All required development tools are properly installed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now start developing the Blacklist Management System:" -ForegroundColor Cyan
    Write-Host "1. Create backend project with FastAPI" -ForegroundColor White
    Write-Host "2. Create frontend project with Vue 3" -ForegroundColor White
    Write-Host "3. Set up MySQL database" -ForegroundColor White
    Write-Host "4. Import initial blacklist data" -ForegroundColor White
} else {
    Write-Host "✗ Some required tools are missing. Please install them before proceeding." -ForegroundColor Red
    Write-Host ""
    Write-Host "Missing tools:" -ForegroundColor Yellow
    if (-not $pythonOk) { Write-Host "  - Python" -ForegroundColor Red }
    if (-not $pipOk) { Write-Host "  - pip" -ForegroundColor Red }
    if (-not $nodeOk) { Write-Host "  - Node.js" -ForegroundColor Red }
    if (-not $npmOk) { Write-Host "  - npm" -ForegroundColor Red }
    if (-not $vueOk) { Write-Host "  - Vue CLI" -ForegroundColor Red }
    if (-not $mysqlOk) { Write-Host "  - MySQL" -ForegroundColor Red }
    if (-not $gitOk) { Write-Host "  - Git" -ForegroundColor Red }
}

Write-Host ""
Write-Host "=== Next Steps ===" -ForegroundColor Cyan
Write-Host "1. Start MySQL service if not running" -ForegroundColor White
Write-Host "2. Create database for the blacklist system" -ForegroundColor White
Write-Host "3. Begin backend development with FastAPI" -ForegroundColor White
Write-Host "4. Begin frontend development with Vue 3" -ForegroundColor White

