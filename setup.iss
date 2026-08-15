; ============================================================
;  LMS Attendance Automation System — Windows Installer
;  Built with Inno Setup 6.x  (https://jrsoftware.org/isinfo.php)
; ============================================================
;
;  HOW TO USE
;  ----------
;  1. Install Inno Setup 6 on your Windows machine (free).
;  2. Regenerate the version resource, then build with PyInstaller:
;         python generate_version_file.py
;         pyinstaller desktop.spec
;     desktop.spec is a ONEFILE build (no COLLECT step), so this
;     produces a single file:
;         dist\LMS Automation.exe
;     If you change APP_NAME in desktop.spec, update MyAppExeName
;     below to match.
;  3. Put this file (setup.iss) and LICENSE.txt in your project root
;     (D:\LMS Automation Version 8.1\), next to the "dist" folder.
;  4. Open setup.iss in the Inno Setup IDE and click Build > Compile
;     (or run:  "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" setup.iss )
;  5. The finished installer appears in the "installer" folder as
;     LMSAttendanceAutomation_Setup_8.1.0.exe
;
; ============================================================

#define MyAppName "LMS Attendance Automation System"
#define MyAppVersion "8.1.0"
#define MyAppPublisher "Waqas Ahmad"
#define MyAppURL ""
; --- EDIT THIS IF YOU CHANGE APP_NAME IN desktop.spec ---
#define MyAppExeName "LMS Automation.exe"

; Generate your own GUID once (Tools > Generate GUID in the Inno Setup
; IDE) and keep it forever — it identifies this app for upgrades.
#define MyAppId "{{8F2C1E4A-7B3D-4E19-9C6F-2A1B5D8E4F7C}"

[Setup]
AppId={#MyAppId}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; Install per-user into LocalAppData — no admin prompt, and matches
; PathManager's expectation that Logs/UserData/Cache/Crash/Temp are
; writable next to the executable at runtime.
DefaultDirName={localappdata}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; License page
LicenseFile=LICENSE.txt

; Look & feel
WizardStyle=modern
WizardImageFile=assets\wizard.bmp
WizardSmallImageFile=assets\wizard_small.bmp
SetupIconFile=assets\app.ico
UninstallDisplayIcon={app}\{#MyAppExeName}

; Output
OutputDir=installer
OutputBaseFilename=LMSAttendanceAutomation_Setup_{#MyAppVersion}
Compression=lzma2/max
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64compatible

; Show a "ready to install" page and let the built-in progress page
; show file names as it copies (nice detail for a slow first install).
DisableReadyPage=no
ShowLanguageDialog=auto

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

; ------------------------------------------------------------
; Custom status text shown above the progress bar during install
; ------------------------------------------------------------
[Messages]
WelcomeLabel1=Welcome to the [name] Setup Wizard
WelcomeLabel2=This will install [name/ver] on your computer.%n%nIt automates attendance submission to the UAF Learning Management System, so you no longer have to mark it by hand.%n%nIt is recommended that you close any running instance of the application before continuing.
FinishedHeadingLabel=Completing the [name] Setup Wizard
FinishedLabelNoIcons=Setup has finished installing [name] on your computer.
FinishedLabel=Setup has finished installing [name] on your computer. The application may be launched by selecting the installed shortcuts.
ClickFinish=Click Finish to exit Setup.

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked
Name: "startmenuicon"; Description: "Create a &Start Menu shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked checkedonce

[Files]
; desktop.spec is a ONEFILE build — assets/ and config/ are already
; embedded inside the exe via Analysis(datas=[...]), so only the
; single exe itself needs to be copied here.
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; IconFilename omitted — the onefile exe already has app.ico embedded
; via desktop.spec's icon=ICON_FILE, so shortcuts pick it up automatically.
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName} now"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Ask nothing fancy — just make sure generated runtime folders are
; fully removed on uninstall. Credentials/logs live under {app}\UserData
; and {app}\Logs since ROOT_DIR is the app folder in frozen builds.
Type: filesandordirs; Name: "{app}\Logs"
Type: filesandordirs; Name: "{app}\Cache"
Type: filesandordirs; Name: "{app}\Crash"
Type: filesandordirs; Name: "{app}\Temp"

[Code]
{ Optional: ask the user before wiping saved LMS credentials/config,
  since UserData\credentials.dat holds their encrypted LMS password. }
var
  KeepUserDataCheckBox: Boolean;

function InitializeUninstall(): Boolean;
begin
  KeepUserDataCheckBox := (MsgBox('Do you want to keep your saved LMS username/password and course settings for next time?' + #13#10 + #13#10 +
    'Choose "No" to remove them completely along with the application.',
    mbConfirmation, MB_YESNO) = IDYES);
  Result := True;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if (CurUninstallStep = usPostUninstall) and (not KeepUserDataCheckBox) then
  begin
    DelTree(ExpandConstant('{app}\UserData'), True, True, True);
  end;
end;
