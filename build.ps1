$version = Invoke-Expression ('.\venv\Scripts\python.exe -c "from __version__ import __version__;print(__version__)"')

New-Item -ErrorAction Ignore -ItemType Directory -Path release
Set-Location .\release
Invoke-Expression ("..\venv\Scripts\pyinstaller.exe ..\main.spec")

Write-Output  "build version: $version"

# crate release dir 
$releasedir = "otogi-frontier-updater_" + $version + "_windows"
New-Item -ErrorAction Ignore -ItemType Directory -Path $releasedir

# move config file
Copy-Item ..\update_server.ini .\$releasedir\update_server.ini

# rename main.exe
$newname = "otogi-frontier-updater.exe"
Move-Item -Force .\dist\main.exe .\$newname

# move exe to run
Copy-Item -Force .\$newname ..\otogi-frontier-updater.exe

# pack release dir
Move-Item -Force .\$newname .\$releasedir
Compress-Archive -Force -Path .\$releasedir -DestinationPath .\$releasedir.zip

# clean up
Remove-Item -Recurse -Force .\$releasedir
Remove-Item -Recurse -Force .\dist