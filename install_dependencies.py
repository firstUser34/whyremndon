#!/usr/bin/env python3
"""
Dependency installer for Ultimate X Visitor Bot
"""

import os
import sys
import subprocess
import platform

def print_step(message):
    """Print a step message"""
    print(f"\n{'='*60}\n{message}\n{'='*60}")

def run_command(command, ignore_errors=False):
    """Run a shell command and return result"""
    print(f"Running: {' '.join(command)}")
    try:
        result = subprocess.run(command, check=not ignore_errors, 
                               capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return result.returncode == 0
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def install_pip_packages():
    """Install required pip packages"""
    print_step("Installing Python dependencies")
    packages = ["requests", "selenium", "fake-useragent"]
    
    # Check if pip is available
    if run_command([sys.executable, "-m", "pip", "--version"], ignore_errors=True):
        run_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        run_command([sys.executable, "-m", "pip", "install"] + packages)
    else:
        print("pip not available. Please install pip first.")
        return False
    
    return True

def install_chrome_linux():
    """Install Chrome and ChromeDriver on Linux"""
    print_step("Installing Chrome and ChromeDriver on Linux")
    
    # Check if we're on Replit
    if os.path.exists("/home/runner"):
        print("Detected Replit environment")
        try:
            # Try to install via nix
            run_command(["nix-env", "-iA", "nixpkgs.chromium"], ignore_errors=True)
            run_command(["nix-env", "-iA", "nixpkgs.chromedriver"], ignore_errors=True)
            return True
        except:
            print("Failed to install via nix-env")
    
    # Try apt-get for Debian/Ubuntu
    if os.path.exists("/usr/bin/apt-get"):
        run_command(["apt-get", "update"], ignore_errors=True)
        run_command(["apt-get", "install", "-y", "chromium-browser", "chromium-driver"], ignore_errors=True)
        return True
    
    # Try yum for CentOS/RHEL
    if os.path.exists("/usr/bin/yum"):
        run_command(["yum", "install", "-y", "chromium", "chromedriver"], ignore_errors=True)
        return True
    
    print("Could not install Chrome automatically. Please install Chrome and ChromeDriver manually.")
    return False

def main():
    """Main installer function"""
    print_step("Ultimate X Visitor Bot - Dependency Installer")
    
    # Install pip packages
    pip_success = install_pip_packages()
    
    # Install system dependencies based on platform
    system = platform.system().lower()
    if system == "linux":
        chrome_success = install_chrome_linux()
    else:
        print(f"Automatic Chrome installation not supported on {system}.")
        print("Please install Chrome and ChromeDriver manually.")
        chrome_success = False
    
    print_step("Installation Summary")
    print(f"Python packages: {'✅ Installed' if pip_success else '❌ Failed'}")
    print(f"Chrome/ChromeDriver: {'✅ Attempted' if chrome_success else '❌ Not installed'}")
    print("\nYou can now run the bot with: python ultimate_x_visitor.py")
    
    if not chrome_success:
        print("\nNote: Browser automation will be disabled without Chrome/ChromeDriver.")
        print("The bot will still work using HTTP requests only.")

if __name__ == "__main__":
    main()
