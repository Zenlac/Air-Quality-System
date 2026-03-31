#!/usr/bin/env python3
"""
Localhost Diagnosis Tool
Diagnoses common localhost connection issues for the Air Pollution Forecasting System
"""

import socket
import subprocess
import sys
import os
import platform

def diagnose_localhost():
    print("🔍 Localhost Diagnosis Tool")
    print("=" * 50)
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version}")
    print("=" * 50)
    
    issues_found = []
    
    # Test 1: Check localhost resolution
    print("\n📍 Test 1: Localhost Resolution")
    try:
        localhost_ip = socket.gethostbyname('localhost')
        print(f"✅ Localhost resolves to: {localhost_ip}")
    except socket.gaierror as e:
        print(f"❌ Localhost resolution failed: {e}")
        issues_found.append("Localhost resolution failed")
    
    # Test 2: Check port availability
    print("\n📍 Test 2: Port 8501 Availability")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 8501))
    sock.close()
    
    if result == 0:
        print("❌ Port 8501 is already in use")
        issues_found.append("Port 8501 already in use")
        
        # Find what's using it
        print("   🔍 Finding process using port 8501...")
        try:
            if platform.system() == 'Windows':
                result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
                lines = result.stdout.split('\n')
                for line in lines:
                    if ':8501' in line and 'LISTENING' in line:
                        parts = line.split()
                        if len(parts) >= 5:
                            pid = parts[-1]
                            print(f"   📋 Process ID using port: {pid}")
                            # Get process name
                            try:
                                proc_result = subprocess.run(['tasklist', '/FI', f'PID eq {pid}'], capture_output=True, text=True)
                                proc_lines = proc_result.stdout.split('\n')
                                for proc_line in proc_lines:
                                    if pid in proc_line and 'python' in proc_line.lower():
                                        print(f"   🐍 Python process: {proc_line.strip()}")
                                        break
                            except Exception as e:
                                print(f"   ⚠️ Could not get process details: {e}")
            else:
                # macOS/Linux
                try:
                    result = subprocess.run(['lsof', '-i', ':8501'], capture_output=True, text=True)
                    if result.stdout:
                        print(f"   📋 Process using port:")
                        for line in result.stdout.split('\n'):
                            if 'LISTEN' in line:
                                print(f"   {line}")
                except FileNotFoundError:
                    print("   ⚠️ lsof command not available")
                except Exception as e:
                    print(f"   ⚠️ Could not identify process: {e}")
        except Exception as e:
            print(f"   ⚠️ Could not identify process: {e}")
    else:
        print("✅ Port 8501 is available")
    
    # Test 3: Check Streamlit installation
    print("\n📍 Test 3: Streamlit Installation")
    try:
        import streamlit
        print(f"✅ Streamlit {streamlit.__version__} installed")
        
        # Check version compatibility
        version_parts = streamlit.__version__.split('.')
        major = int(version_parts[0])
        minor = int(version_parts[1])
        
        if major > 1 or (major == 1 and minor >= 28):
            print("✅ Streamlit version is compatible (>= 1.28.0)")
        else:
            print("⚠️ Streamlit version may be too old (< 1.28.0)")
            issues_found.append("Streamlit version too old")
    except ImportError:
        print("❌ Streamlit not installed")
        issues_found.append("Streamlit not installed")
    
    # Test 4: Check app.py exists and is readable
    print("\n📍 Test 4: Application Files")
    app_path = 'app.py'
    if os.path.exists(app_path):
        print(f"✅ {app_path} found")
        if os.access(app_path, os.R_OK):
            print(f"✅ {app_path} is readable")
            # Check file size
            size = os.path.getsize(app_path)
            print(f"📊 File size: {size:,} bytes")
        else:
            print(f"❌ {app_path} is not readable")
            issues_found.append(f"{app_path} not readable")
    else:
        print(f"❌ {app_path} not found")
        issues_found.append(f"{app_path} not found")
    
    # Test 5: Check run_ui.py exists
    run_ui_path = 'run_ui.py'
    if os.path.exists(run_ui_path):
        print(f"✅ {run_ui_path} found")
    else:
        print(f"❌ {run_ui_path} not found")
        issues_found.append(f"{run_ui_path} not found")
    
    # Test 6: Check network interfaces
    print("\n📍 Test 6: Network Interfaces")
    try:
        # Test different addresses
        addresses = ['localhost', '127.0.0.1']
        for addr in addresses:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((addr, 80))  # Test with a common port
                sock.close()
                if result == 0:
                    print(f"✅ {addr} is reachable")
                else:
                    print(f"⚠️ {addr} may have connectivity issues")
            except Exception as e:
                print(f"❌ {addr} test failed: {e}")
    except Exception as e:
        print(f"⚠️ Network interface test failed: {e}")
    
    # Test 7: Check browser availability
    print("\n📍 Test 7: Browser Availability")
    browsers = []
    if platform.system() == 'Windows':
        # Check for common browsers on Windows
        browser_paths = [
            'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
            'C:\\Program Files\\Mozilla Firefox\\firefox.exe',
            'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe'
        ]
        for path in browser_paths:
            if os.path.exists(path):
                browsers.append(os.path.basename(path))
    elif platform.system() == 'Darwin':  # macOS
        browser_commands = ['chrome', 'firefox', 'safari']
        for cmd in browser_commands:
            try:
                subprocess.run(['which', cmd], capture_output=True, check=True)
                browsers.append(cmd)
            except:
                pass
    else:  # Linux
        browser_commands = ['google-chrome', 'firefox', 'chromium']
        for cmd in browser_commands:
            try:
                subprocess.run(['which', cmd], capture_output=True, check=True)
                browsers.append(cmd)
            except:
                pass
    
    if browsers:
        print(f"✅ Browsers found: {', '.join(browsers)}")
    else:
        print("⚠️ No common browsers detected")
        issues_found.append("No browsers detected")
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 DIAGNOSIS SUMMARY")
    print("=" * 50)
    
    if issues_found:
        print(f"❌ Issues found ({len(issues_found)}):")
        for i, issue in enumerate(issues_found, 1):
            print(f"   {i}. {issue}")
        
        print("\n🔧 RECOMMENDED ACTIONS:")
        if "Port 8501 already in use" in issues_found:
            print("   • Kill existing Python processes or use different port")
        if "Streamlit not installed" in issues_found:
            print("   • Install Streamlit: pip install streamlit>=1.28.0")
        if "app.py not found" in issues_found:
            print("   • Ensure you're in the correct directory")
        if "Localhost resolution failed" in issues_found:
            print("   • Check hosts file and network configuration")
        
        print("\n📖 For detailed solutions, see: localhost_troubleshooting_guide.md")
    else:
        print("✅ No critical issues detected!")
        print("🚀 Try running: python run_ui.py")
        print("   If still fails, try: python run_ui_alternative.py")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    try:
        diagnose_localhost()
    except KeyboardInterrupt:
        print("\n\n⏹️ Diagnosis interrupted by user")
    except Exception as e:
        print(f"\n\n💥 Diagnosis tool failed: {e}")
        print("Please report this issue to support")
