$ErrorActionPreference = 'Stop'
$Installer = Join-Path $PSScriptRoot 'install.py'
if (Get-Command py -ErrorAction SilentlyContinue) { & py -3 $Installer @args }
elseif (Get-Command python -ErrorAction SilentlyContinue) { & python $Installer @args }
else { throw 'Install Python 3.9 or later first.' }
exit $LASTEXITCODE
