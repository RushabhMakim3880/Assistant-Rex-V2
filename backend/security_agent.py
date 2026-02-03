import platform
from security.system import SystemControl
from security.network import NetworkControl
from security.tool_manager import ToolManager
from security.context import ContextCollector
from security.advisor import SecurityAdvisor

# Attack Modules
from security.modules.recon import ReconModule
from security.modules.network_attacks import NetworkAttackModule
from security.modules.wireless import WirelessModule
from security.modules.web_attacks import WebAttackModule
from security.modules.credentials import CredentialModule
from security.modules.exploitation import ExploitModule
from security.modules.payloads import PayloadModule
from security.modules.post_exploit import PostExploitModule
from security.modules.privesc import PrivEscModule

class SecurityAgent:
    def __init__(self):
        self.os_type = platform.system()
        print(f"[SecurityAgent] Initialized on {self.os_type}")
        
        # Initialize Sub-Modules
        self.system = SystemControl()
        self.network = NetworkControl()
        self.tools = ToolManager()
        
        # The Brain
        self.context_collector = ContextCollector(self.system, self.network)
        self.advisor = SecurityAdvisor()
        
        # The Limbs
        self.recon = ReconModule(self.system)
        self.net_attack = NetworkAttackModule(self.system)
        self.wifi = WirelessModule(self.system)
        self.web = WebAttackModule(self.system)
        self.creds = CredentialModule(self.system)
        self.exploit = ExploitModule(self.system)
        self.payload = PayloadModule(self.system)
        self.post_exploit = PostExploitModule(self.system)
        self.priv_esc = PrivEscModule(self.system)

    def _check_platform(self):
        """
        Enforces Strict OS Policy.
        The full Cyber-REX suite is designed for Kali Linux.
        """
        if self.os_type == "Windows":
             return False, (
                 "⛔ **Access Denied**: The Cyber-REX Security Modules are strictly authorized for **Kali Linux** environments only.\n"
                 "Running offensive security tools on Windows is restricted to prevent system instability and policy violations.\n"
                 "Please switch to a Kali Linux instance to utilize these capabilities."
             )
        return True, "OK"

    def execute_command(self, command):
        """Legacy wrapper for raw shell execution via SystemControl."""
        # Note: shell commands themselves might be valid on windows if simple, 
        # but for this agent we lean towards restriction if it's being used for "Security"
        # However, for basic shell tool it might be annoying.
        # Let's keep execute_command open but restrict the *wrappers* below.
        success, output = self.system.execute(command)
        if not success:
            return f"Error: {output}"
        return output

    def get_advice(self, target_url=None):
        """
        High-level function to get AI security advice.
        """
        # Strict Check
        is_valid, msg = self._check_platform()
        if not is_valid: return {"error": msg}

        # 1. Collect Context
        sys_ctx = self.context_collector.get_system_context()
        web_ctx = {}
        if target_url:
            web_ctx = self.context_collector.analyze_web_target(target_url)
            
        # 2. Merge contexts (simplistic for now)
        full_ctx = {**sys_ctx, **web_ctx}
        target_type = "web" if target_url else "system"
        
        # 3. Get Advice
        advice = self.advisor.analyze_feasibility(full_ctx, target_type)
        return advice

    # --- Tool Wrappers (Recon Phase) ---
    def run_nmap_scan(self, target, options="-F"):
        # Strict Check
        is_valid, msg = self._check_platform()
        if not is_valid: return msg

        # Auto-install check
        if not self.tools.is_installed("nmap"):
            success, msg = self.tools.install_tool("nmap")
            if not success: return msg

        return self.execute_command(f"nmap {options} {target}")

    def run_netstat(self, options="-an"):
        # Netstat is a standard utility, we allow it on Windows for debugging connectivity
        if self.os_type == "Windows":
             return self.execute_command(f"netstat {options}")
        return self.execute_command(f"netstat {options}")

    def run_whois(self, domain):
         # Strict Check
         is_valid, msg = self._check_platform()
         if not is_valid: return msg

         if not self.tools.is_installed("whois"):
             if self.os_type != "Windows":
                 self.tools.install_tool("whois")
         
         return self.execute_command(f"whois {domain}")

