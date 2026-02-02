import 'dart:async';
import 'package:camera/camera.dart';
import 'package:flutter/foundation.dart';
import 'socket_service.dart';

class CameraService extends ChangeNotifier {
  final SocketService socketService;
  CameraController? _controller;
  Timer? _timer;
  bool _isStreaming = false;

  CameraService(this.socketService);

  bool get isStreaming => _isStreaming;

  Future<void> initialize() async {
    try {
      final cameras = await availableCameras();
      if (cameras.isEmpty) {
        debugPrint("CameraService: No cameras found.");
        return;
      }

      _controller = CameraController(
        cameras.first,
        ResolutionPreset.low, // Low res is enough for vision and faster
        enableAudio: false,
      );

      await _controller!.initialize();
      debugPrint("CameraService: Initialized.");
    } catch (e) {
      debugPrint("CameraService: Initialization error: $e");
    }
  }

  void startStreaming() {
    if (_controller == null ||
        !_controller!.value.isInitialized ||
        _isStreaming) {
      return;
    }

    _isStreaming = true;
    notifyListeners();
    debugPrint("CameraService: Starting stream...");

    // Take a picture every 500ms for ~2 FPS
    _timer = Timer.periodic(const Duration(milliseconds: 500), (timer) async {
      if (!_isStreaming) {
        timer.cancel();
        return;
      }

      try {
        final XFile file = await _controller!.takePicture();
        final Uint8List bytes = await file.readAsBytes();

        if (socketService.isConnected) {
          socketService.socket?.emit('mobile:camera_frame', bytes);
        }
      } catch (e) {
        debugPrint("CameraService: Capture error: $e");
      }
    });
  }

  void stopStreaming() {
    debugPrint("CameraService: Stopping stream...");
    _isStreaming = false;
    _timer?.cancel();
    _timer = null;
    notifyListeners();
  }

  @override
  void dispose() {
    _controller?.dispose();
    _timer?.cancel();
    super.dispose();
  }
}
