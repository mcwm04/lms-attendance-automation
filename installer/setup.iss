; ============================================================
; LMS Attendance Automation
; Professional Installer
; Version 8
; ============================================================
#define MyAppName "LMS Attendance Automation"
#define MyAppVersion "8.0.0"
#define MyAppPublisher "Waqas Ahmad"
#define MyAppCopyright "© 2026 Waqas Ahmad"
#define MyAppURL "https://github.com/mcwm04/LMS-Automation"
#define MyAppExeName "LMS Automation.exe"

#if !FileExists("..\dist\LMS Automation.exe")
  #error "Build failed: LMS Automation.exe was not found in the dist folder."
#endif

#if !FileExists("..\assets\app.ico")
  #error "Build failed: Application icon was not found."
#endif

#if !FileExists("License.txt")
  #error "Build failed: License.txt is missing."
#endif

[Setup]

AppId={B3A8B4A5-46A6-4A6E-A6D4-8F63D71D5001}
UsePreviousAppDir=yes
UsePreviousLanguage=yes
UsePreviousTasks=yes

AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}

AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

DefaultDirName={autopf64}\{#MyAppName}
DefaultGroupName={#MyAppName}

DisableProgramGroupPage=yes

LicenseFile=License.txt

OutputDir=Output
OutputBaseFilename=LMS Attendance Automation Setup v{#MyAppVersion}

Compression=lzma2
SolidCompression=yes
InternalCompressLevel=ultra64
LZMAUseSeparateProcess=yes

WizardStyle=modern
WizardImageFile=Images\wizard.bmp
WizardSmallImageFile=Images\wizard_small.bmp

PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog

ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

DisableDirPage=no
DisableReadyMemo=no

SetupIconFile=..\assets\app.ico

UninstallDisplayIcon={app}\{#MyAppExeName}

VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription=LMS Attendance Automation Installer
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}
VersionInfoCopyright={#MyAppCopyright}

; -------------------------------------------------
; Digital Code Signing (Enable Later)
; -------------------------------------------------
; SignTool=signtool

CloseApplications=yes
RestartApplications=yes
CloseApplicationsFilter={#MyAppExeName}


[Files]
Source: "..\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Tasks]

Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"

Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"

Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]

Filename: "{app}\{#MyAppExeName}"; Description: "Launch LMS Attendance Automation"; Flags: nowait postinstall skipifsilent


[Languages]

Name: "english"; MessagesFile: "compiler:Default.isl"

[Registry]

Root: HKLM; Subkey: "Software\{#MyAppPublisher}\{#MyAppName}"; \
    ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"; \
    Flags: uninsdeletekey

Root: HKLM; Subkey: "Software\{#MyAppPublisher}\{#MyAppName}"; \
    ValueType: string; ValueName: "Version"; ValueData: "{#MyAppVersion}"

Root: HKLM; Subkey: "Software\{#MyAppPublisher}\{#MyAppName}"; \
    ValueType: string; ValueName: "Publisher"; ValueData: "{#MyAppPublisher}"

[Code]

function InitializeSetup(): Boolean;
begin
  Result := True;

  if DirExists(ExpandConstant('{autopf}\LMS Attendance Automation')) then
  begin
    MsgBox(
      'An existing installation of LMS Attendance Automation was detected.' + #13#10#13#10 +
      'The installer will upgrade the existing installation.',
      mbInformation,
      MB_OK
    );
  end;
end;