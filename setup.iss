; ============================================================
; LMS Attendance Automation
; Professional Installer
; Version 8
; ============================================================
;
; CHANGE NOTES (2026-08-16):
;   - Switched to ONEDIR packaging. desktop.spec now builds
;     EXE()+COLLECT() instead of a single-file EXE(), so
;     PyInstaller's output is the FOLDER "dist\LMS Automation\"
;     (containing LMS Automation.exe + _internal\ + assets\ +
;     config\), not a bare "dist\LMS Automation.exe" file.
;   - Path fix: setup.iss lives at the PROJECT ROOT
;     (D:\LMS Automation Version 8.1\), not inside a separate
;     "installer\" subfolder. All "..\dist\..." / "..\assets\..."
;     references have been changed to root-relative paths
;     ("dist\...", "assets\...") — the old "..\" was climbing one
;     directory too high and causing the dist/exe existence
;     checks to fail even though the build was fine.
;   - [Files] now copies the whole onedir output folder
;     recursively (recursesubdirs/createallsubdirs) instead of a
;     single file, since everything the exe needs at runtime
;     (_internal\, bundled assets\, config\) now lives alongside
;     it rather than being baked into one exe.
;   - [Files] Excludes added for UserData\, Logs\, Cache\,
;     Crash\, Temp\ — these are RUNTIME folders that path_manager.py
;     creates next to the exe on first launch (IS_FROZEN mode
;     points ROOT_DIR at the exe's own folder). If the app was
;     smoke-tested from dist\LMS Automation\ before packaging,
;     those folders can contain real UserData\credentials.dat /
;     credentials.key from that test session. Without this
;     exclude, recursesubdirs would ship that data — and stale
;     logs/cache — to every faculty member who installs. This is
;     a safety net; also delete those folders from dist\LMS
;     Automation\ manually before building the installer.
;
#define MyAppName "LMS Attendance Automation"
#define MyAppVersion "8.0.0"
#define MyAppPublisher "Waqas Ahmad"
#define MyAppCopyright "© 2026 Waqas Ahmad"
#define MyAppURL "https://github.com/mcwm04/LMS-Automation"
#define MyAppExeName "LMS Automation.exe"
#define MyAppDistFolder "dist\LMS Automation"

#if !FileExists(MyAppDistFolder + "\" + MyAppExeName)
  #error "Build failed: LMS Automation.exe was not found in the dist\LMS Automation folder. Did you rebuild with the onedir spec?"
#endif

#if !FileExists("assets\app.ico")
  #error "Build failed: Application icon was not found."
#endif

#if !FileExists("License.txt")
  #error "Build failed: License.txt is missing."
#endif

[Setup]

AppId={{B3A8B4A5-46A6-4A6E-A6D4-8F63D71D5001}
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
WizardImageFile=assets\wizard.bmp
WizardSmallImageFile=assets\wizard_small.bmp

PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog

ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

DisableDirPage=no
DisableReadyMemo=no

SetupIconFile=assets\app.ico

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
; Onedir build: copy the ENTIRE output folder (exe + _internal\
; DLLs/data + bundled assets\/config\), not a single file.
; Excludes keeps runtime-generated folders (created by
; path_manager.py on first launch, e.g. during smoke-testing)
; out of the installer — most importantly UserData\, which can
; contain real encrypted credentials from a test login.
Source: "{#MyAppDistFolder}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "UserData\*,Logs\*,Cache\*,Crash\*,Temp\*"

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