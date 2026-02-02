import 'package:flutter/material.dart';
import 'dart:math';

class Visualizer extends StatefulWidget {
  final bool isListening;
  final double intensity;
  final double width;
  final double height;

  const Visualizer({
    super.key,
    this.isListening = false,
    this.intensity = 0.0,
    this.width = 300,
    this.height = 300,
  });

  @override
  State<Visualizer> createState() => _VisualizerState();
}

class _VisualizerState extends State<Visualizer>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 2),
    )..repeat(reverse: true);
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: widget.width,
      height: widget.height,
      child: Stack(
        alignment: Alignment.center,
        children: [
          // Breathing / Active Circle
          AnimatedBuilder(
            animation: _controller,
            builder: (context, child) {
              double breathe = widget.isListening
                  ? 0
                  : sin(_controller.value * pi) * 10;

              double radius =
                  (widget.width * 0.25) + (widget.intensity * 40) + breathe;

              return CustomPaint(
                painter: CirclePainter(
                  radius: radius,
                  color: const Color(
                    0xFF22D3EE,
                  ).withValues(alpha: widget.isListening ? 0.8 : 0.5),
                  isListening: widget.isListening,
                ),
                size: Size(widget.width, widget.height),
              );
            },
          ),
          // Center Text
          Text(
            "R.E.X",
            style: TextStyle(
              fontSize: widget.width * 0.1,
              fontWeight: FontWeight.bold,
              letterSpacing: 4.0,
              color: const Color(0xFFCFFAFE), // cyan-100
              shadows: [
                Shadow(
                  blurRadius: 15.0,
                  color: const Color(0xFF22D3EE).withValues(alpha: 0.8),
                  offset: Offset.zero,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class CirclePainter extends CustomPainter {
  final double radius;
  final Color color;
  final bool isListening;

  CirclePainter({
    required this.radius,
    required this.color,
    required this.isListening,
  });

  @override
  void paint(Canvas canvas, Size size) {
    var paint = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = 4.0
      ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 20); // Glow effect

    canvas.drawCircle(Offset(size.width / 2, size.height / 2), radius, paint);

    // Inner subtle ring
    var innerPaint = Paint()
      ..color = const Color(0xFF06B6D4).withValues(alpha: 0.1)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2.0;

    canvas.drawCircle(
      Offset(size.width / 2, size.height / 2),
      radius - 15,
      innerPaint,
    );
  }

  @override
  bool shouldRepaint(covariant CirclePainter oldDelegate) {
    return oldDelegate.radius != radius || oldDelegate.color != color;
  }
}
