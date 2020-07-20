param([switch]$cpuonly = $false)

echo "-----------Installing GIMP-ML-----------"

conda create -y -n gimpenv 'python=3'
conda activate gimpenv
if (!((Get-Command python).Path | Select-String -Pattern gimpenv -Quiet)) {
    throw "Failed to activate the created conda environment. Run 'conda init powershell', re-open the powershell window and try again."
}
if ($cpuonly) {
    conda install -c pytorch -y cpuonly pytorch torchvision numpy matplotlib-base
} else {
    conda install -c pytorch -y cudatoolkit pytorch torchvision numpy matplotlib-base
}
pip install -r requirements.txt
python -c "import sys; print(f'python3_executable = r\'{sys.executable}\'')" | out-file -encoding utf8 plugins/_config.py
conda deactivate

# Register the plugins directory in GIMP settings
$pluginsDir = (split-path -parent $MyInvocation.MyCommand.Definition) + '\plugins'
$gimp = (dir "C:\Program Files\GIMP 2\bin\gimp-console-*.exe").FullName
if (!($gimp -and (Test-Path $gimp))) {
    throw "Could not find GIMP. Is it installed? You will have to add '$pluginsDir' to Preferences -> Folders -> Plug-ins manually."
}
$version = (& $gimp --version | Select-String -Pattern 2\.\d+).Matches.Value
if (!($version)) {
    throw "Could not determine GIMP version."
}
$gimprcPath = ($env:APPDATA + '\GIMP\' + $version + '\gimprc')
$escapedDir = [regex]::escape($pluginsDir)
if (!(Test-Path $gimprcPath)) {
    New-Item $gimprcPath -Force
}
if (!(Select-String -Path $gimprcPath -Pattern 'plug-in-path' -Quiet)) {
    (cat $gimprcPath) + ('(plug-in-path "${gimp_dir}\\plug-ins;${gimp_plug_in_dir}\\plug-ins;' + $escapedDir + '")') | Set-Content $gimprcPath
} elseif (!(Select-String -Path $gimprcPath -Pattern ([regex]::escape($escapedDir)) -Quiet)) {
    (cat $gimprcPath) -replace '\(\s*plug-in-path\s+"', ('$0' + $escapedDir + ';') | Set-Content $gimprcPath
}

echo "-----------Installed GIMP-ML------------"
