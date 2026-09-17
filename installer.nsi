Unicode True
!include "MUI2.nsh"
!include "FileFunc.nsh"
Name "Battery Cat"
OutFile "release\Battery-Cat-1.1.2-Windows-x64-Setup.exe"
InstallDir "$LOCALAPPDATA\Programs\Battery Cat"
InstallDirRegKey HKCU "Software\BatteryCat" "InstallDir"
RequestExecutionLevel user
SetCompressor /SOLID lzma
Icon "assets\cat-clock.ico"
UninstallIcon "assets\cat-clock.ico"
VIProductVersion "1.1.2.0"
VIAddVersionKey /LANG=1033 "ProductName" "Battery Cat"
VIAddVersionKey /LANG=1033 "FileDescription" "Battery Cat installer"
VIAddVersionKey /LANG=1033 "FileVersion" "1.1.2"
VIAddVersionKey /LANG=1033 "LegalCopyright" "Battery Cat"
Var TestMode
!define MUI_ABORTWARNING
!define MUI_WELCOMEPAGE_TITLE "Selamat datang di Battery Cat"
!define MUI_WELCOMEPAGE_TEXT "Teman kecil untuk mengingatkan baterai laptop.$\r$\n$\r$\nAplikasi bekerja offline. Batas alarm, suara, dan ukuran widget dapat diatur setelah pemasangan."
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!define MUI_FINISHPAGE_RUN "$INSTDIR\BatteryCat.exe"
!define MUI_FINISHPAGE_RUN_TEXT "Buka Battery Cat"
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "Indonesian"

Function .onInit
  ${GetParameters} $R0
  ClearErrors
  ${GetOptions} $R0 "/TEST" $R1
  ${IfNot} ${Errors}
    StrCpy $TestMode "1"
  ${EndIf}
FunctionEnd

Section "Battery Cat"
  SetShellVarContext current
  SetOutPath "$INSTDIR"
  File /r "dist\BatteryCat\*"
  WriteUninstaller "$INSTDIR\Uninstall.exe"
  ${If} $TestMode != "1"
    CreateDirectory "$SMPROGRAMS\Battery Cat"
    CreateShortcut "$SMPROGRAMS\Battery Cat\Battery Cat.lnk" "$INSTDIR\BatteryCat.exe"
    CreateShortcut "$SMPROGRAMS\Battery Cat\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
    CreateShortcut "$DESKTOP\Battery Cat.lnk" "$INSTDIR\BatteryCat.exe"
    WriteRegStr HKCU "Software\BatteryCat" "InstallDir" "$INSTDIR"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\BatteryCat" "DisplayName" "Battery Cat"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\BatteryCat" "DisplayVersion" "1.1.2"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\BatteryCat" "Publisher" "Battery Cat"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\BatteryCat" "DisplayIcon" "$INSTDIR\BatteryCat.exe"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\BatteryCat" "UninstallString" '"$INSTDIR\Uninstall.exe"'
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\BatteryCat" "QuietUninstallString" '"$INSTDIR\Uninstall.exe" /S'
    WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\BatteryCat" "NoModify" 1
    WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\BatteryCat" "NoRepair" 1
  ${Else}
    FileOpen $R0 "$INSTDIR\test-install.marker" w
    FileClose $R0
  ${EndIf}
SectionEnd

Section "Uninstall"
  SetShellVarContext current
  IfFileExists "$INSTDIR\test-install.marker" test_cleanup normal_cleanup
  normal_cleanup:
    DeleteRegValue HKCU "Software\Microsoft\Windows\CurrentVersion\Run" "BatteryCat"
    DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\BatteryCat"
    DeleteRegKey HKCU "Software\BatteryCat"
    Delete "$SMPROGRAMS\Battery Cat\Battery Cat.lnk"
    Delete "$SMPROGRAMS\Battery Cat\Uninstall.lnk"
    RMDir "$SMPROGRAMS\Battery Cat"
    Delete "$DESKTOP\Battery Cat.lnk"
  test_cleanup:
  !include "uninstall-files.nsh"
  Delete "$INSTDIR\test-install.marker"
  Delete "$INSTDIR\Uninstall.exe"
  RMDir "$INSTDIR"
SectionEnd
