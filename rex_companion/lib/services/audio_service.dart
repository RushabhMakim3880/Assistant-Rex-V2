import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:sound_stream/sound_stream.dart';
import 'package:permission_handler/permission_handler.dart';
import 'socket_service.dart';

class AudioService extends ChangeNotifier {
  final SocketService socketService;
  final RecorderStream _recorder = RecorderStream();
  final PlayerStream _player = PlayerStream();

  StreamSubscription? _audioSubscription;
  bool _isRecording = false;

  AudioService(this.socketService);

  bool get isRecording => _isRecording;

  Future<void> initialize() async {
    debugPrint("AudioService: Initializing...");
    await _recorder.initialize();
    await _player.initialize();
    debugPrint("AudioService: Initialized streams.");

    // Listen for commands from Desktop
    socketService.socket?.on('mobile:start_audio', (_) {
      debugPrint("Received command to START Audio Stream");
      startAudioStream();
    });

    socketService.socket?.on('mobile:stop_audio', (_) {
      debugPrint("Received command to STOP Audio Stream");
      stopAudioStream();
    });
  }

  Future<void> startAudioStream() async {
    // 1. Check Permissions
    var status = await Permission.microphone.status;
    if (!status.isGranted) {
      status = await Permission.microphone.request();
      if (!status.isGranted) {
        debugPrint("AudioService: Mic permission denied.");
        return;
      }
    }

    // 2. Start Recorder Listener
    _audioSubscription ??= _recorder.audioStream.listen((data) {
      if (socketService.isConnected) {
        // Send raw PCM data to server
        // We might need to encode it or send as bytes
        // Socket.IO supports binary data
        socketService.socket?.emit('mobile:audio_stream', data);
      }
    });

    // 3. Start Streams
    await _recorder.start();
    await _player.start(); // Start player to be ready for incoming audio

    _isRecording = true;
    notifyListeners();
    debugPrint("AudioService: Started Streaming (In/Out)");

    // 4. Listen for Incoming Audio from Desktop
    socketService.socket?.on('mobile:audio_out', (data) {
      if (data != null) {
        // Write to player buffer
        // Expecting Uint8List or List<int>
        if (data is List<dynamic>) {
          _player.writeChunk(Uint8List.fromList(data.cast<int>()));
        } else if (data is Uint8List) {
          _player.writeChunk(data);
        }
      }
    });
  }

  Future<void> stopAudioStream() async {
    await _recorder.stop();
    await _player.stop();
    // _audioSubscription?.cancel(); // Keep subscription open?

    socketService.socket?.off('mobile:audio_out');

    _isRecording = false;
    notifyListeners();
    debugPrint("AudioService: Stopped Streaming");
  }
}
