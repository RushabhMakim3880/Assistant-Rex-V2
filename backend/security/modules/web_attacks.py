import requests
from urllib.parse import urljoin

class WebAttackModule:
    """
    Handles Web Application Attacks: SQLi, XSS, etc.
    """
    def __init__(self, system_control):
        self.system = system_control

    def test_sqli(self, url, param):
        """
        Basic SQLi test using a quote payload.
        Real implementation would use more payloads or wrap sqlmap.
        """
        payload = "'"
        # This assumes GET request for simplicity.
        # url: http://example.com/page.php?id=1
        target = f"{url}?{param}={payload}"
        try:
            res = requests.get(target, timeout=5)
            if "sql syntax" in res.text.lower() or "mysql" in res.text.lower():
                return True, "Potential SQLi detected (Error-based)"
            return False, "No obvious SQLi error detected."
        except Exception as e:
            return False, str(e)

    def test_xss(self, url, param):
        """
        Basic Reflected XSS test.
        """
        payload = "<script>alert('REX')</script>"
        target = f"{url}?{param}={payload}"
        try:
            res = requests.get(target, timeout=5)
            if payload in res.text:
                return True, "Potential Reflected XSS detected."
            return False, "Payload not reflected."
        except Exception as e:
            return False, str(e)
