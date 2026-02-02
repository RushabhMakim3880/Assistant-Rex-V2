import 'dart:async';
import 'package:flutter/foundation.dart';
import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:flutter_background_service/flutter_background_service.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'socket_service.dart';
import 'package:shared_preferences/shared_preferences.dart';

// Entry point suitable for isolation
@pragma('vm:entry-point')
void onStart(ServiceInstance service) async {
  DartPluginRegistrant.ensureInitialized();

  // Initialize Notification Channel for Foreground Service
  final FlutterLocalNotificationsPlugin flutterLocalNotificationsPlugin =
      FlutterLocalNotificationsPlugin();

  await flutterLocalNotificationsPlugin
      .resolvePlatformSpecificImplementation<
        AndroidFlutterLocalNotificationsPlugin
      >()
      ?.createNotificationChannel(
        const AndroidNotificationChannel(
          'rex_uplink_channel', // id
          'REX Uplink Service', // name
          description: 'Maintains connection to REX Desktop',
          importance: Importance.low,
        ),
      );

  // Configuration is handled in the main isolate via initialize.
  // Here we just handle the running service.

  // Bring up Socket Logic here?
  // Ideally, SocketService should be singleton accessible or re-created here.
  // Since this runs in a separate isolate often, we might need a fresh socket instance
  // OR we keep the main isolate alive.

  // For 'flutter_background_service', the 'onStart' is the background runner.
  // We need to Connect socket here to persist.

  // Load IP
  final prefs = await SharedPreferences.getInstance();
  final savedIp = prefs.getString('rex_server_ip');

  if (savedIp != null) {
    debugPrint("[Background] Connecting to $savedIp");
    final socket = SocketService();
    socket.connect(savedIp);

    // Periodically update notification?
    Timer.periodic(const Duration(seconds: 30), (timer) async {
      if (service is AndroidServiceInstance) {
        if (await service.isForegroundService()) {
          service.setForegroundNotificationInfo(
            title: "REX Uplink Active",
            content: "Connected: ${socket.isConnected}",
          );
        }
      }

      // Keep alive logic or ping if needed
      if (!socket.isConnected) {
        debugPrint("[Background] Reconnecting...");
        socket.connect(savedIp);
      }
    });
  }

  service.on('stopService').listen((event) {
    service.stopSelf();
  });
}

@pragma('vm:entry-point')
bool onIosBackground(ServiceInstance service) {
  WidgetsFlutterBinding.ensureInitialized();
  return true;
}

class RexBackgroundService {
  static Future<void> initialize() async {
    final service = FlutterBackgroundService();

    // Create Notification Channel (Main Isolate)
    final FlutterLocalNotificationsPlugin flutterLocalNotificationsPlugin =
        FlutterLocalNotificationsPlugin();

    const AndroidNotificationChannel channel = AndroidNotificationChannel(
      'rex_uplink_channel', // id
      'REX Uplink Service', // name
      description: 'Maintains connection to REX Desktop',
      importance: Importance.low,
    );

    await flutterLocalNotificationsPlugin
        .resolvePlatformSpecificImplementation<
          AndroidFlutterLocalNotificationsPlugin
        >()
        ?.createNotificationChannel(channel);

    await service.configure(
      androidConfiguration: AndroidConfiguration(
        onStart: onStart,
        autoStart: false, // We start it manually after connection/permission
        isForegroundMode: true,
        notificationChannelId: 'rex_uplink_channel',
        initialNotificationTitle: 'REX Linked',
        initialNotificationContent: 'Ready',
        foregroundServiceNotificationId: 888,
      ),
      iosConfiguration: IosConfiguration(),
    );
  }

  static Future<void> start() async {
    final service = FlutterBackgroundService();
    if (!await service.isRunning()) {
      service.startService();
    }
  }
}
