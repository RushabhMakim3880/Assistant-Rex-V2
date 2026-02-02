import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import 'package:animate_do/animate_do.dart';
import '../services/socket_service.dart';
import '../services/telephony_service.dart';
import '../services/status_service.dart';
import '../services/file_service.dart';
import 'connection_screen.dart';
import 'settings_screen.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen>
    with TickerProviderStateMixin {
  late AnimationController _pulseController;
  late AnimationController _rotateController;

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 4),
    )..repeat(reverse: true);

    _rotateController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 10),
    )..repeat();

    WidgetsBinding.instance.addPostFrameCallback((_) {
      Provider.of<TelephonyService>(
        context,
        listen: false,
      ).startNativeListener();
    });
  }

  @override
  void dispose() {
    _pulseController.dispose();
    _rotateController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final socketService = Provider.of<SocketService>(context);
    final statusService = Provider.of<StatusService>(context);
    final fileService = Provider.of<FileService>(context);

    if (!socketService.isConnected) {
      Future.microtask(() {
        if (context.mounted) {
          Navigator.of(context).pushReplacement(
            MaterialPageRoute(builder: (context) => const ConnectionScreen()),
          );
        }
      });
      return const Scaffold(
        backgroundColor: Colors.black,
        body: Center(child: CircularProgressIndicator(color: Colors.red)),
      );
    }

    return Scaffold(
      backgroundColor: const Color(0xFF050510),
      body: Stack(
        children: [
          // 1. Ambient Background Gradient
          Positioned.fill(
            child: Container(
              decoration: const BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [
                    Color(0xFF050510),
                    Color(0xFF0F172A),
                    Color(0xFF000000),
                  ],
                ),
              ),
            ),
          ),

          // 2. Animated Glow Orbs
          AnimatedBuilder(
            animation: _pulseController,
            builder: (context, child) {
              return Positioned(
                top: -100,
                right: -50,
                child: Container(
                  width: 300,
                  height: 300,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: const Color(0xFF22D3EE).withOpacity(0.15),
                    boxShadow: [
                      BoxShadow(
                        color: const Color(0xFF22D3EE).withOpacity(0.2),
                        blurRadius: 100,
                        spreadRadius: 20,
                      ),
                    ],
                  ),
                ),
              );
            },
          ),
          Positioned(
            bottom: -150,
            left: -50,
            child: Container(
              width: 400,
              height: 400,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: const Color(0xFF6366F1).withOpacity(0.1),
                boxShadow: [
                  BoxShadow(
                    color: const Color(0xFF6366F1).withOpacity(0.1),
                    blurRadius: 120,
                    spreadRadius: 10,
                  ),
                ],
              ),
            ),
          ),

          // 3. Content
          SafeArea(
            child: Padding(
              padding: const EdgeInsets.symmetric(
                horizontal: 24.0,
                vertical: 16.0,
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Header
                  _buildHeader(socketService),
                  const SizedBox(height: 30),

                  // Core Visualization
                  Center(
                    child: _buildCoreVisualizer(
                      statusService.activeTools.isNotEmpty,
                    ),
                  ),

                  const SizedBox(height: 40),

                  // Status / Logs
                  _buildGlassCard(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          "SYSTEM STATUS",
                          style: GoogleFonts.outfit(
                            color: Colors.white70,
                            fontSize: 12,
                            fontWeight: FontWeight.w500,
                            letterSpacing: 1.5,
                          ),
                        ),
                        const SizedBox(height: 10),
                        Row(
                          children: [
                            Container(
                              width: 8,
                              height: 8,
                              decoration: BoxDecoration(
                                shape: BoxShape.circle,
                                color: statusService.activeTools.isNotEmpty
                                    ? const Color(0xFF22D3EE)
                                    : Colors.grey,
                                boxShadow: statusService.activeTools.isNotEmpty
                                    ? [
                                        const BoxShadow(
                                          color: Color(0xFF22D3EE),
                                          blurRadius: 10,
                                          spreadRadius: 2,
                                        ),
                                      ]
                                    : [],
                              ),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Text(
                                statusService.activeTools.isNotEmpty
                                    ? "EXECUTING: ${statusService.activeTools.last.toUpperCase()}"
                                    : statusService.currentStatus.toUpperCase(),
                                style: GoogleFonts.shareTechMono(
                                  color: Colors.white,
                                  fontSize: 16,
                                  fontWeight: FontWeight.bold,
                                ),
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),

                  const Spacer(),

                  // Actions Grid
                  Text(
                    "QUICK ACTIONS",
                    style: GoogleFonts.outfit(
                      color: Colors.white54,
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                      letterSpacing: 1.2,
                    ),
                  ),
                  const SizedBox(height: 16),

                  Expanded(
                    flex: 2,
                    child: GridView.count(
                      crossAxisCount: 2,
                      mainAxisSpacing: 16,
                      crossAxisSpacing: 16,
                      childAspectRatio: 1.4,
                      children: [
                        _buildActionCard(
                          "FILE BEAM",
                          Icons.upload_file,
                          () => fileService.pickAndSendFile(),
                          color: const Color(0xFF22D3EE),
                        ),
                        _buildActionCard("CAMERA", Icons.camera_alt, () {
                          // This is actually triggered by voice usually, but we can add manual logic here later
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(
                              content: Text(
                                "Camera controlled by Voice Command on Desktop",
                              ),
                            ),
                          );
                        }, color: const Color(0xFFA5F3FC)),
                        _buildStatusTile("TELEPHONY", "READY", Icons.phone),
                        _buildStatusTile("GPS", "ACTIVE", Icons.location_on),
                      ],
                    ),
                  ),

                  const SizedBox(height: 10),
                  Center(
                    child: Text(
                      "CONNECTED TO ADA V2 CORE",
                      style: GoogleFonts.shareTechMono(
                        color: Colors.white30,
                        fontSize: 10,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHeader(SocketService socketService) {
    return Row(
      children: [
        Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: const Color(0xFF22D3EE).withOpacity(0.1),
            borderRadius: BorderRadius.circular(12),
          ),
          child: const Icon(Icons.hub, color: Color(0xFF22D3EE), size: 24),
        ),
        const SizedBox(width: 16),
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              "R.E.X. COMPANION",
              style: GoogleFonts.outfit(
                color: Colors.white,
                fontSize: 18,
                fontWeight: FontWeight.bold,
                letterSpacing: 1,
              ),
            ),
            Text(
              "Remote Uplink Active",
              style: GoogleFonts.outfit(
                color: const Color(0xFF22D3EE),
                fontSize: 12,
              ),
            ),
          ],
        ),
        const Spacer(),
        IconButton(
          onPressed: () => Navigator.push(
            context,
            MaterialPageRoute(builder: (context) => const SettingsScreen()),
          ),
          icon: const Icon(Icons.settings, color: Color(0xFF22D3EE)),
        ),
        IconButton(
          onPressed: () => socketService.disconnect(),
          icon: const Icon(Icons.power_settings_new, color: Colors.redAccent),
        ),
      ],
    );
  }

  Widget _buildCoreVisualizer(bool isActive) {
    return SizedBox(
      height: 220,
      width: 220,
      child: Stack(
        alignment: Alignment.center,
        children: [
          // Outer Rotating Ring
          RotationTransition(
            turns: _rotateController,
            child: Container(
              width: 200,
              height: 200,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                border: Border.all(
                  color: const Color(0xFF22D3EE).withOpacity(0.2),
                  width: 1,
                ),
              ),
              child: CustomPaint(painter: ArcPainter()),
            ),
          ),

          // Middle Pulse
          AnimatedBuilder(
            animation: _pulseController,
            builder: (context, child) {
              return Container(
                width: 140 + (_pulseController.value * 20),
                height: 140 + (_pulseController.value * 20),
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: const Color(0xFF22D3EE).withOpacity(0.05),
                  border: Border.all(
                    color: const Color(0xFF22D3EE).withOpacity(0.3),
                    width: 1.5,
                  ),
                ),
              );
            },
          ),

          // Inner Core
          Container(
            width: 100,
            height: 100,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              gradient: RadialGradient(
                colors: isActive
                    ? [const Color(0xFF22D3EE), const Color(0xFF0F172A)]
                    : [Colors.white10, Colors.black],
              ),
              boxShadow: [
                BoxShadow(
                  color: isActive
                      ? const Color(0xFF22D3EE).withOpacity(0.4)
                      : Colors.transparent,
                  blurRadius: 30,
                  spreadRadius: 5,
                ),
              ],
            ),
            child: Icon(
              isActive ? Icons.graphic_eq : Icons.mic_none,
              color: Colors.white,
              size: 40,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildGlassCard({required Widget child}) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(20),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
        child: Container(
          width: double.infinity,
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: Colors.white.withOpacity(0.05),
            borderRadius: BorderRadius.circular(20),
            border: Border.all(color: Colors.white.withOpacity(0.1), width: 1),
          ),
          child: child,
        ),
      ),
    );
  }

  Widget _buildActionCard(
    String title,
    IconData icon,
    VoidCallback onTap, {
    required Color color,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        decoration: BoxDecoration(
          color: color.withOpacity(0.1),
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: color.withOpacity(0.3), width: 1),
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, color: color, size: 28),
            const SizedBox(height: 8),
            Text(
              title,
              style: GoogleFonts.shareTechMono(
                color: Colors.white,
                fontSize: 14,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatusTile(String title, String status, IconData icon) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.03),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: Colors.white.withOpacity(0.05)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, color: Colors.white30, size: 20),
          const SizedBox(height: 8),
          Text(
            title,
            style: GoogleFonts.outfit(color: Colors.white54, fontSize: 10),
          ),
          Text(
            status,
            style: GoogleFonts.shareTechMono(
              color: const Color(0xFF4ADE80),
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }
}

class ArcPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = const Color(0xFF22D3EE).withOpacity(0.5)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2
      ..strokeCap = StrokeCap.round;

    final rect = Rect.fromLTWH(0, 0, size.width, size.height);

    // Draw 3 random arcs
    canvas.drawArc(rect, 0, 1.5, false, paint);
    canvas.drawArc(rect, 2.5, 0.5, false, paint);
    canvas.drawArc(rect, 4, 1.2, false, paint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
