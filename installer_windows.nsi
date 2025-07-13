; EasySCP NSIS Installer Script
; Requires NSIS 3.0 or later

!include "MUI2.nsh"

; General settings
Name "EasySCP"
OutFile "dist\EasySCP-Setup.exe"
InstallDir "$PROGRAMFILES\EasySCP"
InstallDirRegKey HKLM "Software\EasySCP" "Install_Dir"
RequestExecutionLevel admin

; Version information
!define PRODUCT_VERSION "1.0.0"
!define PRODUCT_PUBLISHER "EasySCP"
!define PRODUCT_WEB_SITE "https://github.com/yourusername/easyscp"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\EasySCP"

; MUI settings
!define MUI_ABORTWARNING
!define MUI_ICON "assets\icon.ico"
!define MUI_UNICON "assets\icon.ico"

; Welcome page
!insertmacro MUI_PAGE_WELCOME
; License page (optional)
; !insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
; Directory page
!insertmacro MUI_PAGE_DIRECTORY
; Install files page
!insertmacro MUI_PAGE_INSTFILES
; Finish page
!define MUI_FINISHPAGE_RUN "$INSTDIR\EasySCP.exe"
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_INSTFILES

; Language
!insertmacro MUI_LANGUAGE "English"

; Installer sections
Section "MainSection" SEC01
  SetOutPath "$INSTDIR"
  
  ; Copy the executable
  File "dist\EasySCP.exe"
  
  ; Create shortcuts
  CreateDirectory "$SMPROGRAMS\EasySCP"
  CreateShortcut "$SMPROGRAMS\EasySCP\EasySCP.lnk" "$INSTDIR\EasySCP.exe"
  CreateShortcut "$SMPROGRAMS\EasySCP\Uninstall.lnk" "$INSTDIR\uninstall.exe"
  CreateShortcut "$DESKTOP\EasySCP.lnk" "$INSTDIR\EasySCP.exe"
  
  ; Write uninstaller
  WriteUninstaller "$INSTDIR\uninstall.exe"
  
  ; Write registry keys
  WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "DisplayName" "EasySCP"
  WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninstall.exe"
  WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\EasySCP.exe"
  WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
  WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
  WriteRegDWORD HKLM "${PRODUCT_UNINST_KEY}" "NoModify" 1
  WriteRegDWORD HKLM "${PRODUCT_UNINST_KEY}" "NoRepair" 1
SectionEnd

; Uninstaller section
Section "Uninstall"
  ; Remove files
  Delete "$INSTDIR\EasySCP.exe"
  Delete "$INSTDIR\uninstall.exe"
  
  ; Remove shortcuts
  Delete "$SMPROGRAMS\EasySCP\*.*"
  Delete "$DESKTOP\EasySCP.lnk"
  
  ; Remove directories
  RMDir "$SMPROGRAMS\EasySCP"
  RMDir "$INSTDIR"
  
  ; Remove registry keys
  DeleteRegKey HKLM "${PRODUCT_UNINST_KEY}"
  DeleteRegKey HKLM "Software\EasySCP"
SectionEnd