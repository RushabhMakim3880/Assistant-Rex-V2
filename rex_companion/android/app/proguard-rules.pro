# Flutter Wrapper
-keep class io.flutter.app.** { *; }
-keep class io.flutter.plugin.**  { *; }
-keep class io.flutter.util.**  { *; }
-keep class io.flutter.view.**  { *; }
-keep class io.flutter.**  { *; }
-keep class io.flutter.plugins.**  { *; }

# Socket.IO and OkHttp/Okio
-keep class io.socket.** { *; }
-keep class okhttp3.** { *; }
-keep class okio.** { *; }
-keep class org.json.** { *; }

# Prevent obfuscation of our own data models (if any)
-keep class com.example.rex_companion.** { *; }

# Flutter Sound (if we re-add it)
-keep class com.dooboolab.** { *; }

# Ignore warnings for Play Core (Dynamic Features) which we don't use
-dontwarn com.google.android.play.core.**
-dontwarn io.flutter.embedding.engine.deferredcomponents.**
