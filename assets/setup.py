#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author: @frnAlt 
GitHub: https://github.com/frnAlt /FARHAN-Shot
License: MIT License
Disclaimer:
    This tool is for educational and authorized penetration testing only.  
    Do NOT use on unauthorized networks.  
    The author is not responsible for any misuse.
"""

import os
import sys
import shutil
import subprocess

red = "\033[1;31m"
green = "\033[1;32m"
yellow = "\033[1;33m"
reset = "\033[0m"

RED = red
GREEN = green
YELLOW = yellow
RESET = reset

SCRIPT_NAME = 'main.py'
MODULE_NAME = 'FARHAN-Shot'
BIN_NAME = 'FARHAN-Shot'

def is_termux():
    return os.getenv("PREFIX", "").startswith("/data/data/com.termux/files/usr")

def print_info(msg):
    print(f"{green}[+]{reset} {msg}")

def print_warn(msg):
    print(f"{yellow}[!]{reset} {msg}")

def print_error(msg):
    print(f"{red}[-]{reset} {msg}")

def install_script():
    if not is_termux():
        print_warn("You don't appear to be running inside Termux. Paths may be incorrect.")
        sys.exit(1)

    prefix = sys.prefix
    python_version = f"python{sys.version_info.major}.{sys.version_info.minor}"

    bin_path = os.path.join(prefix, 'bin', BIN_NAME)
    lib_dir = os.path.join(prefix, 'lib', python_version)
    lib_path = os.path.join(lib_dir, SCRIPT_NAME)

    launcher_code = f'''#!/data/data/com.termux/files/usr/bin/python3
import runpy
if __name__ == "__main__":
    runpy.run_path("{lib_path}", run_name="__main__")
'''

    try:
        os.makedirs(os.path.join(prefix, 'bin'), exist_ok=True)
        with open(bin_path, 'w') as f:
            f.write(launcher_code)
        os.chmod(bin_path, 0o775)
        print_info(f"Launcher script installed at {bin_path}")

        assets_dir = os.path.dirname(os.path.realpath(__file__))
        repo_dir = os.path.abspath(os.path.join(assets_dir, '..'))

        # Copy main.py to lib
        main_src = os.path.join(repo_dir, 'main.py')
        if os.path.exists(main_src):
            shutil.copy2(main_src, lib_path)
            print_info(f"Copied main.py to {lib_path}")

        # Copy assets folder to lib/assets
        dst_assets = os.path.join(lib_dir, 'assets')
        os.makedirs(dst_assets, exist_ok=True)
        for item in os.listdir(assets_dir):
            s = os.path.join(assets_dir, item)
            d = os.path.join(dst_assets, item)
            if os.path.isfile(s):
                shutil.copy2(s, d)
                print_info(f"Copied asset {item} to {d}")

        print_info(f"Installed successfully! Run the tool with: {BIN_NAME}")
        print_info("Showing usage:\n")

        subprocess.run([bin_path, '--help'], check=False)
    except Exception as e:
        print_error(f"Installation failed: {e}")

def uninstall_script():
    prefix = sys.prefix
    python_version = f"python{sys.version_info.major}.{sys.version_info.minor}"

    bin_path = os.path.join(prefix, 'bin', BIN_NAME)
    lib_dir = os.path.join(prefix, 'lib', python_version)
    lib_path = os.path.join(lib_dir, SCRIPT_NAME)
    dst_assets = os.path.join(lib_dir, 'assets')

    for path in [bin_path, lib_path]:
        try:
            os.remove(path)
            print_info(f"Removed: {path}")
        except FileNotFoundError:
            print_warn(f"File not found, skipping: {path}")
        except Exception as e:
            print_error(f"Error removing {path}: {e}")

    if os.path.isdir(dst_assets):
        try:
            shutil.rmtree(dst_assets)
            print_info(f"Removed assets directory: {dst_assets}")
        except Exception as e:
            print_error(f"Error removing assets: {e}")

def main():
    if len(sys.argv) != 2:
        print(f"{yellow}Usage: python3 assets/setup.py [install | uninstall]{reset}")
        sys.exit(1)

    cmd = sys.argv[1].lower()
    if cmd == 'install':
        install_script()
    elif cmd == 'uninstall':
        uninstall_script()
    else:
        print_error("Unknown command. Use 'install' or 'uninstall'.")

if __name__ == '__main__':
    main()
