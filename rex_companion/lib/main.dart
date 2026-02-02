import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import 'package:provider/provider.dart';
import 'services/socket_service.dart';
import 'services/telephony_service.dart';
import 'services/audio_service.dart';
import 'services/background_service.dart';
import 'services/camera_service.dart';
import 'services/file_service.dart';
import 'services/status_service.dart';

// Screens
import 'screens/connection_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  // We initialize the config for background service, but don't start it yet.
  // Starting happens after successful connection.
  await RexBackgroundService.initialize();

  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => SocketService()),
        ChangeNotifierProxyProvider<SocketService, AudioService>(
          create: (_) => AudioService(SocketService()),
          update: (_, socket, prev) => AudioService(socket),
        ),
        ChangeNotifierProxyProvider<SocketService, CameraService>(
          create: (_) => CameraService(SocketService()),
          update: (_, socket, prev) => CameraService(socket),
        ),
        ChangeNotifierProxyProvider<SocketService, FileService>(
          create: (_) => FileService(SocketService()),
          update: (_, socket, prev) => FileService(socket),
        ),
        ChangeNotifierProxyProvider<SocketService, StatusService>(
          create: (_) => StatusService(SocketService()),
          update: (_, socket, prev) => StatusService(socket),
        ),
        ProxyProvider3<
          SocketService,
          CameraService,
          FileService,
          TelephonyService
        >(
          update: (_, socket, camera, file, _) =>
              TelephonyService(socket, camera, file),
        ),
      ],
      child: const RexCompanionApp(),
    ),
  );
}

class RexCompanionApp extends StatelessWidget {
  const RexCompanionApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'REX Companion',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.dark,
        scaffoldBackgroundColor: const Color(0xFF050510), // Deep Black/Blue
        primaryColor: const Color(0xFF22D3EE),
        colorScheme: const ColorScheme.dark(
          primary: Color(0xFF22D3EE),
          secondary: Color(0xFF06B6D4),
          surface: Color(0x1FFFFFFF), // Glass White
          background: Color(0xFF050510),
        ),
        textTheme: GoogleFonts.shareTechMonoTextTheme(
          Theme.of(context).textTheme.apply(
            bodyColor: const Color(0xFFE2E8F0),
            displayColor: const Color(0xFF22D3EE),
          ),
        ),
        useMaterial3: true,
      ),
      home: const ConnectionScreen(),
    );
  }
}
