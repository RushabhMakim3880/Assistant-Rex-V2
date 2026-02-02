@echo off
set "JAVA_HOME=D:\AndroidStudio_Installed\Android Studio\jbr"
set "ANDROID_HOME=D:\AndroidStudio_Installed\AndroidSDK"
set "PATH=%JAVA_HOME%\bin;%ANDROID_HOME%\cmdline-tools\latest\bin;%PATH%"

echo Checking Java...
java -version

echo.
echo Checking SDK Manager...
call D:\AndroidStudio_Installed\AndroidSDK\cmdline-tools\latest\bin\sdkmanager.bat --list_installed

echo.
echo Done.
pause
