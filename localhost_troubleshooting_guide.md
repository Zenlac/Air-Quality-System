# Localhost Error Troubleshooting Guide

## 🚨 Common Localhost Error Scenarios & Solutions

When running `python run_ui.py` or `streamlit run app.py`, you might encounter localhost-related errors. Here's how to diagnose and fix them:

---

## **Scenario 1: Port Already in Use**

### **Error Messages:**
```
Port 8501 is already in use
Address already in use
OSError: [Errno 98] Address already in use
```

### **Solutions:**

#### **Option A: Kill Existing Process**
```bash
# Windows
netstat -ano | findstr :8501
taskkill /PID <PID_NUMBER> /F

# macOS/Linux
lsof -ti:8501 | xargs kill -9
# OR
sudo lsof -ti:8501 | xargs kill -9
```

#### **Option B: Use Different Port**
```bash
# Method 1: Modify run_ui.py temporarily
# Change line 41 to: "--server.port", "8502",

# Method 2: Run directly with different port
streamlit run app.py --server.port 8502

# Method 3: Create alternative launcher
python -c "
import subprocess
import sys
subprocess.run([sys.executable, '-m', 'streamlit', 'run', 'app.py', '--server.port', '8502'])
"
```

---

## **Scenario 2: Connection Refused**

### **Error Messages:**
```
Connection refused
ERR_CONNECTION_REFUSED
Unable to connect to localhost:8501
```

### **Solutions:**

#### **Check if Server is Running**
```bash
# Check if port 8501 is listening
netstat -an | findstr :8501  # Windows
netstat -an | grep :8501     # macOS/Linux
lsof -i :8501                # macOS/Linux
```

#### **Restart the Server**
```bash
# Stop current server (Ctrl+C in terminal)
# Then restart
python run_ui.py
```

#### **Check Firewall/Antivirus**
- Temporarily disable firewall/antivirus
- Add Python/Streamlit to firewall exceptions
- Check if corporate network blocks localhost connections

---

## **Scenario 3: Address Not Available**

### **Error Messages:**
```
OSError: [Errno 99] Cannot assign requested address
Address not available
Failed to bind to localhost
```

### **Solutions:**

#### **Use 0.0.0.0 Instead of localhost**
```bash
# Method 1: Modify run_ui.py
# Change line 42 to: "--server.address", "0.0.0.0",

# Method 2: Run directly
streamlit run app.py --server.address 0.0.0.0

# Method 3: Use IP address
streamlit run app.py --server.address 127.0.0.1
```

#### **Check Network Configuration**
```bash
# Check if localhost resolves
ping localhost
ping 127.0.0.1

# Check hosts file (Windows: C:\Windows\System32\drivers\etc\hosts)
# Should contain: 127.0.0.1 localhost
```

---

## **Scenario 4: Browser Issues**

### **Error Messages:**
```
Page not found
404 Not Found
This site can't be reached
```

### **Solutions:**

#### **Try Different URLs**
```
http://localhost:8501
http://127.0.0.1:8501
http://0.0.0.0:8501
```

#### **Clear Browser Cache**
- Clear cache and cookies for localhost
- Try incognito/private mode
- Try different browser (Chrome, Firefox, Edge, Safari)

#### **Check Browser Console**
- Press F12 → Console tab
- Look for JavaScript errors
- Check Network tab for failed requests

---

## **Scenario 5: Python/Environment Issues**

### **Error Messages:**
```
ModuleNotFoundError: No module named 'streamlit'
Permission denied
Python not found
```

### **Solutions:**

#### **Verify Installation**
```bash
# Check Python
python --version
python -c "import sys; print(sys.executable)"

# Check Streamlit
python -c "import streamlit; print(streamlit.__version__)"

# Reinstall if needed
pip install streamlit>=1.28.0
```

#### **Check Virtual Environment**
```bash
# Check if in venv
python -c "import sys; print(sys.prefix)"

# Activate venv properly
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

#### **Check File Permissions**
```bash
# Check app.py exists and is readable
ls -la app.py          # macOS/Linux
dir app.py             # Windows

# Check directory permissions
ls -la .               # macOS/Linux
dir                    # Windows
```

---

## **Scenario 6: System Resource Issues**

### **Error Messages:**
```
Memory error
Out of memory
System resource exhausted
```

### **Solutions:**

#### **Check System Resources**
```bash
# Check memory usage
# Windows
tasklist | findstr python
wmic OS get TotalVisibleMemorySize,FreePhysicalMemory

# macOS/Linux
free -h
top | grep python
ps aux | grep python
```

#### **Close Other Applications**
- Close browser tabs
- Close other Python processes
- Restart computer if needed

---

## **🔧 Advanced Troubleshooting**

### **Diagnostic Script**
Create `diagnose_localhost.py`:

```python
#!/usr/bin/env python3
import socket
import subprocess
import sys
import os

