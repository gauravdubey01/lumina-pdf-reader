"""
PyInstaller Build Script to package OmniPDF into a standalone Windows .exe and directory for MSIX.
"""
import os
import sys
import subprocess
import shutil

def build(target="both"):
    project_dir = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(project_dir, "dist")
    build_dir = os.path.join(project_dir, "build")
    main_script = os.path.join(project_dir, "main.py")
    icon_path = os.path.join(project_dir, "assets", "icon.ico")

    # 1. Build Onedir (Required for MSIX packaging)
    print("========================================")
    print("Building OmniPDF Onedir Package for MSIX")
    print("========================================")
    cmd_dir = [
        sys.executable, "-m", "PyInstaller",
        "--name=OmniPDF",
        "--noconsole",
        "--onedir",
        "--clean",
        "--noconfirm",
        f"--icon={icon_path}",
        f"--add-data={os.path.join(project_dir, 'app')};app",
        f"--add-data={os.path.join(project_dir, 'assets')};assets",
        f"--distpath={dist_dir}",
        f"--workpath={build_dir}",
        main_script
    ]
    res1 = subprocess.run(cmd_dir, cwd=project_dir)
    if res1.returncode != 0:
        print("Onedir build failed!")
        return False

    # 2. Build Onefile standalone executable
    print("\n========================================")
    print("Building OmniPDF Standalone Single EXE")
    print("========================================")
    cmd_file = [
        sys.executable, "-m", "PyInstaller",
        "--name=OmniPDF_standalone",
        "--noconsole",
        "--onefile",
        "--noconfirm",
        f"--icon={icon_path}",
        f"--add-data={os.path.join(project_dir, 'app')};app",
        f"--add-data={os.path.join(project_dir, 'assets')};assets",
        f"--distpath={dist_dir}",
        f"--workpath={build_dir}",
        main_script
    ]
    res2 = subprocess.run(cmd_file, cwd=project_dir)
    if res2.returncode == 0:
        standalone_src = os.path.join(dist_dir, "OmniPDF_standalone.exe")
        standalone_dst = os.path.join(dist_dir, "OmniPDF-Portable.exe")
        if os.path.exists(standalone_src):
            if os.path.exists(standalone_dst):
                os.remove(standalone_dst)
            os.rename(standalone_src, standalone_dst)

    print("\n========================================")
    print("BUILD SUCCESSFUL!")
    print(f"MSIX Source Directory: {os.path.join(dist_dir, 'OmniPDF')}")
    print(f"Main Executable: {os.path.join(dist_dir, 'OmniPDF', 'OmniPDF.exe')}")
    print("========================================")
    return True

if __name__ == "__main__":
    build()
