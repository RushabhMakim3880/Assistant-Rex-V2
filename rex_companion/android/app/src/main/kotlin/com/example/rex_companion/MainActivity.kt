package com.example.rex_companion

import android.Manifest
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.telecom.TelecomManager
import android.telephony.PhoneStateListener
import android.telephony.TelephonyManager
import androidx.annotation.NonNull
import androidx.core.app.ActivityCompat
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel
import android.provider.ContactsContract


class MainActivity: FlutterActivity() {
    private val CHANNEL = "com.rex.companion/telephony"
    private var methodChannel: MethodChannel? = null

    override fun configureFlutterEngine(@NonNull flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        
        methodChannel = MethodChannel(flutterEngine.dartExecutor.binaryMessenger, CHANNEL)
        methodChannel?.setMethodCallHandler { call, result ->
            when (call.method) {
                "answerCall" -> {
                    answerCall()
                    result.success(true)
                }
                "endCall" -> {
                    // Ending call is tricky on modern Android.
                    // We try TelecomManager first.
                    val telecomManager = getSystemService(Context.TELECOM_SERVICE) as TelecomManager
                    if (ActivityCompat.checkSelfPermission(this, Manifest.permission.ANSWER_PHONE_CALLS) == PackageManager.PERMISSION_GRANTED) {
                        try {
                            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
                                telecomManager.endCall()
                                result.success(true)
                            } else {
                                // Fallback for older Android (Not implemented)
                                result.error("UNSUPPORTED", "Auto-end not supported on this Android version", null)
                            }
                        } catch (e: Exception) {
                            result.error("ERROR", "Failed to end call: ${e.message}", null)
                        }
                    } else {
                        result.error("PERMISSION_DENIED", "Missing ANSWER_PHONE_CALLS permission", null)
                    }
                }
                "dialNumber" -> {
                    val number = call.argument<String>("number")
                    if (number != null) {
                        val intent = Intent(Intent.ACTION_CALL)
                        intent.data = Uri.parse("tel:$number")
                        if (ActivityCompat.checkSelfPermission(this, Manifest.permission.CALL_PHONE) == PackageManager.PERMISSION_GRANTED) {
                            startActivity(intent)
                            result.success(true)
                        } else {
                            result.error("PERMISSION_DENIED", "Missing CALL_PHONE permission", null)
                        }
                    } else {
                         result.error("JOJO", "Number is null", null)
                    }
                }
                "openApp" -> {
                    val appName = call.argument<String>("appName")
                    if (appName != null) {
                        val pm = packageManager
                        val packages = pm.getInstalledApplications(PackageManager.GET_META_DATA)
                        
                        // Prioritized Search
                        var exactMatch: String? = null
                        var startsWithMatch: String? = null
                        var containsMatch: String? = null
                        
                        val debugList = ArrayList<String>()

                        for (app in packages) {
                            val label = pm.getApplicationLabel(app).toString()
                            debugList.add(label)
                            
                            if (label.equals(appName, ignoreCase = true)) {
                                exactMatch = app.packageName
                                break 
                            }
                            
                            if (startsWithMatch == null && label.startsWith(appName, ignoreCase = true)) {
                                startsWithMatch = app.packageName
                            }
                            
                            if (containsMatch == null && label.contains(appName, ignoreCase = true)) {
                                containsMatch = app.packageName
                            }
                        }
                        
                        val bestMatch = exactMatch ?: startsWithMatch ?: containsMatch
                        
                        if (bestMatch != null) {
                             val launchIntent = pm.getLaunchIntentForPackage(bestMatch)
                             if (launchIntent != null) {
                                 startActivity(launchIntent)
                                 result.success(true)
                             } else {
                                 result.error("ERROR", "Cannot launch app (No Launch Intent)", null)
                             }
                        } else {
                             // Log potential matches for debugging
                             println("App '$appName' not found. Installed: ${debugList.take(10)}")
                             result.error("NOT_FOUND", "App not found", null)
                        }
                    } else {
                        result.error("INVALID_ARGUMENT", "App name cannot be null", null)
                    }
                }
                "goHome" -> {
                    val intent = Intent(Intent.ACTION_MAIN)
                    intent.addCategory(Intent.CATEGORY_HOME)
                    intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK
                    startActivity(intent)
                    result.success(true)
                }
                "searchContacts" -> {
                    val query = call.argument<String>("query") ?: ""
                    result.success(searchContacts(query))
                }
                "sendWhatsApp" -> {
                    val number = call.argument<String>("number")
                    val message = call.argument<String>("message")
                    if (number != null && message != null) {
                        try {
                            val uri = Uri.parse("https://api.whatsapp.com/send?phone=$number&text=${Uri.encode(message)}")
                            val intent = Intent(Intent.ACTION_VIEW, uri)
                            intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK
                            startActivity(intent)
                            result.success(true)
                        } catch (e: Exception) {
                            result.error("ERROR", "WhatsApp not installed or error: ${e.message}", null)
                        }
                    } else {
                        result.error("INVALID_ARGUMENT", "Number and message required", null)
                    }
                }
                "getContacts" -> {
                    result.success(getAllContacts())
                }
                "sendMessage" -> {
                    val number = call.argument<String>("number") ?: ""
                    val message = call.argument<String>("message") ?: ""
                    val platform = call.argument<String>("platform") ?: "whatsapp"
                    sendMessage(platform, number, message)
                    result.success(true)
                }
                "setClipboard" -> {
                    val text = call.argument<String>("text")
                    if (text != null) {
                        setClipboard(text)
                        result.success(true)
                    } else {
                        result.error("INVALID_ARGUMENT", "Text required", null)
                    }
                }
                "toggleFlash" -> {
                    val enable = call.argument<Boolean>("enable") ?: false
                    toggleFlash(enable)
                    result.success(true)
                }
                "setVolume" -> {
                    val level = call.argument<Int>("level") ?: 50
                    setVolume(level)
                    result.success(true)
                }
                "startListener" -> {
                    startPhoneListener()
                    result.success(true)
                }
                "setDND" -> {
                    val enable = call.argument<Boolean>("enable") ?: false
                    setDNDMode(enable)
                    result.success(true)
                }
                "getLocation" -> {
                    getLocation { location ->
                        if (location != null) {
                            result.success(mapOf(
                                "lat" to location.latitude,
                                "lng" to location.longitude
                            ))
                        } else {
                            result.error("UNAVAILABLE", "Location not available", null)
                        }
                    }
                }
                else -> result.notImplemented()
            }
        }
    }

    private fun answerCall() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val telecomManager = getSystemService(Context.TELECOM_SERVICE) as TelecomManager
            if (ActivityCompat.checkSelfPermission(this, Manifest.permission.ANSWER_PHONE_CALLS) == PackageManager.PERMISSION_GRANTED) {
                telecomManager.acceptRingingCall()
            }
        }
    }

    private fun getContactName(phoneNumber: String?): String {
        if (phoneNumber == null || phoneNumber.isEmpty()) return "Unknown"
        if (ActivityCompat.checkSelfPermission(this, Manifest.permission.READ_CONTACTS) != PackageManager.PERMISSION_GRANTED) {
            return phoneNumber
        }

        val uri = Uri.withAppendedPath(android.provider.ContactsContract.PhoneLookup.CONTENT_FILTER_URI, Uri.encode(phoneNumber))
        val projection = arrayOf(android.provider.ContactsContract.PhoneLookup.DISPLAY_NAME)
        
        contentResolver.query(uri, projection, null, null, null)?.use { cursor ->
            if (cursor.moveToFirst()) {
                return cursor.getString(0)
            }
        }
        return phoneNumber
    }

    private fun setVolume(level: Int) {
        val audioManager = getSystemService(Context.AUDIO_SERVICE) as android.media.AudioManager
        val maxVolume = audioManager.getStreamMaxVolume(android.media.AudioManager.STREAM_RING)
        val targetVolume = (level * maxVolume) / 100
        audioManager.setStreamVolume(android.media.AudioManager.STREAM_RING, targetVolume, 0)
    }

    private fun toggleFlash(enable: Boolean) {
        val cameraManager = getSystemService(Context.CAMERA_SERVICE) as android.hardware.camera2.CameraManager
        try {
            val cameraId = cameraManager.cameraIdList[0]
            cameraManager.setTorchMode(cameraId, enable)
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    private fun setClipboard(text: String) {
        val clipboard = getSystemService(Context.CLIPBOARD_SERVICE) as android.content.ClipboardManager
        val clip = android.content.ClipData.newPlainText("REX Clipboard", text)
        clipboard.setPrimaryClip(clip)
    }

    private fun setDNDMode(enable: Boolean) {
        val notificationManager = getSystemService(Context.NOTIFICATION_SERVICE) as android.app.NotificationManager
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            if (notificationManager.isNotificationPolicyAccessGranted) {
                val filter = if (enable) android.app.NotificationManager.INTERRUPTION_FILTER_NONE else android.app.NotificationManager.INTERRUPTION_FILTER_ALL
                notificationManager.setInterruptionFilter(filter)
            } else {
                // Request access if not granted
                val intent = Intent(android.provider.Settings.ACTION_NOTIFICATION_POLICY_ACCESS_SETTINGS)
                intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK
                startActivity(intent)
            }
        }
    }

    private fun getLocation(callback: (android.location.Location?) -> Unit) {
        if (ActivityCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
             callback(null)
             return
        }
        val locationManager = getSystemService(Context.LOCATION_SERVICE) as android.location.LocationManager
        val provider = android.location.LocationManager.GPS_PROVIDER
        
        try {
            val location = locationManager.getLastKnownLocation(provider)
            if (location != null) {
                callback(location)
            } else {
                locationManager.requestSingleUpdate(provider, object : android.location.LocationListener {
                    override fun onLocationChanged(loc: android.location.Location) {
                        callback(loc)
                    }
                    override fun onStatusChanged(p0: String?, p1: Int, p2: android.os.Bundle?) {}
                    override fun onProviderEnabled(p0: String) {}
                    override fun onProviderDisabled(p0: String) {}
                }, null)
            }
        } catch (e: Exception) {
            callback(null)
        }
    }

    private fun getAllContacts(): List<Map<String, String>> {
        val contacts = mutableListOf<Map<String, String>>()
        if (ActivityCompat.checkSelfPermission(this, Manifest.permission.READ_CONTACTS) != PackageManager.PERMISSION_GRANTED) {
            return contacts
        }

        val uri = android.provider.ContactsContract.CommonDataKinds.Phone.CONTENT_URI
        val projection = arrayOf(
            android.provider.ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME,
            android.provider.ContactsContract.CommonDataKinds.Phone.NUMBER
        )

        contentResolver.query(uri, projection, null, null, null)?.use { cursor ->
            val nameIndex = cursor.getColumnIndex(android.provider.ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME)
            val numberIndex = cursor.getColumnIndex(android.provider.ContactsContract.CommonDataKinds.Phone.NUMBER)
            
            while (cursor.moveToNext()) {
                contacts.add(mapOf(
                    "name" to cursor.getString(nameIndex),
                    "number" to cursor.getString(numberIndex)
                ))
            }
        }
        return contacts
    }

    private fun searchContacts(query: String): List<Map<String, String>> {
        val contacts = mutableListOf<Map<String, String>>()
        if (ActivityCompat.checkSelfPermission(this, Manifest.permission.READ_CONTACTS) != PackageManager.PERMISSION_GRANTED) {
            return contacts
        }

        val uri = android.provider.ContactsContract.CommonDataKinds.Phone.CONTENT_URI
        val projection = arrayOf(
            android.provider.ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME,
            android.provider.ContactsContract.CommonDataKinds.Phone.NUMBER

        )
        val selection = "${android.provider.ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME} LIKE ?"
        val selectionArgs = arrayOf("%$query%")

        contentResolver.query(uri, projection, selection, selectionArgs, null)?.use { cursor ->
            val nameIndex = cursor.getColumnIndex(android.provider.ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME)
            val numberIndex = cursor.getColumnIndex(android.provider.ContactsContract.CommonDataKinds.Phone.NUMBER)
            
            while (cursor.moveToNext()) {
                contacts.add(mapOf(
                    "name" to cursor.getString(nameIndex),
                    "number" to cursor.getString(numberIndex)
                ))
                if (contacts.size >= 10) break // Limit results
            }
        }
        return contacts
    }

    private fun sendMessage(platform: String, number: String, message: String) {
        val intent = when (platform) {
            "whatsapp" -> {
                val uri = android.net.Uri.parse("https://api.whatsapp.com/send?phone=$number&text=${android.net.Uri.encode(message)}")
                android.content.Intent(android.content.Intent.ACTION_VIEW, uri)
            }
            "telegram" -> {
                val uri = android.net.Uri.parse("tg://msg?text=${android.net.Uri.encode(message)}")
                android.content.Intent(android.content.Intent.ACTION_VIEW, uri)
            }
            "signal" -> {
                val uri = android.net.Uri.parse("sgnl://send?text=${android.net.Uri.encode(message)}")
                android.content.Intent(android.content.Intent.ACTION_VIEW, uri)
            }
            "sms" -> {
                val uri = android.net.Uri.parse("smsto:$number")
                android.content.Intent(android.content.Intent.ACTION_SENDTO, uri).apply {
                    putExtra("sms_body", message)
                }
            }
            else -> null
        }
        intent?.let {
            it.flags = android.content.Intent.FLAG_ACTIVITY_NEW_TASK
            startActivity(it)
        }
    }

    private fun startPhoneListener() {
        if (ActivityCompat.checkSelfPermission(this, Manifest.permission.READ_PHONE_STATE) != PackageManager.PERMISSION_GRANTED) {
            return
        }
        val telephonyManager = getSystemService(Context.TELEPHONY_SERVICE) as TelephonyManager
        
        val listener = object : PhoneStateListener() {
            override fun onCallStateChanged(state: Int, phoneNumber: String?) {
                var stateStr = "IDLE"
                when (state) {
                    TelephonyManager.CALL_STATE_RINGING -> stateStr = "RINGING"
                    TelephonyManager.CALL_STATE_OFFHOOK -> stateStr = "OFFHOOK"
                    TelephonyManager.CALL_STATE_IDLE -> stateStr = "IDLE"
                }
                
                val contactName = if (stateStr == "RINGING" || stateStr == "OFFHOOK") getContactName(phoneNumber) else ""

                methodChannel?.invokeMethod("callStateChanged", mapOf(
                    "state" to stateStr,
                    "number" to (phoneNumber ?: "Unknown"),
                    "name" to contactName
                ))
            }
        }
        
        telephonyManager.listen(listener, PhoneStateListener.LISTEN_CALL_STATE)
    }
}
