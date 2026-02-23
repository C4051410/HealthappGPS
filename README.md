# 📍 Live GPS & Map Tracker

A Python desktop and mobile application built with [Flet](https://flet.dev). It tracks your real-time GPS location, calculates the distance travelled using the Haversine formula, and visualizes your route on an interactive CartoDB map.

---

## 🛠️ 1. Initial System Setup (Windows)

If you are starting completely from scratch and don't have Git installed, open your terminal (PowerShell or command prompt) and run:

```bash
# Install Git using the Windows Package Manager
winget install Git.Git

# Verify the installation (Restart your terminal first!)
git --version

# Initialize a new, empty Git repository
git init

# Add all your project files to the staging area
git add .

# Save your first version
git commit -m "Initial commit: Added Flet map and GPS tracker"

# Create a virtual environment named '.venv'
python -m venv .venv

# Activate the virtual environment (Windows)
.venv\Scripts\activate

# Activate the virtual environment (Mac/Linux)
source .venv/bin/activate

# Save your currently installed libraries to a file
pip freeze > requirements.txt

flet run main.py

# For Android devices
flet run --android

# For iOS devices
flet run --ios

# If the connection fails, force Flet to use your specific IP address:
flet run --android --host <YOUR_IP_ADDRESS>
