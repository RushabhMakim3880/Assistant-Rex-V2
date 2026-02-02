import asyncio
import queue
import time

class MobileBridge:
    def __init__(self, on_audio_data=None, on_call_state=None, on_notification=None, on_contact_results=None, on_location_results=None, on_camera_frame=None):
        self.connected_device_id = None
        self.audio_queue = queue.Queue()
        self.on_audio_data = on_audio_data
        self.on_call_state = on_call_state
        self.on_notification = on_notification
        self.on_contact_results = on_contact_results
        self.on_location_results = on_location_results
        self.on_camera_frame = on_camera_frame
        self.on_file_beam_response = None  # New callback
        self.on_audio_out = None
        self.is_active = False
        self.on_command = None

    def connect_device(self, device_id):
        self.connected_device_id = device_id
        self.is_active = True
        print(f"[MobileBridge] Device Connected: {device_id}")

    def disconnect_device(self):
        print(f"[MobileBridge] Device Disconnected: {self.connected_device_id}")
        self.connected_device_id = None
        self.is_active = False

    def receive_audio(self, data):
        """Receive PCM audio data from mobile."""
        if self.is_active:
            self.audio_queue.put(data)
            # Optional: direct pass-through if needed immediately
            # if self.on_audio_data:
            #     self.on_audio_data(data)

    def receive_call_state(self, state_data):
        """
        state_data: { 'state': 'RINGING'|'OFFHOOK'|'IDLE', 'number': '...' }
        """
        print(f"[MobileBridge] Call State: {state_data}")
        if self.on_call_state:
            res = self.on_call_state(state_data)
            if asyncio.iscoroutine(res):
                # Ensure we have a loop
                try:
                    loop = asyncio.get_running_loop()
                    loop.create_task(res)
                except RuntimeError:
                    # No loop running?
                    pass

    def receive_notification(self, notif_data):
        """
        notif_data: { 'package': '...', 'title': '...', 'text': '...' }
        """
        print(f"[MobileBridge] Notification: {notif_data}")
        if self.on_notification:
            self.on_notification(notif_data)

    def get_audio_chunk(self):
        """Retrieve audio from queue for processing by main loop."""
        try:
            return self.audio_queue.get_nowait()
        except queue.Empty:
            return None

    def has_audio(self):
        return not self.audio_queue.empty()

    def set_audio_output_handler(self, handler):
        self.on_audio_out = handler

    def send_audio(self, data):
        """Send audio to the connected mobile device."""
        if self.is_active and self.on_audio_out:
            # We assume on_audio_out is a callable that handles the actual sending (likely async)
            self.on_audio_out(data)

    def control_call(self, action):
        """Send call control command (answer/end/reject)."""
        if self.is_active and self.on_audio_out: # Revert reuse of audio_out for generic emit? 
            # Ideally we need a generic 'send_command' callback or access to sio
            # but for now we are stuck with 'on_audio_out' which is a hack.
            # Wait! server.py creates MobileBridge but doesn't pass 'emit'.
            # It only set 'set_audio_output_handler'.
            
            # Hack: We need a 'send_command' handler.
            pass
            
    # CRITICAL: We need a generic way to emit events from MobileBridge -> Server -> SocketIO
    # I'll add 'set_command_handler' similar to audio.
    
    def set_command_handler(self, handler):
        self.on_command = handler

    def control_call(self, action):
        if self.is_active and hasattr(self, 'on_command') and self.on_command:
            self.on_command('mobile:control_call', {'action': action})

    def dial_number(self, number):
        if self.is_active and hasattr(self, 'on_command') and self.on_command:
            self.on_command('mobile:dial', {'number': number})

    def open_app(self, app_name):
        if self.is_active and hasattr(self, 'on_command') and self.on_command:
            self.on_command('mobile:open_app', {'app_name': app_name})

    def go_home(self):
        if self.is_active and hasattr(self, 'on_command') and self.on_command:
            self.on_command('mobile:go_home', {})

    def search_contacts(self, query):
        if self.is_active and hasattr(self, 'on_command') and self.on_command:
            self.on_command('mobile:search_contacts', {'query': query})

    def send_message(self, number, message, platform='whatsapp'):
        if self.is_active and hasattr(self, 'on_command') and self.on_command:
            self.on_command('mobile:send_message', {'number': number, 'message': message, 'platform': platform})

    def get_contacts(self):
        if self.is_active and hasattr(self, 'on_command') and self.on_command:
            self.on_command('mobile:get_contacts', {})

    def set_clipboard(self, text):
        if self.is_active and hasattr(self, 'on_command') and self.on_command:
            self.on_command('mobile:set_clipboard', {'text': text})

    def hardware_control(self, action, value):
        if self.is_active and hasattr(self, 'on_command') and self.on_command:
            self.on_command('mobile:hardware_control', {'action': action, 'value': value})

    def start_mic(self):
        if self.is_active and hasattr(self, 'on_command') and self.on_command:
            self.on_command('mobile:start_audio', {})

    def stop_mic(self):
        if self.is_active and hasattr(self, 'on_command') and self.on_command:
            self.on_command('mobile:stop_audio', {})

    def get_location(self):
        if self.is_active and hasattr(self, 'on_command') and self.on_command:
            self.on_command('mobile:get_location', {})

    def set_dnd(self, enabled):
        if self.is_active and hasattr(self, 'on_command') and self.on_command:
            self.on_command('mobile:set_dnd', {'enable': enabled})

    def start_camera(self):
        if self.is_active and hasattr(self, 'on_command') and self.on_command:
            self.on_command('mobile:camera_control', {'action': 'start'})

    def stop_camera(self):
        if self.is_active and hasattr(self, 'on_command') and self.on_command:
            self.on_command('mobile:camera_control', {'action': 'stop'})

    def send_file(self, filename, base64_data):
        if self.is_active and hasattr(self, 'on_command') and self.on_command:
            self.on_command('mobile:file_beam', {
                'action': 'receive',
                'filename': filename,
                'data': base64_data
            })

    def request_file(self):
        if self.is_active and hasattr(self, 'on_command') and self.on_command:
            self.on_command('mobile:file_beam', {'action': 'request'})

    def handle_camera_frame(self, bytes_data):
        if self.on_camera_frame:
            self.on_camera_frame(bytes_data)

    def handle_file_beam_response(self, data):
        """Called when mobile beams a file back to desktop."""
        if hasattr(self, 'on_file_beam_response') and self.on_file_beam_response:
            self.on_file_beam_response(data)

    def handle_contact_results(self, data):
        """Called when mobile sends back contact search results."""
        if self.on_contact_results:
            self.on_contact_results(data)

    def handle_location_results(self, data):
        """Called when mobile sends back GPS coordinates."""
        if self.on_location_results:
            self.on_location_results(data)
