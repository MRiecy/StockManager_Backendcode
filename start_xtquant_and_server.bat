@echo off
echo 正在检查迅投极速交易终端...

REM 检查迅投进程是否已经运行
tasklist /FI "IMAGENAME eq xtthbss.exe" | find "xtthbss.exe" > nul
if %ERRORLEVEL% EQU 0 (
    echo 迅投极速交易终端已经在运行中。
) else (
    echo 迅投极速交易终端未运行，尝试启动...
    
    REM 尝试从不同的可能位置启动迅投
    set FOUND=0
    
    if exist "E:\迅投极速交易终端 睿智融科版\xtthbss.exe" (
        echo 找到迅投程序，正在启动...
        start "" "E:\迅投极速交易终端 睿智融科版\xtthbss.exe"
        set FOUND=1
    ) else if exist "E:\迅投极速交易终端睿智融科版\xtthbss.exe" (
        echo 找到迅投程序，正在启动...
        start "" "E:\迅投极速交易终端睿智融科版\xtthbss.exe"
        set FOUND=1
    ) else if exist "D:\迅投极速交易终端 睿智融科版\xtthbss.exe" (
        echo 找到迅投程序，正在启动...
        start "" "D:\迅投极速交易终端 睿智融科版\xtthbss.exe"
        set FOUND=1
    ) else if exist "C:\迅投极速交易终端 睿智融科版\xtthbss.exe" (
        echo 找到迅投程序，正在启动...
        start "" "C:\迅投极速交易终端 睿智融科版\xtthbss.exe"
        set FOUND=1
    )
    
    if %FOUND% EQU 0 (
        echo 未找到迅投程序。请手动启动迅投极速交易终端并登录，然后按任意键继续...
        pause > nul
    ) else (
        echo 等待迅投极速交易终端启动和登录（30秒）...
        timeout /t 30
    )
)

echo 正在启动 Django 服务器...
python manage.py runserver

echo 服务器已停止。
pause 