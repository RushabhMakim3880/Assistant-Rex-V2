import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'package:permission_handler/permission_handler.dart';
import 'socket_service.dart';
import 'camera_service.dart';
import 'file_service.dart';

class TelephonyService {
  static const platform = MethodChannel('com.rex.companion/telephony');
  final SocketService socketService;
  final CameraService cameraService;
  final FileService fileService;

  TelephonyService(this.socketService, this.cameraService, this.fileService) {
    _initMethodCallHandler();
    // Don't auto-start here. Wait for UI to confirm permissions.
  }

  Future<void> startNativeListener() async {
    debugPrint("TelephonyService: Checking permissions to start listener...");
    var status = await Permission.phone.status;
    var micStatus = await Permission.microphone.status;

    if (!status.isGranted || !micStatus.isGranted) {
      Map<Permission, PermissionStatus> statuses = await [
        Permission.phone,
        Permission.microphone,
        Permission.camera,
      ].request();

      status = statuses[Permission.phone]!;
    }

    if (status.isGranted) {
      debugPrint(
        "TelephonyService: Permissions granted. Starting native listener.",
      );
      try {
        await platform.invokeMethod('startListener');
      } on PlatformException catch (e) {
        debugPrint("Failed to start listener: '${e.message}'.");
      }
    } else {
      debugPrint("TelephonyService: Permissions DENIED.");
    }
  }

  void _initMethodCallHandler() {
    platform.setMethodCallHandler((call) async {
      debugPrint("Native Method Call: ${call.method}");

      if (call.method == "callStateChanged") {
        final args = call.arguments;
        debugPrint("Call State Changed: $args");

        if (socketService.isConnected) {
          socketService.socket?.emit('mobile:call_state', args);
        }
      }
    });

    // Listen for commands from Desktop
    socketService.addListener(_attachSocketListeners);

    // Initial check (in case already connected)
    if (socketService.isConnected) {
      _attachSocketListeners();
    }
  }

  void _attachSocketListeners() {
    if (socketService.isConnected) {
      // Handshake
      debugPrint("Sending Handshake: mobile:connect");
      socketService.socket?.emit('mobile:connect', {
        'device_id': 'android_device',
      });

      // Remove existing listeners to avoid duplicates
      socketService.socket?.off('mobile:answer_call');
      socketService.socket?.off('mobile:end_call');
      socketService.socket?.off('mobile:dial');
      socketService.socket?.off('mobile:open_app');
      socketService.socket?.off('mobile:go_home');
      socketService.socket?.off('mobile:search_contacts');
      socketService.socket?.off('mobile:send_whatsapp');
      socketService.socket?.off('mobile:get_contacts');
      socketService.socket?.off('mobile:set_clipboard');
      socketService.socket?.off('mobile:hardware_control');

      socketService.socket?.on('mobile:answer_call', (_) {
        debugPrint("Received command to Answer Call");
        answerCall();
      });

      socketService.socket?.on('mobile:end_call', (_) {
        debugPrint("Received command to End Call");
        endCall();
      });

      socketService.socket?.on('mobile:dial', (data) {
        debugPrint("Received command to Dial: $data");
        if (data is Map && data['number'] != null) {
          dialNumber(data['number']);
        }
      });

      socketService.socket?.on('mobile:open_app', (data) {
        debugPrint("Received command to Open App: $data");
        if (data is Map && data['app_name'] != null) {
          openApp(data['app_name']);
        }
      });

      socketService.socket?.on('mobile:go_home', (_) {
        debugPrint("Received command to Go Home");
        goHome();
      });

      socketService.socket?.on('mobile:search_contacts', (data) async {
        debugPrint("Received command to Search Contacts: $data");
        if (data is Map && data['query'] != null) {
          final results = await searchContacts(data['query']);
          socketService.socket?.emit('mobile:contact_results', {
            'query': data['query'],
            'results': results,
          });
        }
      });

      socketService.socket?.on('mobile:send_message', (data) {
        debugPrint("Received command to Send Message: $data");
        if (data is Map && data['number'] != null && data['message'] != null) {
          final platform = data['platform'] ?? 'whatsapp';
          sendMessage(platform, data['number'], data['message']);
        }
      });

      socketService.socket?.on('mobile:get_contacts', (_) async {
        debugPrint("Received command to Get Contacts");
        final results = await getContacts();
        socketService.socket?.emit('mobile:contact_list', {'results': results});
      });

      socketService.socket?.on('mobile:set_clipboard', (data) {
        debugPrint("Received command to Set Clipboard: $data");
        if (data is Map && data['text'] != null) {
          setClipboard(data['text']);
        }
      });

      socketService.socket?.on('mobile:hardware_control', (data) {
        debugPrint("Received command for Hardware Control: $data");
        if (data is Map && data['action'] != null) {
          handleHardwareControl(data['action'], data['value']);
        }
      });

      socketService.socket?.on('mobile:set_dnd', (data) {
        if (data is Map && data['enable'] != null) {
          setDND(data['enable']);
        }
      });

      socketService.socket?.on('mobile:get_location', (_) async {
        final location = await getLocation();
        if (location != null) {
          socketService.socket?.emit('mobile:location_results', location);
        }
      });

      socketService.socket?.on('mobile:camera_control', (data) async {
        if (data is Map && data['action'] != null) {
          if (data['action'] == 'start') {
            // Dynamic Permission Check
            var status = await Permission.camera.status;
            if (!status.isGranted) {
              status = await Permission.camera.request();
            }

            if (status.isGranted) {
              cameraService.initialize().then(
                (_) => cameraService.startStreaming(),
              );
            } else {
              debugPrint("Camera permission denied.");
            }
          } else {
            cameraService.stopStreaming();
          }
        }
      });

      socketService.socket?.on('mobile:file_beam', (data) {
        if (data is Map && data['action'] != null) {
          if (data['action'] == 'receive' && data['data'] != null) {
            fileService.receiveFile(
              data['filename'] ?? 'received_file',
              data['data'],
            );
          } else if (data['action'] == 'request') {
            fileService.pickAndSendFile();
          }
        }
      });
    }
  }

