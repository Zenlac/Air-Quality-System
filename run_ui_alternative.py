#!/usr/bin/env python3
"""
Alternative UI Launcher for Air Pollution Forecasting System
Automatically finds available ports and addresses to avoid localhost errors
"""

import subprocess
import sys
import socket
import time
import webbrowser
from urllib.parse import urljoin

def find_free_port(start_port=8501, max_port=8600):
    """Find a free port in the given range"""
    for port in range(start_port, max_port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        if result != 0:
            return port
    return None

def test_address(address, port):
    """Test if we can bind to the given address and port"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((address, port))
        sock.close()
        return result != 0  # Return True if port is free
    except:
        return False

def launch_streamlit(address, port):
    """Launch Streamlit with the given address and port"""
    print(f"🚀 Launching Streamlit on {address}:{port}")
    
    try:
        # Launch streamlit
        process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", str(port),
            "--server.address", address,
            "--browser.gatherUsageStats", "false",
            "--server.headless", "true"  # Don't auto-open browser
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Wait a moment to see if it starts successfully
        time.sleep(3)
        
        if process.poll() is None:
            # Process is still running, likely successful
            print(f"✅ Server started successfully!")
            print(f"🌐 URL: http://{address}:{port}")
            
            # Try to open browser
            try:
                url = f"http://{address}:{port}"
                webbrowser.open(url)
                print(f"🌐 Opening browser at {url}")
            except Exception as e:
                print(f"⚠️ Could not auto-open browser: {e}")
                print(f"   Please manually visit: http://{address}:{port}")
            
            return process
        else:
            # Process failed, get error
            stdout, stderr = process.communicate()
            print(f"❌ Failed to start server:")
            if stderr:
                print(f"   Error: {stderr.strip()}")
            if stdout:
                print(f"   Output: {stdout.strip()}")
            return None
            
    except Exception as e:
        print(f"❌ Error launching Streamlit: {e}")
        return None

def main():
    print("🔄 Alternative UI Launcher")
    print("=" * 50)
    print("This launcher will automatically find available ports and addresses")
    print("to help resolve localhost connection issues.")
    print("=" * 50)
    
    # Check if app.py exists
    if not os.path.exists('app.py'):
        print("❌ app.py not found in current directory")
        print("   Please ensure you're running this from the project root")
        sys.exit(1)
    
    # Find free port
    print("🔍 Searching for available port...")
    port = find_free_port()
    if not port:
        print("❌ No free ports available in range 8501-8600")
        print("   Please close some applications and try again")
        sys.exit(1)
    
    print(f"✅ Found available port: {port}")
    
    # Try different addresses in order of preference
    addresses = [
        ('localhost', 'Standard localhost'),
        ('127.0.0.1', 'Direct IP address'),
        ('0.0.0.0', 'All interfaces')
    ]
    
    print("\n🔄 Testing different addresses...")
    
    for address, description in addresses:
        print(f"\n📍 Trying: {address} ({description})")
        
        if not test_address(address, port):
            print(f"   ❌ Cannot bind to {address}:{port}")
            continue
        
        # Try to launch
        process = launch_streamlit(address, port)
        
        if process:
            print(f"\n🎉 SUCCESS! Server is running on http://{address}:{port}")
            print("\n📋 Instructions:")
            print(f"   • URL: http://{address}:{port}")
            print("   • Press Ctrl+C in this terminal to stop the server")
            print("   • The browser should open automatically")
            print("   • If not, manually visit the URL above")
            print("\n⏳ Waiting for you to stop the server...")
            
            try:
                # Wait for user to stop
                process.wait()
            except KeyboardInterrupt:
                print("\n\n🛑 Stopping server...")
                process.terminate()
                
                # Give it a moment to terminate gracefully
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    print("   Forcing termination...")
                    process.kill()
                
                print("✅ Server stopped")
            return
        else:
            print(f"   ❌ Failed with {address}")
    
    # If we get here, all attempts failed
    print("\n❌ All address attempts failed!")
    print("\n🔧 Troubleshooting suggestions:")
    print("   1. Run 'python diagnose_localhost.py' for detailed diagnosis")
    print("   2. Check firewall/antivirus settings")
    print("   3. Try restarting your computer")
    print("   4. See localhost_troubleshooting_guide.md for more help")
    
    print("\n📞 If issues persist, please contact support with:")
    print("   • Output from diagnose_localhost.py")
    print("   • Your operating system and Python version")
    print("   • Any error messages you see")

if __name__ == "__main__":
    import os  # Import here to avoid issues at module level
    main()
