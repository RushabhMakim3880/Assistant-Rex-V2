import shutil
from ..system import SystemControl

class ReconModule:
    """
    Handles Passive and Active Reconnaissance.
    """
    def __init__(self, system_control):
        self.system = system_control

    # --- Active Recon ---
    def run_nmap(self, target, scan_type="fast"):
        """
        scan_type: fast (-F), aggressive (-A), stealth (-sS), all (-p-)
        """
        options = "-F"
        if scan_type == "aggressive": options = "-A"
        elif scan_type == "stealth": options = "-sS"
        elif scan_type == "all": options = "-p- -T4"
        
        cmd = f"nmap {options} {target}"
        return self.system.execute(cmd)

    def enumerate_subdomains(self, domain):
        """
        Uses sublist3r or similar if available.
        """
        if shutil.which("sublist3r"):
            return self.system.execute(f"sublist3r -d {domain}")
        else:
            return False, "Sublist3r not installed."

    # --- Passive Recon ---
    def whois_lookup(self, domain):
        return self.system.execute(f"whois {domain}")
    
    def nslookup(self, domain):
        return self.system.execute(f"nslookup {domain}")