  Future<void> answerCall() async {
    try {
      await platform.invokeMethod('answerCall');
    } on PlatformException catch (e) {
      debugPrint("Failed to answer call: '${e.message}'.");
    }
  }

  Future<void> endCall() async {
    try {
      await platform.invokeMethod('endCall');
    } on PlatformException catch (e) {
      debugPrint("Failed to end call: '${e.message}'.");
    }
  }

  Future<void> dialNumber(String number) async {
    try {
      await platform.invokeMethod('dialNumber', {'number': number});
    } on PlatformException catch (e) {
      debugPrint("Failed to dial number: '${e.message}'.");
    }
  }

  Future<void> openApp(String appName) async {
    try {
      await platform.invokeMethod('openApp', {'appName': appName});
    } on PlatformException catch (e) {
      debugPrint("Failed to open app: '${e.message}'.");
    }
  }

  Future<void> goHome() async {
    try {
      await platform.invokeMethod('goHome');
    } on PlatformException catch (e) {
      debugPrint("Failed to go home: '${e.message}'.");
    }
  }

  Future<List<Map<String, String>>> searchContacts(String query) async {
    try {
      final List<dynamic> results = await platform.invokeMethod(
        'searchContacts',
        {'query': query},
      );
      return results.map((e) => Map<String, String>.from(e)).toList();
    } on PlatformException catch (e) {
      debugPrint("Failed to search contacts: '${e.message}'.");
      return [];
    }
  }

  Future<void> sendMessage(
    String platformName,
    String number,
    String message,
  ) async {
    try {
      await platform.invokeMethod('sendMessage', {
        'platform': platformName,
        'number': number,
        'message': message,
      });
    } on PlatformException catch (e) {
      debugPrint("Failed to send message: '${e.message}'.");
    }
  }

  Future<List<Map<String, String>>> getContacts() async {
    try {
      final List<dynamic> results = await platform.invokeMethod('getContacts');
      return results.map((e) => Map<String, String>.from(e)).toList();
    } on PlatformException catch (e) {
      debugPrint("Failed to get contacts: '${e.message}'.");
      return [];
    }
  }

  Future<void> setClipboard(String text) async {
    try {
      await platform.invokeMethod('setClipboard', {'text': text});
    } on PlatformException catch (e) {
      debugPrint("Failed to set clipboard: '${e.message}'.");
    }
  }

  Future<void> handleHardwareControl(String action, dynamic value) async {
    try {
      if (action == 'flashlight') {
        await platform.invokeMethod('toggleFlash', {'enable': value});
      } else if (action == 'volume') {
        // level should be 0-100
        await platform.invokeMethod('setVolume', {'level': value});
      } else if (action == 'dnd') {
        await platform.invokeMethod('setDND', {'enable': value});
      }
    } on PlatformException catch (e) {
      debugPrint("Failed to control hardware: '${e.message}'.");
    }
  }

  Future<void> setDND(bool enable) async {
    try {
      await platform.invokeMethod('setDND', {'enable': enable});
    } on PlatformException catch (e) {
      debugPrint("Failed to set DND: '${e.message}'.");
    }
  }

  Future<Map<String, double>?> getLocation() async {
    try {
      final Map<dynamic, dynamic>? result = await platform.invokeMethod(
        'getLocation',
      );
      if (result != null) {
        return {'lat': result['lat'] as double, 'lng': result['lng'] as double};
      }
    } on PlatformException catch (e) {
      debugPrint("Failed to get location: '${e.message}'.");
    }
    return null;
  }
}
