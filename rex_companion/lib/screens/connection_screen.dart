import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../services/socket_service.dart';
import 'dashboard_screen.dart';
import 'qr_scan_screen.dart';
import '../services/background_service.dart';

class ConnectionScreen extends StatefulWidget {
  const ConnectionScreen({super.key});

  @override
  State<ConnectionScreen> createState() => _ConnectionScreenState();
}

class _ConnectionScreenState extends State<ConnectionScreen>
    with SingleTickerProviderStateMixin {
  final TextEditingController _ipController = TextEditingController();
  late AnimationController _pulseController;
  bool _isConnecting = false;

  @override
  void initState() {
    super.initState();
    _loadSavedIp();

    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 4),
    )..repeat(reverse: true);

    // Listen for connection changes
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) {
        final socketService = Provider.of<SocketService>(
          context,
          listen: false,
        );
        socketService.addListener(_handleSocketConnection);
      }
    });
  }

  @override
  void dispose() {
    try {
      final socketService = Provider.of<SocketService>(context, listen: false);
      socketService.removeListener(_handleSocketConnection);
    } catch (e) {
      // Provider might be disposed
    }
    _pulseController.dispose();
    _ipController.dispose();
    super.dispose();
  }

  void _handleSocketConnection() {
    if (!mounted) return;
    try {
      final socketService = Provider.of<SocketService>(context, listen: false);

      if (socketService.isConnected) {
        setState(() {
          _isConnecting = false;
        });
        // Navigate
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(builder: (context) => const DashboardScreen()),
        );
      }
    } catch (e) {
      debugPrint("Error in _handleSocketConnection: $e");
    }
  }

  Future<void> _loadSavedIp() async {
    final prefs = await SharedPreferences.getInstance();
    final savedIp = prefs.getString('rex_server_ip');
    if (savedIp != null) {
      if (mounted) {
        setState(() {
          _ipController.text = savedIp;
        });
      }
    }
  }

  Future<void> _saveIp(String ip) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('rex_server_ip', ip);
  }

  Future<void> _scanQR() async {
    final result = await Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => const QRScanScreen()),
    );

    if (result != null && result is String) {
      setState(() {
        _ipController.text = result;
      });
      // Auto-connect after scan
      if (mounted) {
        final socketService = Provider.of<SocketService>(
          context,
          listen: false,
        );
        _connect(socketService);
      }
    }
  }

  void _connect(SocketService socketService) {
    // Force hide keyboard
    FocusManager.instance.primaryFocus?.unfocus();

    if (_ipController.text.isNotEmpty) {
      setState(() {
        _isConnecting = true;
      });
      String input = _ipController.text.trim();

      if (!input.startsWith('http')) {
        input = 'http://$input';
      }

      if (input.split(':').length < 3) {
        input = '$input:8000';
      }

      _saveIp(input);

      try {
        socketService.connect(input);

        // Start Background Keep-Alive Service
        RexBackgroundService.start();

        // Timeout Handler
        Future.delayed(const Duration(seconds: 15), () {
          if (mounted && _isConnecting && !socketService.isConnected) {
            setState(() {
              _isConnecting = false;
            });
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text("Connection Timeout. Check PC Firewall."),
                backgroundColor: Colors.redAccent,
              ),
            );
          }
        });
      } catch (e) {
        setState(() {
          _isConnecting = false;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text("Error: $e"), backgroundColor: Colors.red),
        );
      }
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text("Enter IP or Scan QR"),
          backgroundColor: Colors.orange,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final socketService = Provider.of<SocketService>(context);

    return Scaffold(
      backgroundColor: Colors.black,
      body: Stack(
        children: [
          // Holographic Background
          AnimatedBuilder(
            animation: _pulseController,
            builder: (context, child) {
              return Positioned(
                top: -150,
                left: -100,
                child: Container(
                  width: 500,
                  height: 500,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: const Color(
                      0xFF22D3EE,
                    ).withValues(alpha: 0.05 + (_pulseController.value * 0.05)),
                    backgroundBlendMode: BlendMode.screen,
                    boxShadow: [
                      BoxShadow(
                        color: const Color(0xFF22D3EE).withValues(alpha: 0.15),
                        blurRadius: 150,
                        spreadRadius: 50,
                      ),
                    ],
                  ),
                ),
              );
            },
          ),

          Center(
            child: SingleChildScrollView(
              child: Padding(
                padding: const EdgeInsets.all(32.0),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    // Logo / Title
                    Container(
                      width: 80,
                      height: 80,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        border: Border.all(
                          color: const Color(0xFF22D3EE),
                          width: 2,
                        ),
                        boxShadow: const [
                          BoxShadow(
                            color: Color(0xFF22D3EE),
                            blurRadius: 20,
                            spreadRadius: -5,
                          ),
                        ],
                      ),
                      child: const Icon(
                        Icons.hub,
                        color: Color(0xFF22D3EE),
                        size: 40,
                      ),
                    ),
                    const SizedBox(height: 24),

                    Text(
                      "REX LINK",
                      style: GoogleFonts.shareTechMono(
                        fontSize: 32,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                        letterSpacing: 4.0,
                      ),
                    ),
                    Text(
                      "SECURE UPLINK TERMINAL",
                      style: GoogleFonts.shareTechMono(
                        fontSize: 12,
                        color: const Color(0xFF22D3EE).withValues(alpha: 0.7),
                        letterSpacing: 1.0,
                      ),
                    ),

                    const SizedBox(height: 64),

                    // Input Field
                    TextField(
                      controller: _ipController,
                      style: const TextStyle(
                        color: Colors.white,
                        fontFamily: 'ShareTechMono',
                      ),
                      decoration: InputDecoration(
                        labelText: "HOST ADDRESS",
                        labelStyle: TextStyle(
                          color: Colors.white.withValues(alpha: 0.3),
                        ),
                        enabledBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                          borderSide: BorderSide(
                            color: Colors.white.withValues(alpha: 0.1),
                          ),
                        ),
                        focusedBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                          borderSide: const BorderSide(
                            color: Color(0xFF22D3EE),
                          ),
                        ),
                        filled: true,
                        fillColor: Colors.white.withValues(alpha: 0.05),
                        suffixIcon: IconButton(
                          icon: const Icon(
                            Icons.qr_code_scanner,
                            color: Color(0xFF22D3EE),
                          ),
                          onPressed: _scanQR,
                        ),
                      ),
                    ),
                    const SizedBox(height: 32),

                    // Connect Button (Primary)
                    SizedBox(
                      width: double.infinity,
                      height: 56,
                      child: ElevatedButton(
                        onPressed: _isConnecting
                            ? null
                            : () => _connect(socketService),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF22D3EE),
                          foregroundColor: Colors.black,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                          elevation: 10,
                          shadowColor: const Color(
                            0xFF22D3EE,
                          ).withValues(alpha: 0.4),
                          textStyle: const TextStyle(
                            fontFamily: 'ShareTechMono',
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        child: _isConnecting
                            ? const SizedBox(
                                width: 24,
                                height: 24,
                                child: CircularProgressIndicator(
                                  color: Colors.black,
                                  strokeWidth: 2,
                                ),
                              )
                            : const Text("ESTABLISH UPLINK"),
                      ),
                    ),

                    const SizedBox(height: 24),

                    // Scan Button (Secondary)
                    TextButton.icon(
                      onPressed: _scanQR,
                      icon: const Icon(
                        Icons.qr_code,
                        size: 20,
                        color: Colors.white54,
                      ),
                      label: Text(
                        "SCAN QR CODE",
                        style: GoogleFonts.shareTechMono(color: Colors.white54),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
