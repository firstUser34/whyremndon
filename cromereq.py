import os
import subprocess
import sys
import zipfile
import shutil
import platform
import requests

def run_cmd(command, shell=True):
    try:
        print(f"\n⚙️ Running: {command}")
        subprocess.check_call(command, shell=shell)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running: {command}\n{e}")
        sys.exit(1)

def install_chrome():
    print("\n🔍 Checking if Google Chrome is installed...")
    result = shutil.which("google-chrome") or shutil.which("chrome") or shutil.which("chromium")
    if result:
        print(f"✅ Chrome already installed: {result}")
        return

    print("📦 Installing Google Chrome...")
    run_cmd("wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -O chrome.deb")
    run_cmd("sudo apt-get update -y")
    run_cmd("sudo apt-get install -y ./chrome.deb || sudo apt-get -f install -y")

def get_chrome_version():
    try:
        version_output = subprocess.check_output(["google-chrome", "--version"]).decode()
        print(f"🌐 Chrome Version: {version_output.strip()}")
        version_number = version_output.strip().split()[2]
        major_version = version_number.split('.')[0]
        return version_number, major_version
    except Exception as e:
        print("❌ Could not determine Chrome version:", e)
        sys.exit(1)

def install_chromedriver(chrome_version, major_version):
    print("🔍 Installing matching ChromeDriver...")

    try:
        # Construct download URL
        base_url = f"https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/{chrome_version}/linux64/chromedriver-linux64.zip"
        zip_path = "chromedriver.zip"

        print(f"⬇️ Downloading from: {base_url}")
        response = requests.get(base_url, stream=True)
        if response.status_code != 200:
            raise Exception(f"Download failed with status code {response.status_code}")
        
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        # Unzip
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall("chromedriver-temp")

        # Move to PATH
        run_cmd("sudo mv chromedriver-temp/chromedriver /usr/local/bin/")
        run_cmd("sudo chmod +x /usr/local/bin/chromedriver")

        print("✅ ChromeDriver installed successfully.")
        os.remove(zip_path)
        shutil.rmtree("chromedriver-temp")

    except Exception as e:
        print("❌ Failed to install ChromeDriver:", e)
        sys.exit(1)

def main():
    print("🖥️ Detecting platform:", platform.system(), platform.platform())
    
    if not shutil.which("sudo"):
        print("❌ 'sudo' not found. Please run as a user with sudo privileges.")
        sys.exit(1)

    print("🔄 Updating system packages...")
    run_cmd("sudo apt-get update -y && sudo apt-get upgrade -y")

    install_chrome()
    chrome_version, major_version = get_chrome_version()
    install_chromedriver(chrome_version, major_version)

    print("\n🎉 All done! Chrome + ChromeDriver installed and ready.")

if __name__ == "__main__":
    main()
