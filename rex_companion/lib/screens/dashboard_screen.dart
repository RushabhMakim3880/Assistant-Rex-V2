import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import 'package:animate_do/animate_do.dart';
import '../services/socket_service.dart';
import '../services/telephony_service.dart';
import '../services/status_service.dart';
import '../services/file_service.dart';
import 'connection_screen.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen>
    with TickerProviderStateMixin {
  late AnimationController _pulseController;

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 4),
    )..repeat(reverse: true);

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
      backgroundColor: Colors.black,
      body: Stack(
        children: [
          // Background Glow
          AnimatedBuilder(
            animation: _pulseController,
            builder: (context, child) {
              return Positioned(
                top: -100,
                right: -100,
                child: Container(
                  width: 400,
                  height: 400,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: const Color(
                      0xFF22D3EE,
                    ).withValues(alpha: 0.05 + (_pulseController.value * 0.05)),
                    boxShadow: [
                      BoxShadow(
                        color: const Color(0xFF22D3EE).withValues(alpha: 0.1),
                        blurRadius: 100,
                        spreadRadius: 20,
                      ),
                    ],
                  ),
                ),
              );
            },
          ),

          SafeArea(
            child: Padding(
              padding: const EdgeInsets.symmetric(
                horizontal: 24.0,
                vertical: 16.0,
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // App Bar
                  Row(
                    children: [
                      FadeInLeft(
                        child: Text(
                          "R.E.X. CORE",
                          style: GoogleFonts.shareTechMono(
                            color: const Color(0xFF22D3EE),
                            fontSize: 24,
                            fontWeight: FontWeight.bold,
                            letterSpacing: 2,
                          ),
                        ),
                      ),
                      const Spacer(),
                      IconButton(
                        icon: const Icon(
                          Icons.power_settings_new,
                          color: Colors.redAccent,
                        ),
                        onPressed: () => socketService.disconnect(),
                      ),
                    ],
                  ),

                  const SizedBox(height: 20),

                  // Status Header
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: const Color(0xFF22D3EE).withValues(alpha: 0.05),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(
                        color: const Color(0xFF22D3EE).withValues(alpha: 0.2),
                      ),
                    ),
                    child: Stack(
                      children: [
                        // Scanline effect on high-priority status
                        if (statusService.activeTools.isNotEmpty)
                          Positioned.fill(
                            child: CustomPaint(
                              painter: ScanlinePainter(_pulseController.value),
                            ),
                          ),
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              "ACTIVITY STATUS",
                              style: GoogleFonts.shareTechMono(
                                color: const Color(
                                  0xFF22D3EE,
                                ).withValues(alpha: 0.5),
                                fontSize: 12,
                              ),
                            ),
                            const SizedBox(height: 8),
                            Text(
                              statusService.currentStatus.toUpperCase(),
                              style: GoogleFonts.shareTechMono(
                                color: Colors.white,
                                fontSize: 20,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(height: 24),

                  // Central Reactive Visualizer
                  Center(
                    child: Stack(
                      alignment: Alignment.center,
                      children: [
                        // Background Glow Pulse
                        AnimatedBuilder(
                          animation: _pulseController,
                          builder: (context, child) {
                            return Container(
                              width: 180 + (_pulseController.value * 20),
                              height: 180 + (_pulseController.value * 20),
                              decoration: BoxDecoration(
                                shape: BoxShape.circle,
                                color: const Color(
                                  0xFF22D3EE,
                                ).withValues(alpha: 0.05),
                                border: Border.all(
                                  color: const Color(
                                    0xFF22D3EE,
                                  ).withValues(alpha: 0.1),
                                  width: 1,
                                ),
                              ),
                            );
                          },
                        ),
                        // Rotating/Scanning Ring
                        RotationTransition(
                          turns: _pulseController,
                          child: Container(
                            width: 150,
                            height: 150,
                            decoration: BoxDecoration(
                              shape: BoxShape.circle,
                              border: Border.all(
                                color: const Color(
                                  0xFF22D3EE,
                                ).withValues(alpha: 0.3),
                                width: 2,
                                style: BorderStyle.none, // Hide plain border
                              ),
                            ),
                            child: CustomPaint(painter: RingPainter()),
                          ),
                        ),
                        // Core Icon
                        Pulse(
                          infinite: true,
                          duration: const Duration(seconds: 2),
                          child: Container(
                            width: 100,
                            height: 100,
                            decoration: BoxDecoration(
                              shape: BoxShape.circle,
                              color: const Color(
                                0xFF22D3EE,
                              ).withValues(alpha: 0.1),
                              boxShadow: [
                                BoxShadow(
                                  color: const Color(
                                    0xFF22D3EE,
                                  ).withValues(alpha: 0.2),
                                  blurRadius: 20,
                                  spreadRadius: 5,
                                ),
                              ],
                            ),
                            child: const Icon(
                              Icons.api_outlined,
                              size: 48,
                              color: Color(0xFF22D3EE),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(height: 24),

                  // Execution Log (Activity Mirroring)
                  Text(
                    "REAL-TIME LOG",
                    style: GoogleFonts.shareTechMono(
                      color: Colors.white.withValues(alpha: 0.4),
                      fontSize: 12,
                    ),
                  ),
                  const SizedBox(height: 12),
                  Container(
                    height: 120,
                    width: double.infinity,
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.white.withValues(alpha: 0.03),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(
                        color: Colors.white.withValues(alpha: 0.05),
                      ),
                    ),
                    child: statusService.activeTools.isEmpty
                        ? Center(
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Icon(
                                  Icons.blur_on,
                                  color: const Color(
                                    0xFF22D3EE,
                                  ).withValues(alpha: 0.2),
                                  size: 32,
                                ),
                                const SizedBox(height: 8),
                                Text(
                                  "SYSTEM IDLE",
                                  style: GoogleFonts.shareTechMono(
                                    color: Colors.white.withValues(alpha: 0.2),
                                    fontSize: 14,
                                  ),
                                ),
                              ],
                            ),
                          )
                        : ListView.builder(
                            itemCount: statusService.activeTools.length,
                            itemBuilder: (context, index) {
                              return FadeIn(
                                child: Padding(
                                  padding: const EdgeInsets.symmetric(
                                    vertical: 4.0,
                                  ),
                                  child: Row(
                                    children: [
                                      Pulse(
                                        infinite: true,
                                        child: const Icon(
                                          Icons.circle,
                                          color: Color(0xFF22D3EE),
                                          size: 8,
                                        ),
                                      ),
                                      const SizedBox(width: 8),
                                      Text(
                                        "EXECUTING: ${statusService.activeTools[index]}",
                                        style: GoogleFonts.shareTechMono(
                                          color: const Color(0xFF22D3EE),
                                          fontSize: 13,
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              );
                            },
                          ),
                  ),

                  const SizedBox(height: 32),

                  // Actions
                  Text(
                    "REMOTE TOOLS",
                    style: GoogleFonts.shareTechMono(
                      color: Colors.white.withValues(alpha: 0.4),
                      fontSize: 12,
                    ),
                  ),
                  const SizedBox(height: 12),
                  Expanded(
                    child: GridView.count(
                      crossAxisCount: 2,
                      mainAxisSpacing: 16,
                      crossAxisSpacing: 16,
                      children: [
                        _buildActionButton(
                          "FILE BEAM",
                          Icons.send_to_mobile,
                          () => fileService.pickAndSendFile(),
                        ),
                        _buildActionButton("CAMERA POV", Icons.visibility, () {
                          // Quick toggle logic could go here or show a preview
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(
                              content: Text("Camera controlled by REX."),
                            ),
                          );
                        }),
                        _buildStatusCard(
                          "TELEPHONY",
                          "READY",
                          Icons.phone_android,
                        ),
                        _buildStatusCard(
                          "LOCATION",
                          "ACTIVE",
                          Icons.location_on,
                        ),
                      ],
                    ),
                  ),

                  // Footer
                  Center(
                    child: Text(
                      "REX COMPANION v1.2 | PHASE 4 ACTIVE",
                      style: GoogleFonts.shareTechMono(
                        color: Colors.white.withValues(alpha: 0.2),
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

  Widget _buildActionButton(String label, IconData icon, VoidCallback onTap) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: const Color(0xFF22D3EE).withValues(alpha: 0.05),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(
              color: const Color(0xFF22D3EE).withValues(alpha: 0.2),
            ),
          ),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(icon, color: const Color(0xFF22D3EE), size: 32),
              const SizedBox(height: 12),
              Text(
                label,
                style: GoogleFonts.shareTechMono(
                  color: const Color(0xFF22D3EE),
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStatusCard(String title, String status, IconData icon) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.02),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white.withValues(alpha: 0.05)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Icon(icon, color: Colors.white.withValues(alpha: 0.2), size: 24),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: GoogleFonts.shareTechMono(
                  color: Colors.white.withValues(alpha: 0.3),
                  fontSize: 10,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                status,
                style: GoogleFonts.shareTechMono(
                  color: Colors.white.withValues(alpha: 0.6),
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class ScanlinePainter extends CustomPainter {
  final double progress;
  ScanlinePainter(this.progress);

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = const Color(0xFF22D3EE).withValues(alpha: 0.1)
      ..strokeWidth = 1.0;

    double y = size.height * progress;
    canvas.drawLine(Offset(0, y), Offset(size.width, y), paint);

    // Multiple faint lines
    canvas.drawLine(
      Offset(0, (y + 10) % size.height),
      Offset(size.width, (y + 10) % size.height),
      paint,
    );
    canvas.drawLine(
      Offset(0, (y - 10) % size.height),
      Offset(size.width, (y - 10) % size.height),
      paint,
    );
  }

  @override
  bool shouldRepaint(covariant ScanlinePainter oldDelegate) => true;
}

class RingPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = const Color(0xFF22D3EE).withValues(alpha: 0.3)
      ..strokeWidth = 2.0
      ..style = PaintingStyle.stroke;

    final center = Offset(size.width / 2, size.height / 2);
    final radius = size.width / 2;

    // Draw partial arcs for a holographic ring effect
    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      0,
      1.5,
      false,
      paint,
    );
    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      3.14,
      1.5,
      false,
      paint,
    );
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
