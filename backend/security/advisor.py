class SecurityAdvisor:
    """
    The 'Brain' that reasons over Context to recommend attacks.
    DOES NOT ATTACK. ONLY ADVISES.
    """
    
    def analyze_feasibility(self, context, target_type="web"):
        """
        Input: Context Dict (from ContextCollector)
        Output: List of feasible actions with reasoning.
        """
        advice = {
            "recommended": [],
            "not_recommended": [],
            "info": []
        }
        
        if target_type == "web":
            self._analyze_web(context, advice)
        elif target_type == "system":
            self._analyze_system(context, advice)
            
        return advice

    def _analyze_web(self, ctx, advice):
        # 1. SQL Injection
        if any("id=" in ctx.get('url', '') for p in ['id', 'cat', 'query']):
            advice["recommended"].append({
                "module": "web_attack",
                "attack": "sqli_test",
                "reason": "URL parameter 'id' detected, potential for SQLi."
            })
            
        # 2. XSS
        if len(ctx.get('inputs', [])) > 0:
            advice["recommended"].append({
                "module": "web_attack",
                "attack": "xss_reflection",
                "reason": "Input fields detected on page."
            })
        
        # 3. Auth
        if ctx.get('auth_detected'):
             advice["recommended"].append({
                "module": "credential",
                "attack": "brute_force_login",
                "reason": "Login form detected."
            })
        else:
             advice["not_recommended"].append({
                "attack": "brute_force_login",
                "reason": "No authentication endpoints found."
            })

    def _analyze_system(self, ctx, advice):
        # 1. Priv Esc
        if ctx.get('privilege') == 'user':
             advice["recommended"].append({
                "module": "priv_esc",
                "attack": "enum_suid",
                "reason": "Running as unprivileged user."
            })
        
        # 2. Network
        if 80 in ctx.get('open_ports', []) or 443 in ctx.get('open_ports', []):
             advice["info"].append("Web server detected on local machine.")
