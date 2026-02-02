import 'package:flutter/material.dart';
import 'package:socket_io_client/socket_io_client.dart' as io;

class SocketService with ChangeNotifier {
  io.Socket? _socket;
  bool _isConnected = false;
  Map<String, dynamic> _systemStats = {"cpu": 0.0, "ram": 0.0};

  bool get isConnected => _isConnected;
  io.Socket? get socket => _socket;
  Map<String, dynamic> get systemStats => _systemStats;

  void connect(String url) {
    if (_isConnected) return;

    debugPrint("Connecting to $url...");

    _socket = io.io(
      url,
      io.OptionBuilder()
          .setTransports(['websocket'])
          .disableAutoConnect()
          .build(),
    );

    _socket?.connect();

    _socket?.onConnect((_) {
      debugPrint('Connected to Desktop');
      _isConnected = true;
      notifyListeners();
    });

    _socket?.onDisconnect((_) {
      debugPrint('Disconnected');
      _isConnected = false;
      notifyListeners();
    });

    _socket?.on('system_stats', (data) {
      // print("Stats: $data");
      if (data is Map<String, dynamic>) {
        _systemStats = data;
        notifyListeners();
      }
    });

    _socket!.onConnectError((data) {
      debugPrint('Connection Error: $data');
      _isConnected = false;
      notifyListeners();
    });
  }

  void disconnect() {
    _socket?.disconnect();
  }
}
