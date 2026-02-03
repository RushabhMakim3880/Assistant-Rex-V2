from ..system import SystemControl

class PrivEscModule:
    """
    Handles Privilege Escalation enumeration.
    """
    def __init__(self, system_control):
        self.system = system_control

    def enum_suid(self):
        """
        Finds SUID binaries.
        find / -perm -u=s -type f 2>/dev/null
        """
        return self.system.execute("find / -perm -u=s -type f 2>/dev/null")

    def check_kernel_version(self):
        return self.system.execute("uname -a")
