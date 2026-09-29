"""
MSIX Packaging Pipeline for OmniPDF Microsoft Store Release.
Compiles the application, generates Store manifest, packages assets, and creates .msix using makeappx.exe.
"""
import os
import sys
import shutil
import subprocess

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

WINDOWS_KIT_BIN = r"C:\Program Files (x86)\Windows Kits\10\bin\10.0.26100.0\x64"
MAKEAPPX_PATH = os.path.join(WINDOWS_KIT_BIN, "makeappx.exe")
SIGNTOOL_PATH = os.path.join(WINDOWS_KIT_BIN, "signtool.exe")

PACKAGE_NAME = "Gauravdubey.Omnipdf"
PUBLISHER = "CN=0A36019C-61EA-47F2-A9AE-D3B27D5E13D4"
PUBLISHER_DISPLAY_NAME = "Gaurav_dubey"
VERSION = "1.0.0.0"

APPX_MANIFEST_CONTENT = f"""<?xml version="1.0" encoding="utf-8"?>
<Package
  xmlns="http://schemas.microsoft.com/appx/manifest/foundation/windows10"
  xmlns:uap="http://schemas.microsoft.com/appx/manifest/uap/windows10"
  xmlns:rescap="http://schemas.microsoft.com/appx/manifest/foundation/windows10/restrictedcapabilities"
  xmlns:desktop="http://schemas.microsoft.com/appx/manifest/desktop/windows10"
  IgnorableNamespaces="uap rescap desktop">

  <Identity
    Name="{PACKAGE_NAME}"
    Publisher="{PUBLISHER}"
    Version="{VERSION}"
    ProcessorArchitecture="x64" />

  <Properties>
    <DisplayName>OmniPDF</DisplayName>
    <PublisherDisplayName>{PUBLISHER_DISPLAY_NAME}</PublisherDisplayName>
    <Logo>Assets\\StoreLogo.png</Logo>
    <Description>OmniPDF - Modern Book Reading &amp; Productivity Suite for Windows</Description>
  </Properties>

  <Dependencies>
    <TargetDeviceFamily Name="Windows.Desktop" MinVersion="10.0.17763.0" MaxVersionTested="10.0.22621.0" />
  </Dependencies>

  <Resources>
    <Resource Language="en-us" />
  </Resources>

  <Applications>
    <Application Id="App"
      Executable="OmniPDF.exe"
      EntryPoint="Windows.FullTrustApplication">
      <uap:VisualElements
        DisplayName="OmniPDF"
        Description="OmniPDF - Modern Book Reading &amp; Productivity Suite"
        BackgroundColor="transparent"
        Square150x150Logo="Assets\\Square150x150Logo.png"
        Square44x44Logo="Assets\\Square44x44Logo.png">
        <uap:DefaultTile
          Wide310x150Logo="Assets\\Wide310x150Logo.png"
          Square71x71Logo="Assets\\SmallTile.png"
          Square310x310Logo="Assets\\LargeTile.png"
          ShortName="OmniPDF">
          <uap:ShowNameOnTiles>
            <uap:ShowOn Tile="square150x150Logo" />
            <uap:ShowOn Tile="wide310x150Logo" />
            <uap:ShowOn Tile="square310x310Logo" />
          </uap:ShowNameOnTiles>
        </uap:DefaultTile>
        <uap:SplashScreen Image="Assets\\SplashScreen.png" BackgroundColor="#141517" />
      </uap:VisualElements>
      <Extensions>
        <uap:Extension Category="windows.fileTypeAssociation">
          <uap:FileTypeAssociation Name="pdf">
            <uap:SupportedFileTypes>
              <uap:FileType>.pdf</uap:FileType>
            </uap:SupportedFileTypes>
            <uap:DisplayName>PDF Document</uap:DisplayName>
            <uap:EditFlags OpenIsSafe="true" />
          </uap:FileTypeAssociation>
        </uap:Extension>
      </Extensions>
    </Application>
  </Applications>

  <Capabilities>
    <rescap:Capability Name="runFullTrust" />
  </Capabilities>
</Package>
"""

