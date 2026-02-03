import os
import subprocess
import logging

class SystemControl:
    """
    Handles OS-level automation: Files, Permissions, Processes, Services, Logs.
    """
    def __init__(self):
        self.logger = logging.getLogger("SystemControl")

    def execute(self, cmd):
        """Helper to run shell commands."""
        try:
            # Check for sudo requirement? For now, we assume REX runs as root or user handles it.
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                return False, result.stderr.strip()
            return True, result.stdout.strip()
        except Exception as e:
            return False, str(e)

    # --- File System ---
    def write_file(self, path, content, mode='w', permissions=None):
        try:
            with open(path, mode) as f:
                f.write(content)
            if permissions:
                self.set_permissions(path, permissions)
            return True, f"File written: {path}"
        except Exception as e:
            return False, str(e)

    def delete_file(self, path):
        try:
            os.remove(path)
            return True, f"Deleted: {path}"
        except Exception as e:
            return False, str(e)

    def set_permissions(self, path, chmod_code):
        """Example: set_permissions('/tmp/payload', '755')"""
        return self.execute(f"chmod {chmod_code} {path}")

    # --- Process Management ---
    def spawn_process(self, command, background=True):
        """
        Spawns a process.
        background=True: Uses Popen (non-blocking).
        background=False: Uses run (blocking).
        """
        try:
            if background:
                # nohup to detach? Or just Popen?
                # For a persistent agent tool, Popen is better.
                proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                return True, f"Started PID: {proc.pid}"
            else:
                success, output = self.execute(command)
                return success, output
        except Exception as e:
            return False, str(e)

    def kill_process(self, pid_or_name):
        # basic heuristic: if digit -> pid, else pkill
        if str(pid_or_name).isdigit():
            return self.execute(f"kill -9 {pid_or_name}")
        else:
            return self.execute(f"pkill -f {pid_or_name}")

    # --- Service Control ---
    def service_control(self, service, action):
        """action: start, stop, restart, status"""
        valid = ['start', 'stop', 'restart', 'status', 'enable', 'disable']
        if action not in valid:
            return False, "Invalid action"
        return self.execute(f"service {service} {action}") # Kali uses service or systemctl

    # --- Logs ---
    def tail_log(self, log_path, lines=50):
        if not os.path.exists(log_path):
            return False, "Log file not found"
        return self.execute(f"tail -n {lines} {log_path}")
