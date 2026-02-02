import 'dart:convert';
import 'dart:io';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/foundation.dart';
import 'package:open_app_file/open_app_file.dart';
import 'package:path_provider/path_provider.dart';
import 'socket_service.dart';

class FileService extends ChangeNotifier {
  final SocketService socketService;

  FileService(this.socketService);

  Future<void> receiveFile(String filename, String base64Data) async {
    try {
      final bytes = base64Decode(base64Data);
      final directory =
          await getExternalStorageDirectory() ??
          await getApplicationDocumentsDirectory();
      final filePath = '${directory.path}/$filename';

      final file = File(filePath);
      await file.writeAsBytes(bytes);

      debugPrint("FileService: Received and saved file to $filePath");

      // Open the file automatically
      await OpenAppFile.open(filePath);
    } catch (e) {
      debugPrint("FileService: Error receiving file: $e");
    }
  }

  Future<void> pickAndSendFile() async {
    try {
      FilePickerResult? result = await FilePicker.platform.pickFiles();

      if (result != null && result.files.single.path != null) {
        File file = File(result.files.single.path!);
        String filename = result.files.single.name;
        Uint8List bytes = await file.readAsBytes();
        String base64Data = base64Encode(bytes);

        if (socketService.isConnected) {
          socketService.socket?.emit('mobile:file_beam_response', {
            'filename': filename,
            'data': base64Data,
          });
          debugPrint("FileService: Beamed file '$filename' to desktop.");
        }
      } else {
        // User canceled the picker
        debugPrint("FileService: File picking canceled.");
      }
    } catch (e) {
      debugPrint("FileService: Error picking/sending file: $e");
    }
  }
}