def create_msix_package():
    project_dir = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(project_dir, "dist")
    app_dir = os.path.join(dist_dir, "OmniPDF")

    print("==================================================")
    print("  Creating OmniPDF Microsoft Store MSIX Package   ")
    print("==================================================")

    # 1. Verify Application Build exists
    exe_path = os.path.join(app_dir, "OmniPDF.exe")
    if not os.path.exists(exe_path):
        print("OmniPDF.exe not found in dist/OmniPDF. Running build_exe.py first...")
        from build_exe import build
        if not build():
            print("Failed to build application executable!")
            return False

    # 2. Write AppxManifest.xml into packaging directory
    manifest_path = os.path.join(app_dir, "AppxManifest.xml")
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write(APPX_MANIFEST_CONTENT.strip())
    print(f"[OK] Created AppxManifest.xml with Publisher: {PUBLISHER}")

    # 3. Copy Store Assets into app_dir/Assets/
    store_assets_src = os.path.join(project_dir, "assets", "StoreAssets")
    app_assets_dst = os.path.join(app_dir, "Assets")
    os.makedirs(app_assets_dst, exist_ok=True)

    for item in os.listdir(store_assets_src):
        src_file = os.path.join(store_assets_src, item)
        dst_file = os.path.join(app_assets_dst, item)
        shutil.copy2(src_file, dst_file)
    print(f"[OK] Copied Store visual assets into {app_assets_dst}")

    # 4. Run makeappx.exe pack
    output_msix = os.path.join(dist_dir, f"{PACKAGE_NAME}_{VERSION}_x64.msix")
    if os.path.exists(output_msix):
        try:
            os.remove(output_msix)
        except Exception:
            pass

    cmd = [
        MAKEAPPX_PATH, "pack",
        "/d", app_dir,
        "/p", output_msix,
        "/o"  # Overwrite
    ]
    print(f"\nRunning MakeAppx:\n{' '.join(cmd)}")
    res = subprocess.run(cmd)

    if res.returncode != 0:
        print("\n[ERROR] MakeAppx packaging failed!")
        return False

    print(f"\n[OK] Successfully created MSIX package:")
    print(f"  {output_msix}")

    # 5. Optional: Sign package for local test installation
    pfx_cert = os.path.join(dist_dir, "OmniPDF_TestCert.pfx")
    _sign_for_local_testing(output_msix, pfx_cert)

    print("\n==================================================")
    print("         MSIX PACKAGING COMPLETE!                 ")
    print("==================================================")
    print(f"Package File : {output_msix}")
    print(f"Package Name : {PACKAGE_NAME}")
    print(f"Publisher    : {PUBLISHER}")
    print(f"Version      : {VERSION}")
    print(f"Store Ready  : YES (Upload directly to Partner Center)")
    print("==================================================")
    return True

def _sign_for_local_testing(msix_path: str, pfx_path: str):
    """Generates a matching self-signed cert and signs MSIX for local developer testing."""
    if not os.path.exists(SIGNTOOL_PATH):
        return

    print("\n[Signing for Local Testing]")
    # PowerShell script to create cert if not exists
    ps_cert = f"""
    $cert = Get-ChildItem -Path Cert:\\CurrentUser\\My | Where-Object {{ $_.Subject -eq '{PUBLISHER}' }} | Select-Object -First 1
    if (-not $cert) {{
        $cert = New-SelfSignedCertificate -Type Custom -Subject '{PUBLISHER}' `
            -KeyUsage DigitalSignature -FriendlyName 'OmniPDF Test Certificate' `
            -CertStoreLocation 'Cert:\\CurrentUser\\My' -TextExtension @("2.5.29.37={{text}}1.3.6.1.5.5.7.3.3")
    }}
    $pwd = ConvertTo-SecureString -String 'omnipdf123' -Force -AsPlainText
    Export-PfxCertificate -Cert $cert -FilePath '{pfx_path}' -Password $pwd | Out-Null
    """
    try:
        subprocess.run(["powershell", "-NoProfile", "-Command", ps_cert], check=True, capture_output=True)
        if os.path.exists(pfx_path):
            sign_cmd = [
                SIGNTOOL_PATH, "sign",
                "/fd", "SHA256",
                "/a",
                "/f", pfx_path,
                "/p", "omnipdf123",
                msix_path
            ]
            res = subprocess.run(sign_cmd, capture_output=True, text=True)
            if res.returncode == 0:
                print("[OK] MSIX signed successfully with developer certificate.")
            else:
                print("Note on signing:", res.stderr.strip() or res.stdout.strip())
    except Exception as e:
        print(f"Note: Could not self-sign: {e}")

if __name__ == "__main__":
    create_msix_package()
