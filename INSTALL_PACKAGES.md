# 🚀 QUICK INSTALLATION GUIDE

## ⚠️ YOU NEED TO INSTALL PACKAGES FIRST!

The frontend is missing `react-router-dom` and `lucide-react` packages.

---

## ✅ Option 1: Run the Installation Script (EASIEST)

1. **Navigate to:**
   ```
   c:\Users\Vaibhav Somanna\Desktop\DrMartens\frontend
   ```

2. **Double-click:**
   ```
   install-packages.bat
   ```

3. **Wait for installation to complete** (30-60 seconds)

4. **Restart frontend:**
   ```powershell
   npm run dev
   ```

---

## ✅ Option 2: Manual Installation

### Open CMD (NOT PowerShell):

1. Press `Win + R`
2. Type: `cmd`
3. Press Enter

### Run these commands:

```cmd
cd /d "c:\Users\Vaibhav Somanna\Desktop\DrMartens\frontend"
npm install react-router-dom lucide-react
```

### Then restart:
```cmd
npm run dev
```

---

## ✅ Option 3: Use Node.js Directly

```powershell
cd "c:\Users\Vaibhav Somanna\Desktop\DrMartens\frontend"
& "C:\Program Files\nodejs\npm.cmd" install react-router-dom lucide-react
npm run dev
```

---

## 📦 What Gets Installed:

- **react-router-dom** (v6.x) - For navigation between pages
- **lucide-react** (latest) - For beautiful icons (MapPin, ShoppingBag, etc.)

---

## ✅ After Installation:

You should see in `package.json`:
```json
"dependencies": {
  "axios": "^1.6.2",
  "react": "^18.3.1",
  "react-dom": "^18.3.1",
  "recharts": "^2.10.3",
  "react-router-dom": "^6.x.x",    ← NEW
  "lucide-react": "^0.x.x"         ← NEW
}
```

---

## 🎯 Then You Can Access:

1. **http://localhost:5173/** - Google Maps Reviews
2. **http://localhost:5173/combined** - Combined Analysis (Google + Amazon)

---

## 🆘 If Installation Fails:

### Clear npm cache:
```cmd
cd /d "c:\Users\Vaibhav Somanna\Desktop\DrMartens\frontend"
npm cache clean --force
npm install react-router-dom lucide-react
```

### Or delete node_modules and reinstall everything:
```cmd
cd /d "c:\Users\Vaibhav Somanna\Desktop\DrMartens\frontend"
rmdir /s /q node_modules
npm install
```

---

## 📝 Summary:

**Problem:** Frontend can't find `react-router-dom` and `lucide-react`

**Solution:** Install them with:
```cmd
npm install react-router-dom lucide-react
```

**Easiest Way:** Just double-click `install-packages.bat` in the frontend folder! 🎯
