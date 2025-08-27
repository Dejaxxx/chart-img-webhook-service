#!/usr/bin/env python3
"""
Validation script for Chart-IMG Production Setup
Checks that all necessary files and configurations are in place
"""

import os
import sys
import json

def validate_setup():
    """Validate the Chart-IMG production setup"""
    
    print("=" * 60)
    print("   CHART-IMG PRODUCTION SETUP VALIDATION")
    print("=" * 60)
    
    errors = []
    warnings = []
    
    # Check current directory
    current_dir = os.getcwd()
    expected_dir = "/Users/abdulaziznahas/trading-factory/chart-img-production"
    
    print(f"\n📂 Checking Directory...")
    if current_dir != expected_dir:
        warnings.append(f"Not in production directory. Run: cd {expected_dir}")
    else:
        print(f"   ✅ In correct directory")
    
    # Check required files
    print(f"\n📄 Checking Required Files...")
    required_files = [
        'chart_img_service_v7_hybrid.py',
        'start_chart_service.sh',
        'chart_requirements.txt',
        'CHART_IMG_DEFINITIVE_README.md',
        'QUICK_START.txt',
        'test_chart_final.py'
    ]
    
    for file in required_files:
        filepath = os.path.join(expected_dir, file)
        if os.path.exists(filepath):
            print(f"   ✅ {file}")
        else:
            errors.append(f"Missing file: {file}")
            print(f"   ❌ {file} - MISSING")
    
    # Check output directory
    print(f"\n📊 Checking Output Directory...")
    output_dir = "/Users/abdulaziznahas/chart-img-outputs"
    if os.path.exists(output_dir):
        print(f"   ✅ Output directory exists")
        # Check if writable
        test_file = os.path.join(output_dir, ".write_test")
        try:
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            print(f"   ✅ Output directory is writable")
        except:
            errors.append(f"Output directory not writable: {output_dir}")
            print(f"   ❌ Output directory not writable")
    else:
        warnings.append(f"Output directory doesn't exist. It will be created on first run.")
        print(f"   ⚠️  Output directory doesn't exist (will be created)")
    
    # Check Python version
    print(f"\n🐍 Checking Python Version...")
    python_version = sys.version_info
    if python_version.major >= 3 and python_version.minor >= 9:
        print(f"   ✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        errors.append(f"Python 3.9+ required. Current: {python_version.major}.{python_version.minor}")
        print(f"   ❌ Python 3.9+ required")
    
    # Check if service is already running
    print(f"\n🔌 Checking Port 5002...")
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 5002))
    sock.close()
    
    if result == 0:
        print(f"   ⚠️  Port 5002 is already in use (service may be running)")
        warnings.append("Port 5002 is already in use. Kill existing service if needed.")
    else:
        print(f"   ✅ Port 5002 is available")
    
    # Check executable permissions
    print(f"\n🔧 Checking Permissions...")
    scripts = ['start_chart_service.sh', 'test_chart_final.py']
    for script in scripts:
        filepath = os.path.join(expected_dir, script)
        if os.path.exists(filepath):
            if os.access(filepath, os.X_OK):
                print(f"   ✅ {script} is executable")
            else:
                warnings.append(f"{script} is not executable. Run: chmod +x {script}")
                print(f"   ⚠️  {script} not executable")
    
    # Summary
    print("\n" + "=" * 60)
    print("                    VALIDATION SUMMARY")
    print("=" * 60)
    
    if not errors and not warnings:
        print("\n🎉 PERFECT! Everything is set up correctly!")
        print("\n📚 Quick Start Commands:")
        print("   cd /Users/abdulaziznahas/trading-factory/chart-img-production")
        print("   ./start_chart_service.sh")
        print("   open http://localhost:5002/test/NVDA")
        return True
    else:
        if errors:
            print(f"\n❌ ERRORS FOUND ({len(errors)}):")
            for error in errors:
                print(f"   • {error}")
        
        if warnings:
            print(f"\n⚠️  WARNINGS ({len(warnings)}):")
            for warning in warnings:
                print(f"   • {warning}")
        
        print("\n📋 Next Steps:")
        if errors:
            print("   1. Fix the errors above")
        if warnings:
            print("   2. Address warnings if needed")
        print("   3. Run this validation again")
        
        return False

if __name__ == "__main__":
    success = validate_setup()
    sys.exit(0 if success else 1)
