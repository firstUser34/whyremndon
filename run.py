#!/usr/bin/env python3
"""
Runner script for Ultimate X Visitor Bot
"""

import os
import sys
import subprocess

def main():
    """Main runner function"""
    print("=" * 60)
    print("🚀 Ultimate X Visitor Bot - Runner")
    print("=" * 60)
    
    # Check if dependencies are installed
    try:
        import requests
        import selenium
    except ImportError:
        print("Dependencies not installed. Running installer first...")
        subprocess.run([sys.executable, "install_dependencies.py"])
    
    # Run the bot
    print("\nStarting the bot...")
    subprocess.run([sys.executable, "ultimate_x_visitor.py"])

if __name__ == "__main__":
    main()
