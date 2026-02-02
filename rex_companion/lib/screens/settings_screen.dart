import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:provider/provider.dart';
import '../services/socket_service.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  Map<Permission, PermissionStatus> _statuses = {};
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _checkPermissions();
  }

  Future<void> _checkPermissions() async {
    final permissions = [
      Permission.camera,
      Permission.microphone,
      Permission.phone,
      Permission.notification,
      // Permission.location, // Optional
    ];

    Map<Permission, PermissionStatus> statuses = {};
    for (var p in permissions) {
      statuses[p] = await p.status;
    }

    if (mounted) {
      setState(() {
        _statuses = statuses;
        _isLoading = false;
      });
    }
  }

  Future<void> _requestPermission(Permission p) async {
    final status = await p.request();
    if (mounted) {
      setState(() {
        _statuses[p] = status;
      });
    }
  }

  Future<void> _requestAll() async {
    Map<Permission, PermissionStatus> statuses = await [
      Permission.camera,
      Permission.microphone,
      Permission.phone,
      Permission.notification,
    ].request();

    if (mounted) {
      setState(() {
        _statuses = statuses;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF050510),
      body: Stack(
        children: [
          // Background Gradient
          Positioned.fill(
            child: Container(
              decoration: const BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [Color(0xFF050510), Color(0xFF0F172A)],
                ),
              ),
            ),
          ),

          SafeArea(
            child: Padding(
              padding: const EdgeInsets.all(24.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Header
                  Row(
                    children: [
                      IconButton(
                        onPressed: () => Navigator.pop(context),
                        icon: const Icon(
                          Icons.arrow_back_ios,
                          color: Colors.white70,
                        ),
                      ),
                      const SizedBox(width: 8),
                      Text(
                        "SYSTEM CONFIG",
                        style: GoogleFonts.shareTechMono(
                          color: const Color(0xFF22D3EE),
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 30),

                  // Connection Info
                  _buildSectionHeader("UPLINK STATUS"),
                  const SizedBox(height: 10),
                  Consumer<SocketService>(
                    builder: (context, socket, child) {
                      return _buildGlassCard(
                        child: Row(
                          children: [
                            Icon(
                              socket.isConnected ? Icons.link : Icons.link_off,
                              color: socket.isConnected
                                  ? const Color(0xFF4ADE80)
                                  : Colors.red,
                            ),
                            const SizedBox(width: 15),
                            Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  socket.isConnected
                                      ? "CONNECTED"
                                      : "DISCONNECTED",
                                  style: GoogleFonts.shareTechMono(
                                    color: Colors.white,
                                    fontSize: 16,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                                Text(
                                  // socket.socket?.io.uri ?? "Unknown URL", // uri access might be tricky depending on implementation
                                  "Socket.IO Gateway",
                                  style: GoogleFonts.outfit(
                                    color: Colors.white54,
                                    fontSize: 12,
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ),
                      );
                    },
                  ),

                  const SizedBox(height: 30),

                  // Permissions
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      _buildSectionHeader("PERMISSIONS"),
                      TextButton(
                        onPressed: _requestAll,
                        child: Text(
                          "GRANT ALL",
                          style: GoogleFonts.shareTechMono(
                            color: const Color(0xFF22D3EE),
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 10),
                  Expanded(
                    child: _isLoading
                        ? const Center(child: CircularProgressIndicator())
                        : ListView(
                            children: _statuses.entries.map((entry) {
                              return Padding(
                                padding: const EdgeInsets.only(bottom: 12.0),
                                child: _buildPermissionTile(
                                  entry.key,
                                  entry.value,
                                ),
                              );
                            }).toList(),
                          ),
                  ),

                  // System Settings Link
                  Center(
                    child: TextButton.icon(
                      onPressed: () => openAppSettings(),
                      icon: const Icon(Icons.settings, color: Colors.white54),
                      label: Text(
                        "OPEN SYSTEM SETTINGS",
                        style: GoogleFonts.outfit(color: Colors.white54),
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

  Widget _buildSectionHeader(String title) {
    return Text(
      title,
      style: GoogleFonts.outfit(
        color: const Color(0xFF22D3EE).withOpacity(0.7),
        fontSize: 12,
        fontWeight: FontWeight.w600,
        letterSpacing: 1.5,
      ),
    );
  }

  Widget _buildPermissionTile(Permission permission, PermissionStatus status) {
    final isGranted = status.isGranted;
    final color = isGranted
        ? const Color(0xFF4ADE80)
        : (status.isPermanentlyDenied ? Colors.red : Colors.orange);

    return _buildGlassCard(
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(_getPermissionIcon(permission), color: color, size: 20),
          ),
          const SizedBox(width: 15),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  permission.toString().split('.').last.toUpperCase(),
                  style: GoogleFonts.shareTechMono(
                    color: Colors.white,
                    fontSize: 16,
                  ),
                ),
                Text(
                  status.toString().split('.').last.toUpperCase(),
                  style: GoogleFonts.outfit(
                    color: color,
                    fontSize: 10,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ),
          if (!isGranted)
            IconButton(
              onPressed: () => _requestPermission(permission),
              icon: const Icon(Icons.refresh, color: Colors.white54),
            ),
        ],
      ),
    );
  }

  IconData _getPermissionIcon(Permission p) {
    if (p == Permission.camera) return Icons.camera_alt;
    if (p == Permission.microphone) return Icons.mic;
    if (p == Permission.phone) return Icons.phone;
    if (p == Permission.notification) return Icons.notifications;
    if (p == Permission.location) return Icons.location_on;
    return Icons.security;
  }

  Widget _buildGlassCard({required Widget child}) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(16),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
        child: Container(
          width: double.infinity,
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.white.withOpacity(0.05),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: Colors.white.withOpacity(0.1), width: 1),
          ),
          child: child,
        ),
      ),
    );
  }
}
