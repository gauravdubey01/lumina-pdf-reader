"""
PyInstaller Build Script to package Lumina PDF Reader into a standalone Windows .exe.
"""
import os
import sys
import subprocess
import shutil

def build():
    print("========================================")
    print("Building Lumina PDF Reader Standalone EXE")
    print("========================================")

    project_dir = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(project_dir, "dist")
    build_dir = os.path.join(project_dir, "build")

    main_script = os.path.join(project_dir, "main.py")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=LuminaPDF",
        "--noconsole",
        "--onefile",
        "--clean",
        "--noconfirm",
        f"--icon={os.path.join(project_dir, 'assets', 'icon.ico')}",
        f"--add-data={os.path.join(project_dir, 'app')};app",
        f"--add-data={os.path.join(project_dir, 'assets')};assets",
        f"--distpath={dist_dir}",
        f"--workpath={build_dir}",
        main_script
    ]

    print(f"Running command: {' '.join(cmd)}")
    res = subprocess.run(cmd, cwd=project_dir)

    if res.returncode == 0:
        exe_path = os.path.join(dist_dir, "LuminaPDF.exe")
        print("\n========================================")
        print("BUILD SUCCESSFUL!")
        print(f"Single Standalone Executable created at:\n{exe_path}")
        print("========================================")
        return True
    else:
        print("\nBUILD FAILED with exit code:", res.returncode)
        return False

if __name__ == "__main__":
    build()
