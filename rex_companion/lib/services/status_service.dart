import 'package:flutter/foundation.dart';
import 'package:home_widget/home_widget.dart';
import 'socket_service.dart';

class StatusService extends ChangeNotifier {
  final SocketService socketService;
  String _currentStatus = "Connected";
  List<String> _activeTools = [];

  StatusService(this.socketService) {
    _initSocketListeners();
    _updateWidget(); // Sync initial state
  }

  String get currentStatus => _currentStatus;
  List<String> get activeTools => _activeTools;

  void _initSocketListeners() {
    socketService.addListener(() {
      if (socketService.isConnected) {
        socketService.socket?.on('mobile:activity_update', (data) {
          if (data is Map) {
            _currentStatus = data['status'] ?? "Idle";
            _activeTools = List<String>.from(data['tools'] ?? []);
            notifyListeners();
            _updateWidget();
          }
        });
      }
    });
  }

  Future<void> _updateWidget() async {
    try {
      await HomeWidget.saveWidgetData<String>(
        'status',
        _currentStatus.toUpperCase(),
      );
      String activity = _activeTools.isNotEmpty
          ? "EXECUTING: ${_activeTools.first}"
          : "SYSTEM IDLE";
      await HomeWidget.saveWidgetData<String>('activity', activity);

      await HomeWidget.updateWidget(
        name: 'RexWidgetProvider',
        androidName: 'RexWidgetProvider',
      );
    } catch (e) {
      debugPrint("StatusService: Error updating widget: $e");
    }
  }
}
