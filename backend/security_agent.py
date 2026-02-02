import subprocess
import platform
import os
import json

class SecurityAgent:
    def __init__(self):
        self.os_type = platform.system()
        print(f"[SecurityAgent] Initialized on {self.os_type}")

    def execute_command(self, command):
        """
        Executes a shell command safely.
        """
        try:
            # On Windows, use PowerShell; on Linux, use Bash/Sh
            shell = True
            executable = None
            if self.os_type == "Windows":
                 executable = "powershell.exe"
            else:
                 executable = "/bin/bash"

            print(f"[SecurityAgent] Executing: {command}")
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                executable=executable if self.os_type != "Windows" else None # Powershell via shell=True often defaults to cmd, but flexible
            )
            
            output = result.stdout
            if result.stderr:
                output += f"\n[STDERR]: {result.stderr}"
            
            return output.strip()
        except Exception as e:
            return f"Error executing command: {str(e)}"

    def run_nmap_scan(self, target, options="-F"):
        """
        Runs an Nmap scan on the target.
        Default options: -F (Fast scan)
        """
        # specialized wrapper to ensure nmap is installed
        check = self.execute_command("nmap --version")
        if "command not found" in check.lower() or "is not recognized" in check.lower():
            return "Error: 'nmap' is not installed or not in PATH."

        cmd = f"nmap {options} {target}"
        return self.execute_command(cmd)

    def run_netstat(self, options="-an"):
        """
        Runs netstat to see active connections.
        """
        cmd = f"netstat {options}"
        return self.execute_command(cmd)

    def run_whois(self, domain):
        """
        Runs whois lookup.
        """
        cmd = f"whois {domain}"
        return self.execute_command(cmd)
