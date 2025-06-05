#!/usr/bin/env python3
"""
Dependency installer for Ultimate X Visitor Bot (Debian/Ubuntu)
"""

import subprocess
import sys

def print_step(message):
    print(f"\n{'='*60}\n{message}\n{'='*60}")

def run_command(command, ignore_errors=False):
    print(f"Running: {' '.join(command)}")
    try:
        result = subprocess.run(command, check=not ignore_errors,
                                capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"Error: {e}")
        return False

def install_pip_packages():
    print_step("Installing Python dependencies")
    packages = ["requests", "selenium", "fake-useragent", "webdriver-manager"]

    if run_command([sys.executable, "-m", "pip", "--version"], ignore_errors=True):
        run_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        run_command([sys.executable, "-m", "pip", "install"] + packages)
        return True
    else:
        print("pip not found. Please install pip manually.")
        return False

def install_chrome_ubuntu():
    print_step("Installing Google Chrome and dependencies on Debian/Ubuntu")

    # Update package lists
    if not run_command(["sudo", "apt-get", "update", "-y"]):
        return False

    # Install dependencies for Chrome
    if not run_command(["sudo", "apt-get", "install", "-y", "wget", "gnupg", "ca-certificates"]):
        return False

    # Add Google Chrome's official GPG key and repo
    run_command(["wget", "-q", "-O", "-", "https://dl.google.com/linux/linux_signing_key.pub"], ignore_errors=True)
    run_command(["sudo", "apt-key", "add", "-"], ignore_errors=True)
    run_command([
        "sudo", "sh", "-c",
        "echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' >> /etc/apt/sources.list.d/google-chrome.list"
    ], ignore_errors=True)

    # Update package list again after adding repo
    if not run_command(["sudo", "apt-get", "update", "-y"]):
        return False

    # Install Google Chrome stable
    if not run_command(["sudo", "apt-get", "install", "-y", "google-chrome-stable"]):
        return False

    print("Google Chrome installed successfully!")
    return True

def main():
    print_step("Ultimate X Visitor Bot - Dependency Installer (Debian/Ubuntu)")

    pip_success = install_pip_packages()
    chrome_success = install_chrome_ubuntu()

    print_step("Installation Summary")
    print(f"Python packages: {'✅ Installed' if pip_success else '❌ Failed'}")
    print(f"Google Chrome: {'✅ Installed' if chrome_success else '❌ Failed or Not Installed'}")

    print("\nYou can now run the bot with: python ultimate_x_visitor.py")
    if not chrome_success:
        print("Warning: Chrome installation failed, browser automation might not work!")

if __name__ == "__main__":
    main()
