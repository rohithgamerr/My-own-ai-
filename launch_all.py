
import os
import subprocess
import sys

# Set the root directory of the OS
root_dir = '/root/Lumina_OS'
os.environ['PYTHONPATH'] = root_dir

# Launch the AI Mind Server
subprocess.Popen([
    'python3', '-m', 'uvicorn', 'mind.main:app', 
    '--host', '0.0.0.0', '--port', '8000'
])

# Launch the Nexus Bot Server
subprocess.Popen([
    'python3', '-m', 'uvicorn', 'bot.main:app', 
    '--host', '0.0.0.0', '--port', '8001'
])

print("Lumina OS Servers are booting up with corrected paths...")

