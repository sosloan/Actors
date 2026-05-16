[CmdletBinding()]
param(
    [switch]$SampleData,
    [switch]$InstallPyArrow,
    [string]$PythonCommand = "py"
)

$ErrorActionPreference = "Stop"

function Invoke-Python {
    param(
        [string[]]$Arguments
    )

    & $script:PythonCommand @Arguments

    if ($LASTEXITCODE -ne 0) {
        throw "Python command failed: $($Arguments -join ' ')"
    }
}

function Test-PythonCommand {
    param(
        [string]$CommandName
    )

    try {
        & $CommandName --version | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

if (-not (Test-PythonCommand -CommandName $PythonCommand)) {
    if ($PythonCommand -eq "py" -and (Test-PythonCommand -CommandName "python")) {
        $PythonCommand = "python"
    }
    else {
        throw "Unable to find a working Python launcher. Tried '$PythonCommand'."
    }
}

$script:PythonCommand = $PythonCommand

$RepoRoot = Split-Path -Parent $PSScriptRoot
$RequirementsPath = Join-Path $RepoRoot "database\requirements-database.txt"
$InitScript = Join-Path $RepoRoot "scripts\init_database.py"
$DemoScript = Join-Path $RepoRoot "scripts\demo_database.py"
$TestPath = Join-Path $RepoRoot "tests\test_database.py"

Push-Location $RepoRoot

try {
    Write-Host "Using Python launcher: $PythonCommand"
    Write-Host "Repository root: $RepoRoot"

    Invoke-Python -Arguments @("-m", "pip", "install", "--upgrade", "pip")
    Invoke-Python -Arguments @("-m", "pip", "install", "-r", $RequirementsPath)

    if ($InstallPyArrow) {
        Invoke-Python -Arguments @("-m", "pip", "install", "pyarrow")
    }

    $InitArguments = @($InitScript)
    if ($SampleData) {
        $InitArguments += "--sample-data"
    }
    Invoke-Python -Arguments $InitArguments

    Invoke-Python -Arguments @($DemoScript)
    Invoke-Python -Arguments @("-m", "pytest", $TestPath, "-v")

    Write-Host ""
    Write-Host "Windows database setup completed successfully."
}
finally {
    Pop-Location
}
