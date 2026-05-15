; ============================================================
; INSTALADOR - PUBLICADOR REDES
; AutomaPro - Wellington Martinez
; ============================================================

#define AppName "Publicador Redes"
#define AppVersion "1.0.0"
#define AppPublisher "AutomaPro"
#define AppURL "https://automapro.online"
#define AppExeName "PublicadorRedes.exe"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}
DefaultDirName={autopf}\AutomaPro\PublicadorRedes
DefaultGroupName=AutomaPro\Publicador Redes
AllowNoIcons=yes
LicenseFile=
OutputDir=installer_output
OutputBaseFilename=PublicadorRedes_Setup_v{#AppVersion}
SetupIconFile=iconos\dashboard.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Ejecutables principales
Source: "dist\PublicadorRedes.exe";    DestDir: "{app}"; Flags: ignoreversion
Source: "dist\PanelControlRedes.exe";  DestDir: "{app}"; Flags: ignoreversion
Source: "dist\WizardPublicador.exe";   DestDir: "{app}"; Flags: ignoreversion
Source: "dist\ConfiguradorRedes.exe";  DestDir: "{app}"; Flags: ignoreversion
Source: "dist\GestorAnuncios.exe";     DestDir: "{app}"; Flags: ignoreversion
Source: "dist\GestorTareasRedes.exe";  DestDir: "{app}"; Flags: ignoreversion

; Configuración
Source: "config_global.txt";  DestDir: "{app}"; Flags: ignoreversion onlyifdoesntexist
Source: "version.txt";        DestDir: "{app}"; Flags: ignoreversion

; Carpetas necesarias
Source: "anuncios\*";   DestDir: "{app}\anuncios";  Flags: ignoreversion recursesubdirs createallsubdirs
Source: "iconos\*";     DestDir: "{app}\iconos";     Flags: ignoreversion recursesubdirs createallsubdirs
Source: "mensajes\*";   DestDir: "{app}\mensajes";   Flags: ignoreversion recursesubdirs createallsubdirs

[Dirs]
Name: "{app}\perfiles"
Name: "{app}\anuncios"
Name: "{app}\mensajes"
Name: "{app}\iconos"
Name: "{app}\installer_output"

[Icons]
; Acceso directo Panel de Control (acceso principal)
Name: "{group}\Panel de Control";      Filename: "{app}\PanelControlRedes.exe";  IconFilename: "{app}\iconos\dashboard.ico"
Name: "{group}\Publicar Ahora";        Filename: "{app}\PublicadorRedes.exe";    IconFilename: "{app}\iconos\dashboard.ico"
Name: "{group}\Gestor de Anuncios";    Filename: "{app}\GestorAnuncios.exe";     IconFilename: "{app}\iconos\anuncios.ico"
Name: "{group}\Configurador";          Filename: "{app}\ConfiguradorRedes.exe";  IconFilename: "{app}\iconos\settings.ico"
Name: "{group}\Gestor de Tareas";      Filename: "{app}\GestorTareasRedes.exe";  IconFilename: "{app}\iconos\calendar.ico"
Name: "{group}\{cm:UninstallProgram,{#AppName}}"; Filename: "{uninstallexe}"

; Acceso directo en escritorio (opcional)
Name: "{autodesktop}\Publicador Redes"; Filename: "{app}\PanelControlRedes.exe"; IconFilename: "{app}\iconos\dashboard.ico"; Tasks: desktopicon

[Run]
Filename: "{app}\WizardPublicador.exe"; Description: "Configurar Publicador Redes"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}\perfiles"
Type: filesandordirs; Name: "{app}\anuncios"