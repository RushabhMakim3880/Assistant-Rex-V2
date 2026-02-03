import psutil
import socket
import platform
# Optional: import requests for web context if needed active probing

class ContextCollector:
    """
    Aggregates context from the environment to inform the Feasibility Engine.
    """
    def __init__(self, system_control, network_control):
        self.system = system_control
        self.network = network_control

    def get_system_context(self):
        """
        Returns info about running processes, open ports, privilege level.
        """
        context = {
            "platform": platform.system().lower(),
            "privilege": "root" if self._is_root() else "user",
            "processes": self._get_interesting_processes(),
            "open_ports": self._get_open_ports(),
            "interfaces": self._get_interfaces()
        }
        return context

    def _is_root(self):
        try:
            return os.geteuid() == 0
        except:
            return False # Windows default

    def _get_interesting_processes(self):
        """Filters for security-relevant processes (web servers, dbs, av)."""
        interesting = []
        targets = ['apache', 'nginx', 'mysql', 'postgres', 'docker', 'wireshark', 'burpsuite']
        try:
            for proc in psutil.process_iter(['name']):
                if any(t in proc.info['name'].lower() for t in targets):
                    interesting.append(proc.info['name'])
        except:
            pass
        return list(set(interesting))

    def _get_open_ports(self):
        """Returns list of open listening ports."""
        ports = []
        try:
            for conn in psutil.net_connections(kind='inet'):
                if conn.status == 'LISTEN':
                    ports.append(conn.laddr.port)
        except:
            pass
        return ports

    def _get_interfaces(self):
        """Returns network interfaces."""
        return list(psutil.net_if_addrs().keys())

    # --- Web Context (User would pass a URL/Target) ---
    def analyze_web_target(self, url, html_content=None, headers=None):
        """
        Constructs context object for a web target.
        This doesn't scan, just structures known data.
        """
        ctx = {
            "url": url,
            "inputs": [], # form fields
            "headers": headers or {},
            "cookies": False,
            "auth_detected": False,
            "tech_stack": []
        }
        
        # Simple heuristic analysis if content is provided
        if html_content:
            lower_html = html_content.lower()
            if "<input" in lower_html:
                # Basic parsing or regex could go here
                ctx["inputs"].append("generic_form")
                
            if "login" in lower_html or "password" in lower_html:
                ctx["auth_detected"] = True
                
            if "react" in lower_html: ctx["tech_stack"].append("React")
            if "php" in lower_html: ctx["tech_stack"].append("PHP")
            
        return ctx
