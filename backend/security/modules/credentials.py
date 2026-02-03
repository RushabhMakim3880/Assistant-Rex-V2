from ..system import SystemControl
import shutil

class CredentialModule:
    """
    Handles Brute-force and Wordlist generation.
    """
    def __init__(self, system_control):
        self.system = system_control

    def run_hydra(self, target, service, user, wordlist):
        """
        Wraps Hydra for brute-forcing.
        hydra -l [user] -P [wordlist] [target] [service]
        """
        if not shutil.which("hydra"):
            return False, "Hydra not installed."
        
        cmd = f"hydra -l {user} -P {wordlist} {target} {service}"
        return self.system.spawn_process(cmd)

    def generate_wordlist(self, keywords, output_file="passwords.txt"):
        """
        Simple context-aware wordlist generator.
        keywords: list of strings (company name, year, etc.)
        """
        try:
            with open(output_file, 'w') as f:
                for k in keywords:
                    f.write(f"{k}\n")
                    f.write(f"{k}123\n")
                    f.write(f"{k}2024\n")
                    f.write(f"{k}2025\n")
                    f.write(f"{k}!\n")
            return True, f"Wordlist generated: {output_file}"
        except Exception as e:
            return False, str(e)
