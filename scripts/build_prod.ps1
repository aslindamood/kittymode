# Production Build Script for KittyMode
# Creates a minimal venv with only runtime dependencies for smaller exe size

$ErrorActionPreference = "Stop"

# Get the script's directory and go up one level to project root
if ($PSScriptRoot) {
    $ProjectRoot = (Get-Item $PSScriptRoot).Parent.FullName
} else {
    $ProjectRoot = (Get-Location).Path
}

Write-Host "=== KittyMode Production Build ===" -ForegroundColor Cyan
Write-Host "Project root: $ProjectRoot"

# Clean up old production venv if exists
$ProdVenv = Join-Path $ProjectRoot ".venv_prod"
if (Test-Path $ProdVenv) {
    Write-Host "Removing old production venv..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force $ProdVenv
}

# Create fresh production venv
Write-Host "Creating production virtual environment..." -ForegroundColor Green
python -m venv $ProdVenv

# Activate and install minimal dependencies
$PipExe = Join-Path $ProdVenv "Scripts\pip.exe"
$PythonExe = Join-Path $ProdVenv "Scripts\python.exe"

Write-Host "Installing minimal runtime dependencies..." -ForegroundColor Green

# Core runtime dependencies only (no torch!)
& $PipExe install --upgrade pip
& $PipExe install `
    onnxruntime `
    numpy `
    pynput `
    pystray `
    Pillow `
    PyInstaller `
    pyinstaller-hooks-contrib

# Install transformers WITHOUT torch backend
# We only need the tokenizer, not the full ML framework
& $PipExe install transformers --no-deps
& $PipExe install `
    tokenizers `
    huggingface-hub `
    safetensors `
    filelock `
    requests `
    tqdm `
    pyyaml `
    regex `
    packaging

Write-Host "Verifying ONNX model exists..." -ForegroundColor Green
$OnnxModel = Join-Path $ProjectRoot "models\onnx\model.onnx"
if (-not (Test-Path $OnnxModel)) {
    Write-Host "ERROR: ONNX model not found at $OnnxModel" -ForegroundColor Red
    Write-Host "Run 'python scripts/export_onnx.py' first to export the model." -ForegroundColor Red
    exit 1
}

# Clean build artifacts
Write-Host "Cleaning build artifacts..." -ForegroundColor Yellow
$DistPath = Join-Path $ProjectRoot "dist"
$BuildPath = Join-Path $ProjectRoot "build"
if (Test-Path $DistPath) { Remove-Item -Recurse -Force $DistPath }
if (Test-Path $BuildPath) { Remove-Item -Recurse -Force $BuildPath }

# Build with PyInstaller
Write-Host "Building executable with PyInstaller..." -ForegroundColor Green
Push-Location $ProjectRoot
& $PythonExe -m PyInstaller --clean kittymode.spec
Pop-Location

# Check result
$ExePath = Join-Path $ProjectRoot "dist\KittyMode.exe"
if (Test-Path $ExePath) {
    $Size = (Get-Item $ExePath).Length / 1MB
    Write-Host ""
    Write-Host "=== Build Complete ===" -ForegroundColor Green
    Write-Host "Executable: $ExePath"
    Write-Host ("Size: {0:N1} MB" -f $Size) -ForegroundColor Cyan
} else {
    Write-Host "ERROR: Build failed - executable not found" -ForegroundColor Red
    exit 1
}
