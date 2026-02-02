@echo off
echo ==========================================
echo      Building REX Companion App APK
echo ==========================================

:: Navigate to Flutter project
cd rex_companion

:: Set Environment Variables
set ANDROID_HOME=D:\AndroidStudio_Installed\AndroidSDK
set "JAVA_HOME=D:\AndroidStudio_Installed\Android Studio\jbr"

:: update local.properties explicitly (Forward slashes are safer for Gradle)
echo sdk.dir=D:/AndroidStudio_Installed/AndroidSDK > android\local.properties
echo flutter.sdk=D:/flutter_windows_3.38.9-stable/flutter >> android\local.properties
echo flutter.compileSdkVersion=36 >> android\local.properties
echo flutter.minSdkVersion=24 >> android\local.properties
echo flutter.targetSdkVersion=35 >> android\local.properties

:: Run Build
echo Stopping Gradle Daemons to clear cache...
cd android
call .\gradlew.bat --stop
cd ..

echo Running 'flutter clean'...
call flutter clean
echo Running 'flutter build apk --release'...
call flutter build apk --release

:: Check Result
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ==========================================
    echo [SUCCESS] APK Built Successfully!
    echo Location: rex_companion\build\app\outputs\flutter-apk\app-release.apk
    echo ==========================================
    echo.
    echo Copying to root for easy access...
    copy build\app\outputs\flutter-apk\app-release.apk ..\rex_companion_app.apk
    echo Copied to: D:\Assistants\ada_v2-main\ada_v2-main\rex_companion_app.apk
) else (
    echo.
    echo [ERROR] Build Failed. Please check the logs above.
)

pause
