@echo off 

set /a StartS=%time:~6,2% 
set /a StartM=%time:~3,2% 
:: ======================

:: if not exist out\android\build.ninja (
gn\bin\gn gen out\android --args="target_os = \"android\" target_cpu = \"arm\" android_sdk_version = \"android-18\" android_sdk_build_tools_version = \"18.0.1\""
:: ) 
gn\bin\ninja -C out\android\

:: ======================
set /a EndS=%time:~6,2% 
set /a EndM=%time:~3,2% 

set /a  diffS_=%EndS%-%StartS%
set /a  diffM_=%EndM%-%StartM%
echo ""
echo "Total time:  %diffM_%min %diffS_%seconds"

:: pause 