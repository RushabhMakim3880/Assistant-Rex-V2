import 'package:flutter/material.dart';
import 'package:mobile_scanner/mobile_scanner.dart';

class QRScanScreen extends StatefulWidget {
  const QRScanScreen({super.key});

  @override
  State<QRScanScreen> createState() => _QRScanScreenState();
}

class _QRScanScreenState extends State<QRScanScreen> {
  bool _hasScanned = false; // Lock to prevent multiple pops
  final MobileScannerController _controller = MobileScannerController(
    detectionSpeed: DetectionSpeed.normal,
    facing: CameraFacing.back,
    torchEnabled: false,
  );

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _onDetect(BarcodeCapture capture) {
    if (_hasScanned) return; // Ignore if already processed

    final List<Barcode> barcodes = capture.barcodes;
    for (final barcode in barcodes) {
      String? rawValue = barcode.rawValue;
      if (rawValue != null) {
        setState(() {
          _hasScanned = true;
        });
        debugPrint('QRScanScreen: Barcode found! $rawValue');
        Navigator.pop(context, rawValue);
        break; // Stop loop
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        title: const Text(
          "SCAN CONNECTION QR",
          style: TextStyle(
            color: Color(0xFF22D3EE),
            fontFamily: 'ShareTechMono',
            fontWeight: FontWeight.bold,
          ),
        ),
        backgroundColor: Colors.black,
        iconTheme: const IconThemeData(color: Color(0xFF22D3EE)),
        elevation: 0,
        actions: [
          IconButton(
            icon: ValueListenableBuilder<MobileScannerState>(
              valueListenable: _controller,
              builder: (context, state, child) {
                switch (state.torchState) {
                  case TorchState.off:
                    return const Icon(Icons.flash_off, color: Colors.grey);
                  case TorchState.on:
                    return const Icon(Icons.flash_on, color: Color(0xFF22D3EE));
                  default:
                    return const Icon(Icons.flash_off, color: Colors.grey);
                }
              },
            ),
            onPressed: () => _controller.toggleTorch(),
          ),
          IconButton(
            icon: ValueListenableBuilder<MobileScannerState>(
              valueListenable: _controller,
              builder: (context, state, child) {
                switch (state.cameraDirection) {
                  case CameraFacing.front:
                    return const Icon(Icons.camera_front);
                  case CameraFacing.back:
                    return const Icon(Icons.camera_rear);
                  default:
                    return const Icon(Icons.camera_rear);
                }
              },
            ),
            onPressed: () => _controller.switchCamera(),
          ),
        ],
      ),
      body: Stack(
        children: [
          MobileScanner(controller: _controller, onDetect: _onDetect),
          // Overlay
          Container(
            decoration: ShapeDecoration(
              shape: QrScannerOverlayShape(
                borderColor: const Color(0xFF22D3EE),
                borderRadius: 10,
                borderLength: 30,
                borderWidth: 10,
                cutOutSize: 300,
              ),
            ),
          ),
          // Instructions
          Positioned(
            bottom: 50,
            left: 0,
            right: 0,
            child: Center(
              child: Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 24,
                  vertical: 12,
                ),
                decoration: BoxDecoration(
                  color: Colors.black.withValues(alpha: 0.7),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(
                    color: const Color(0xFF22D3EE).withValues(alpha: 0.3),
                  ),
                ),
                child: const Text(
                  "Align QR code within the frame",
                  style: TextStyle(
                    color: Colors.white,
                    fontFamily: 'ShareTechMono',
                    fontSize: 16,
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

// Helper class for overlay if not in package, usually it is.
// If 'QrScannerOverlayShape' is missing, we'll remove it or use a simple Container with border.
// Checking package usage... 'mobile_scanner' typically requires external overlay widget or manual implementation.
// Actually, 'mobile_scanner' doesn't export QrScannerOverlayShape anymore in v5.
// I'll replace it with a simple custom painter or just a center box if it fails, but for now let's use a simple Center container helper.

class QrScannerOverlayShape extends ShapeBorder {
  final Color borderColor;
  final double borderWidth;
  final Color overlayColor;
  final double borderRadius;
  final double borderLength;
  final double cutOutSize;
  final double cutOutBottomOffset;

  const QrScannerOverlayShape({
    this.borderColor = Colors.red,
    this.borderWidth = 10.0,
    this.overlayColor = const Color.fromRGBO(0, 0, 0, 80),
    this.borderRadius = 0,
    this.borderLength = 40,
    this.cutOutSize = 250,
    this.cutOutBottomOffset = 0,
  });

  @override
  EdgeInsetsGeometry get dimensions => EdgeInsets.zero;

  @override
  Path getInnerPath(Rect rect, {TextDirection? textDirection}) {
    return Path()
      ..fillType = PathFillType.evenOdd
      ..addPath(getOuterPath(rect), Offset.zero);
  }

  @override
  Path getOuterPath(Rect rect, {TextDirection? textDirection}) {
    Path getLeftTopPath(Rect rect) {
      return Path()
        ..moveTo(rect.left, rect.bottom)
        ..lineTo(rect.left, rect.top)
        ..lineTo(rect.right, rect.top);
    }

    return getLeftTopPath(rect);
  }

  @override
  void paint(Canvas canvas, Rect rect, {TextDirection? textDirection}) {
    final width = rect.width;
    final height = rect.height;
    final borderOffset = borderWidth / 2;
    final localCutOutSize = cutOutSize;
    final localCutOutBottomOffset = cutOutBottomOffset;

    final backgroundPaint = Paint()
      ..color = overlayColor
      ..style = PaintingStyle.fill;

    final borderPaint = Paint()
      ..color = borderColor
      ..style = PaintingStyle.stroke
      ..strokeWidth = borderWidth;

    final boxPaint = Paint()
      ..color = borderColor
      ..style = PaintingStyle.fill
      ..blendMode = BlendMode.srcOut;

    final cutOutRect = Rect.fromLTWH(
      rect.left + width / 2 - localCutOutSize / 2 + borderOffset,
      rect.top +
          height / 2 -
          localCutOutSize / 2 +
          borderOffset -
          localCutOutBottomOffset,
      localCutOutSize - borderOffset * 2,
      localCutOutSize - borderOffset * 2,
    );

    canvas
      ..saveLayer(rect, backgroundPaint)
      ..drawRect(rect, backgroundPaint)
      ..drawRRect(
        RRect.fromRectAndRadius(cutOutRect, Radius.circular(borderRadius)),
        boxPaint,
      )
      ..restore();

    final borderPath = _getBorderPath(cutOutRect, borderRadius, borderLength);

    canvas.drawPath(borderPath, borderPaint);
  }

  Path _getBorderPath(Rect rect, double borderRadius, double borderLength) {
    // Top Left
    final path = Path()
      ..moveTo(rect.left, rect.top + borderLength)
      ..lineTo(rect.left, rect.top + borderRadius)
      ..arcToPoint(
        Offset(rect.left + borderRadius, rect.top),
        radius: Radius.circular(borderRadius),
      )
      ..lineTo(rect.left + borderLength, rect.top);

    // Top Right
    path
      ..moveTo(rect.right - borderLength, rect.top)
      ..lineTo(rect.right - borderRadius, rect.top)
      ..arcToPoint(
        Offset(rect.right, rect.top + borderRadius),
        radius: Radius.circular(borderRadius),
      )
      ..lineTo(rect.right, rect.top + borderLength);

    // Bottom Right
    path
      ..moveTo(rect.right, rect.bottom - borderLength)
      ..lineTo(rect.right, rect.bottom - borderRadius)
      ..arcToPoint(
        Offset(rect.right - borderRadius, rect.bottom),
        radius: Radius.circular(borderRadius),
      )
      ..lineTo(rect.right - borderLength, rect.bottom);

    // Bottom Left
    path
      ..moveTo(rect.left + borderLength, rect.bottom)
      ..lineTo(rect.left + borderRadius, rect.bottom)
      ..arcToPoint(
        Offset(rect.left, rect.bottom - borderRadius),
        radius: Radius.circular(borderRadius),
      )
      ..lineTo(rect.left, rect.bottom - borderLength);

    return path;
  }

  @override
  ShapeBorder scale(double t) {
    return QrScannerOverlayShape(
      borderColor: borderColor,
      borderWidth: borderWidth * t,
      overlayColor: overlayColor,
    );
  }
}
