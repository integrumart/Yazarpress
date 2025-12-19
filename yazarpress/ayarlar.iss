[Setup]
AppName=YazarPress
AppVersion=2.6
DefaultDirName={autopf}\YazarPress
DefaultGroupName=YazarPress
UninstallDisplayIcon={app}\YazarPress_v2.6.exe
Compression=none
SolidCompression=no
WizardStyle=modern
; Program her zaman 'Tüm Kullanıcılar' için yüklensin (Listede görünmesi için kritik)
PrivilegesRequired=admin

OutputDir=C:\Users\volkano\Desktop\yazarpress\Output
OutputBaseFilename=YazarPress_Kurulum_v2.6_Kesin

[Tasks]
Name: "desktopicon"; Description: "Masaüstü simgesi oluştur"; GroupDescription: "Ek simgeler:"; Flags: unchecked

[Files]
Source: "C:\Users\volkano\Desktop\yazarpress\dist\YazarPress_v2.6.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\volkano\Desktop\yazarpress\logo.png"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Başlat Menüsü klasörü ve kısayolu
Name: "{group}\YazarPress"; Filename: "{app}\YazarPress_v2.6.exe"; IconFilename: "{app}\logo.png"
; Başlat Menüsü -> Programlar listesine direkt ekle
Name: "{commonprograms}\YazarPress"; Filename: "{app}\YazarPress_v2.6.exe"
; Masaüstü kısayolu
Name: "{autodesktop}\YazarPress"; Filename: "{app}\YazarPress_v2.6.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\YazarPress_v2.6.exe"; Description: "YazarPress Uygulamasını Başlat"; Flags: nowait postinstall skipifsilent