def diagnose_localhost():
    print("🔍 Localhost Diagnosis Tool")
    print("=" * 50)
    
    # Test 1: Check localhost resolution
    try:
        socket.gethostbyname('localhost')
        print("✅ Localhost resolves correctly")
    except socket.gaierror:
        print("❌ Localhost resolution failed")
    
    # Test 2: Check port availability
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 8501))
    sock.close()
    
    if result == 0:
        print("❌ Port 8501 is already in use")
        # Find what's using it
        try:
            if sys.platform == 'win32':
                result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
                lines = result.stdout.split('\n')
                for line in lines:
                    if ':8501' in line and 'LISTENING' in line:
                        parts = line.split()
                        if len(parts) >= 5:
                            pid = parts[-1]
                            print(f"   Process ID using port: {pid}")
                            # Get process name
                            try:
                                proc_result = subprocess.run(['tasklist', '/FI', f'PID eq {pid}'], capture_output=True, text=True)
                                print(f"   Process: {proc_result.stdout}")
                            except:
                                pass
            else:
                result = subprocess.run(['lsof', '-i', ':8501'], capture_output=True, text=True)
                if result.stdout:
                    print(f"   Process using port: {result.stdout}")
        except Exception as e:
            print(f"   Could not identify process: {e}")
    else:
        print("✅ Port 8501 is available")
    
    # Test 3: Check Streamlit installation
    try:
        import streamlit
        print(f"✅ Streamlit {streamlit.__version__} installed")
    except ImportError:
        print("❌ Streamlit not installed")
    
    # Test 4: Check app.py exists
    app_path = 'app.py'
    if os.path.exists(app_path):
        print(f"✅ {app_path} found")
        if os.access(app_path, os.R_OK):
            print("✅ {app_path} is readable")
        else:
            print("❌ {app_path} is not readable")
    else:
        print(f"❌ {app_path} not found")

if __name__ == "__main__":
    diagnose_localhost()
```

### **Alternative Launcher Script**
Create `run_ui_alternative.py`:

```python
#!/usr/bin/env python3
import subprocess
import sys
import socket
import time

def find_free_port(start_port=8501, max_port=8600):
    """Find a free port in the given range"""
    for port in range(start_port, max_port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        if result != 0:
            return port
    return None

def main():
    print("🚀 Alternative UI Launcher")
    print("=" * 50)
    
    # Find free port
    port = find_free_port()
    if not port:
        print("❌ No free ports available in range 8501-8600")
        sys.exit(1)
    
    print(f"📍 Using port: {port}")
    
    # Try different addresses
    addresses = ['localhost', '127.0.0.1', '0.0.0.0']
    
    for address in addresses:
        try:
            print(f"🔄 Trying address: {address}")
            
            # Launch streamlit
            process = subprocess.Popen([
                sys.executable, "-m", "streamlit", "run", "app.py",
                "--server.port", str(port),
                "--server.address", address,
                "--browser.gatherUsageStats", "false"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait a moment to see if it starts
            time.sleep(3)
            
            if process.poll() is None:
                print(f"✅ Server started successfully!")
                print(f"🌐 URL: http://{address}:{port}")
                print("Press Ctrl+C to stop the server")
                
                # Wait for user to stop
                try:
                    process.wait()
                except KeyboardInterrupt:
                    print("\n🛑 Stopping server...")
                    process.terminate()
                    process.wait()
                return
            else:
                # Process failed, get error
                stdout, stderr = process.communicate()
                print(f"❌ Failed with address {address}:")
                if stderr:
                    print(stderr.decode())
                process.terminate()
                
        except Exception as e:
            print(f"❌ Error with address {address}: {e}")
    
    print("❌ All addresses failed. Manual troubleshooting required.")

if __name__ == "__main__":
    main()
```

---

## **📋 Quick Fix Checklist**

### **Immediate Steps:**
1. **Stop all Python processes** (Ctrl+C in terminals)
2. **Check for port conflicts**: `netstat -an | findstr :8501`
3. **Try different port**: `streamlit run app.py --server.port 8502`
4. **Try different address**: `streamlit run app.py --server.address 127.0.0.1`
5. **Clear browser cache** and try incognito mode
6. **Try different browser**

### **If Still Failing:**
1. **Run diagnostic script**: `python diagnose_localhost.py`
2. **Use alternative launcher**: `python run_ui_alternative.py`
3. **Check firewall/antivirus settings**
4. **Restart computer** (last resort)

### **Prevention Tips:**
1. **Always stop server properly** (Ctrl+C)
2. **Use consistent port** (avoid port conflicts)
3. **Keep browser updated**
4. **Maintain clean Python environment**

---

## **🆘 When to Get Help**

Contact support if:
- All troubleshooting steps fail
- Error messages are not listed here
- Issue persists after computer restart
- Multiple users experience same issue

**Include in support request:**
- Full error message
- Operating system and version
- Python and Streamlit versions
- Steps already tried
- Output from diagnostic script

---

*This guide covers the most common localhost issues. For specific error messages not covered here, run the diagnostic script and include the output in your support request.*
