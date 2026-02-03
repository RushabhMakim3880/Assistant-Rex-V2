import subprocess
import shutil

class ToolManager:
    """
    Handles tool detection and auto-installation.
    """
    def is_installed(self, tool_name):
        return shutil.which(tool_name) is not None

    def install_tool(self, tool_name, provider="apt"):
        """
        Providers: apt, pip, git (requires url)
        """
        if self.is_installed(tool_name):
            return True, f"{tool_name} is already installed."

        cmd = ""
        if provider == "apt":
            cmd = f"DEBIAN_FRONTEND=noninteractive apt-get install -y {tool_name}"
        elif provider == "pip":
            cmd = f"pip install {tool_name}"
        
        # Run
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                return True, f"Successfully installed {tool_name}"
            return False, f"Install failed: {result.stderr}"
        except Exception as e:
            return False, str(e)
