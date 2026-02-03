import subprocess
import logging

class NetworkControl:
    """
    Handles Network-level automation: Interfaces, MAC Spoofing, Monitor Mode, Firewall.
    """
    def __init__(self):
        self.logger = logging.getLogger("NetworkControl")

    def execute(self, cmd):
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                return False, result.stderr.strip()
            return True, result.stdout.strip()
        except Exception as e:
            return False, str(e)

    # --- Interface Control ---
    def set_interface_state(self, interface, state):
        """state: up, down"""
        return self.execute(f"ip link set {interface} {state}")

    def change_mac(self, interface, new_mac=None):
        """
        Uses macchanger.
        If new_mac is None, uses -r (random).
        """
        # 1. Down
        self.set_interface_state(interface, "down")
        
        # 2. Change
        if new_mac:
            cmd = f"macchanger -m {new_mac} {interface}"
        else:
            cmd = f"macchanger -r {interface}"
        success, out = self.execute(cmd)
        
        # 3. Up
        self.set_interface_state(interface, "up")
        
        return success, out

    def set_monitor_mode(self, interface, enable=True):
        """
        Uses airmon-ng usually, or iwconfig.
        airmon-ng is safer for Kali.
        """
        action = "start" if enable else "stop"
        return self.execute(f"airmon-ng {action} {interface}")

    # --- Firewall (basic ufw/iptables wrapper) ---
    def rule_control(self, action, port, protocol="tcp", direction="allow"):
        """
        Wrapper for UFW (Uncomplicated Firewall).
        action: add, delete (mapped to ufw allow/deny)
        """
        # ufw allow 80/tcp
        if direction not in ["allow", "deny", "reject"]:
            return False, "Invalid direction"
        
        cmd = f"ufw {direction} {port}/{protocol}"
        if action == "delete":
            cmd = f"ufw delete {direction} {port}/{protocol}"
            
        return self.execute(cmd)
