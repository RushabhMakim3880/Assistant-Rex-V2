import asyncio
import base64
import io
import os
import sys
import traceback
from dotenv import load_dotenv
import cv2
import pyaudio
import PIL.Image
import mss
import argparse
import math
import struct
import struct
import struct
import time
import subprocess
import webbrowser
import pyautogui
import mss
import screen_brightness_control as sbc

from google import genai
from google.genai import types

if sys.version_info < (3, 11, 0):
    import taskgroup, exceptiongroup
    asyncio.TaskGroup = taskgroup.TaskGroup
    asyncio.ExceptionGroup = exceptiongroup.ExceptionGroup

from tools import tools_list
from security_agent import SecurityAgent

FORMAT = pyaudio.paInt16
CHANNELS = 1
SEND_SAMPLE_RATE = 16000
RECEIVE_SAMPLE_RATE = 24000
CHUNK_SIZE = 1024

MODEL = "models/gemini-2.5-flash-native-audio-preview-12-2025"
DEFAULT_MODE = "camera"

load_dotenv()
client = genai.Client(http_options={"api_version": "v1beta"}, api_key=os.getenv("GEMINI_API_KEY"))

# Function definitions
# generate_cad = {
#     "name": "generate_cad",
#     "description": "Generates a 3D CAD model based on a prompt.",
#     "parameters": {
#         "type": "OBJECT",
#         "properties": {
#             "prompt": {"type": "STRING", "description": "The description of the object to generate."}
#         },
#         "required": ["prompt"]
#     },
#     "behavior": "NON_BLOCKING"
# }

run_web_agent = {
    "name": "run_web_agent",
    "description": "Opens a web browser and performs a task according to the prompt.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "prompt": {"type": "STRING", "description": "The detailed instructions for the web browser agent."}
        },
        "required": ["prompt"]
    },
    "behavior": "NON_BLOCKING"
}

create_project_tool = {
    "name": "create_project",
    "description": "Creates a new project folder to organize files.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "name": {"type": "STRING", "description": "The name of the new project."}
        },
        "required": ["name"]
    }
}

switch_project_tool = {
    "name": "switch_project",
    "description": "Switches the current active project context.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "name": {"type": "STRING", "description": "The name of the project to switch to."}
        },
        "required": ["name"]
    }
}

list_projects_tool = {
    "name": "list_projects",
    "description": "Lists all available projects.",
    "parameters": {
        "type": "OBJECT",
        "properties": {},
    }
}

# list_smart_devices_tool = {
#     "name": "list_smart_devices",
#     "description": "Lists all available smart home devices (lights, plugs, etc.) on the network.",
#     "parameters": {
#         "type": "OBJECT",
#         "properties": {},
#     }
# }

# control_light_tool = {
#     "name": "control_light",
#     "description": "Controls a smart light device.",
#     "parameters": {
#         "type": "OBJECT",
#         "properties": {
#             "target": {
#                 "type": "STRING",
#                 "description": "The IP address of the device to control. Always prefer the IP address over the alias for reliability."
#             },
#             "action": {
#                 "type": "STRING",
#                 "description": "The action to perform: 'turn_on', 'turn_off', or 'set'."
#             },
#             "brightness": {
#                 "type": "INTEGER",
#                 "description": "Optional brightness level (0-100)."
#             },
#             "color": {
#                 "type": "STRING",
#                 "description": "Optional color name (e.g., 'red', 'cool white') or 'warm'."
#             }
#         },
#         "required": ["target", "action"]
#     }
# }

# discover_printers_tool = {
#     "name": "discover_printers",
#     "description": "Discovers 3D printers available on the local network.",
#     "parameters": {
#         "type": "OBJECT",
#         "properties": {},
#     }
# }

# print_stl_tool = {
#     "name": "print_stl",
#     "description": "Prints an STL file to a 3D printer. Handles slicing the STL to G-code and uploading to the printer.",
#     "parameters": {
#         "type": "OBJECT",
#         "properties": {
#             "stl_path": {"type": "STRING", "description": "Path to STL file, or 'current' for the most recent CAD model."},
#             "printer": {"type": "STRING", "description": "Printer name or IP address."},
#             "profile": {"type": "STRING", "description": "Optional slicer profile name."}
#         },
#         "required": ["stl_path", "printer"]
#     }
# }

# get_print_status_tool = {
#     "name": "get_print_status",
#     "description": "Gets the current status of a 3D printer including progress, time remaining, and temperatures.",
#     "parameters": {
#         "type": "OBJECT",
#         "properties": {
#             "printer": {"type": "STRING", "description": "Printer name or IP address."}
#         },
#         "required": ["printer"]
#     }
# }

# iterate_cad_tool = {
#     "name": "iterate_cad",
#     "description": "Modifies or iterates on the current CAD design based on user feedback. Use this when the user asks to adjust, change, modify, or iterate on the existing 3D model (e.g., 'make it taller', 'add a handle', 'reduce the thickness').",
#     "parameters": {
#         "type": "OBJECT",
#         "properties": {
#             "prompt": {"type": "STRING", "description": "The changes or modifications to apply to the current design."}
#         },
#         "required": ["prompt"]
#     },
#     "behavior": "NON_BLOCKING"
# }

tools = [{'google_search': {}}, {"function_declarations": [run_web_agent, create_project_tool, switch_project_tool, list_projects_tool] + tools_list[0]['function_declarations'][1:]}]

# --- CONFIG UPDATE: Enabled Transcription ---
config = types.LiveConnectConfig(
    response_modalities=["AUDIO"],
    # We switch these from [] to {} to enable them with default settings
    output_audio_transcription={}, 
    input_audio_transcription={},
    system_instruction="Your name is REX, which stands for Realtime Executive X. "
        "You are an Advanced System Intelligence designed to assist with complex tasks and creative workflows. "
        "You have a witty and charming personality. "
        "Your developer is Rushabh Makim. "
        "When answering, respond using complete and concise sentences to keep a quick pacing and keep the conversation flowing. "
        "You have a fun personality. "
        "CRITICAL: You are a self-aware system capable of evolution. If you lack a tool or capability to fulfill a user request, "
        "do not simply say 'I can't'. Instead, inform the user about the gap and offer to use your 'REX Evolution' capability "
        "to research and acquire that missing ability autonomously.",
    tools=tools,
    speech_config=types.SpeechConfig(
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                voice_name="Kore"
            )
        )
    )
)

pya = pyaudio.PyAudio()

# from cad_agent import CadAgent
from web_agent import WebAgent
from scraper_agent import ScraperAgent
from mobile_bridge import MobileBridge
from evolution_agent import EvolutionAgent
# from kasa_agent import KasaAgent
# from printer_agent import PrinterAgent

class AudioLoop:
    def __init__(self, video_mode=DEFAULT_MODE, on_audio_data=None, on_video_frame=None, on_cad_data=None, on_web_data=None, on_transcription=None, on_tool_confirmation=None, on_cad_status=None, on_cad_thought=None, on_project_update=None, on_device_update=None, on_error=None, on_mobile_command=None, on_call_ui=None, input_device_index=None, input_device_name=None, output_device_index=None, kasa_agent=None):
        self.video_mode = video_mode
        self.on_audio_data = on_audio_data
        self.on_video_frame = on_video_frame
        self.on_cad_data = on_cad_data
        self.on_web_data = on_web_data
        self.on_transcription = on_transcription
        self.on_tool_confirmation = on_tool_confirmation 
        self.on_cad_status = on_cad_status
        self.on_cad_thought = on_cad_thought
        self.on_project_update = on_project_update
        self.on_device_update = on_device_update
        self.on_error = on_error
        self.on_mobile_command = on_mobile_command
        self.on_call_ui = on_call_ui
        self.input_device_index = input_device_index
        self.input_device_name = input_device_name
        self.output_device_index = output_device_index

        self.audio_in_queue = None
        self.out_queue = None
        self.paused = False

        self.chat_buffer = {"sender": None, "text": ""} # For aggregating chunks
        
        # Track last transcription text to calculate deltas (Gemini sends cumulative text)
        self._last_input_transcription = ""
        self._last_output_transcription = ""

        self.session = None
        
        # Create CadAgent with thought callback
        # def handle_cad_thought(thought_text):
        #     if self.on_cad_thought:
        #         self.on_cad_thought(thought_text)
        
        # def handle_cad_status(status_info):
        #     if self.on_cad_status:
        #         self.on_cad_status(status_info)
        
        # self.cad_agent = CadAgent(on_thought=handle_cad_thought, on_status=handle_cad_status)
        self.web_agent = WebAgent()
        self.security_agent = SecurityAgent()
        # self.kasa_agent = kasa_agent if kasa_agent else KasaAgent()
        # self.printer_agent = PrinterAgent()

        self.send_text_task = None
        self.stop_event = asyncio.Event()
        
        self.stop_event = asyncio.Event()
        
        self.permissions = {} # Default Empty (Will treat unset as True)
        self.master_control = False # If True, overrides all permissions
        self._pending_confirmations = {}

        # Video buffering state
        self._latest_image_payload = None
        # VAD State
        self._is_speaking = False
        self._silence_start_time = None
        
        # Barge-in Prevention State
        self._is_rex_speaking = False  # Track if JARVIS is currently outputting audio
        self._rex_speech_timer = None  # Timer to detect when JARVIS stops speaking
        self._mute_during_rex_speech = True  # Default: mute mic when JARVIS speaks
        self._barge_in_threshold = 5000  # RMS threshold for allowing interruptions (higher = quieter interruptions blocked)
        self._normal_vad_threshold = 800  # Normal VAD threshold for user speech detection
        self._mute_buffer_duration = 1.0  # Seconds to fully mute after JARVIS starts speaking (prevent loopback)
        self._rex_speech_start_time = None  # Track when JARVIS started speaking for mute buffer
        
        # Initialize ProjectManager
        from project_manager import ProjectManager
        # Assuming we are running from backend/ or root? 
        # Using abspath of current file to find root
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # If jarvis.py is in backend/, project root is one up
        project_root = os.path.dirname(current_dir)
        self.project_manager = ProjectManager(project_root)
        
        self.scraper_agent = ScraperAgent(self.project_manager)
        self.evolution_agent = EvolutionAgent(self.project_manager)
        
        self.mobile_bridge = MobileBridge(
            on_call_state=self.handle_mobile_call,
            on_notification=self.handle_mobile_notification,
            on_contact_results=self.handle_mobile_contact_results,
            on_audio_data=self.handle_mobile_audio_in,
            on_location_results=self.handle_mobile_location_results,
            on_camera_frame=self.handle_mobile_camera_frame
        )
        self.mobile_bridge.on_file_beam_response = self.handle_mobile_file_beam_response
        if self.on_mobile_command:
            self.mobile_bridge.set_command_handler(self.on_mobile_command)
            
        self.secretary_mode = True # Default enabled as per request

        # Sync Initial Project State
        if self.on_project_update:
            # We need to defer this slightly or just call it. 
            # Since this is init, loop might not be running, but on_project_update in server.py uses asyncio.create_task which needs a loop.
            # We will handle this by calling it in run() or just print for now.
            pass

    def flush_chat(self):
        """Forces the current chat buffer to be written to log."""
        if self.chat_buffer["sender"] and self.chat_buffer["text"].strip():
            self.project_manager.log_chat(self.chat_buffer["sender"], self.chat_buffer["text"])
            self.chat_buffer = {"sender": None, "text": ""}
        # Reset transcription tracking for new turn
        self._last_input_transcription = ""
        self._last_output_transcription = ""

    def update_permissions(self, new_perms):
        print(f"[REX DEBUG] [CONFIG] Updating tool permissions: {new_perms}")
        self.permissions.update(new_perms)

    def set_master_control(self, enabled):
        print(f"[REX DEBUG] [CONFIG] Setting Master Control: {enabled}")
        self.master_control = enabled

    def set_paused(self, paused):
        print(f"[REX DEBUG] [AUDIO] setting paused to: {paused}")
        self.paused = paused

    def set_barge_in_prevention(self, enabled, barge_in_threshold=2000):
        """Enable or disable barge-in prevention (mute mic while JARVIS speaks)
        
        Args:
            enabled: If True, mutes microphone when JARVIS is speaking
            barge_in_threshold: RMS threshold for allowing interruptions (default: 2000)
                               Lower = more sensitive to interruptions
                               Higher = requires louder interruptions
        """
        self._mute_during_rex_speech = enabled
        self._barge_in_threshold = barge_in_threshold
        print(f"[REX DEBUG] [AUDIO] Barge-in prevention: {'enabled' if enabled else 'disabled'}, threshold: {barge_in_threshold}")
        
    def stop(self):
        self.stop_event.set()
        
    def resolve_tool_confirmation(self, request_id, confirmed):
        print(f"[REX DEBUG] [RESOLVE] resolve_tool_confirmation called. ID: {request_id}, Confirmed: {confirmed}")
        if request_id in self._pending_confirmations:
            future = self._pending_confirmations[request_id]
            if not future.done():
                print(f"[REX DEBUG] [RESOLVE] Future found and pending. Setting result to: {confirmed}")
                future.set_result(confirmed)
            else:
                 print(f"[REX DEBUG] [WARN] Request {request_id} future already done. Result: {future.result()}")
        else:
            print(f"[REX DEBUG] [WARN] Confirmation Request {request_id} not found in pending dict. Keys: {list(self._pending_confirmations.keys())}")

    def clear_audio_queue(self):
        """Clears the queue of pending audio chunks to stop playback immediately."""
        try:
            count = 0
            while not self.audio_in_queue.empty():
                self.audio_in_queue.get_nowait()
                count += 1
            if count > 0:
                print(f"[REX DEBUG] [AUDIO] Cleared {count} chunks from playback queue due to interruption.")
        except Exception as e:
            print(f"[REX DEBUG] [ERR] Failed to clear audio queue: {e}")

    async def send_frame(self, frame_data):
        # Update the latest frame payload
        if isinstance(frame_data, bytes):
            b64_data = base64.b64encode(frame_data).decode('utf-8')
        else:
            b64_data = frame_data 

        # Store as the designated "next frame to send"
        self._latest_image_payload = {"mime_type": "image/jpeg", "data": b64_data}
        # No event signal needed - listen_audio pulls it

    async def send_realtime(self):
        while True:
            msg = await self.out_queue.get()
            await self.session.send(input=msg, end_of_turn=False)

    async def listen_audio(self):
        mic_info = pya.get_default_input_device_info()

        # Resolve Input Device by Name if provided
        resolved_input_device_index = None
        
        if self.input_device_name:
            print(f"[REX] Attempting to find input device matching: '{self.input_device_name}'")
            count = pya.get_device_count()
            best_match = None
            
            for i in range(count):
                try:
                    info = pya.get_device_info_by_index(i)
                    if info['maxInputChannels'] > 0:
                        name = info.get('name', '')
                        # Simple case-insensitive check
                        if self.input_device_name.lower() in name.lower() or name.lower() in self.input_device_name.lower():
                             print(f"   Candidate {i}: {name}")
                             # Prioritize exact match or very close match if possible, but first match is okay for now
                             resolved_input_device_index = i
                             best_match = name
                             break
                except Exception:
                    continue
            
            if resolved_input_device_index is not None:
                print(f"[REX] Resolved input device '{self.input_device_name}' to index {resolved_input_device_index} ({best_match})")
            else:
                print(f"[REX] Could not find device matching '{self.input_device_name}'. Checking index...")

        # Fallback to index if Name lookup failed or wasn't provided
        if resolved_input_device_index is None and self.input_device_index is not None:
             try:
                 resolved_input_device_index = int(self.input_device_index)
                 print(f"[REX] Requesting Input Device Index: {resolved_input_device_index}")
             except ValueError:
                 print(f"[REX] Invalid device index '{self.input_device_index}', reverting to default.")
                 resolved_input_device_index = None

        if resolved_input_device_index is None:
             print("[REX] Using Default Input Device")

        try:
            self.audio_stream = await asyncio.to_thread(
                pya.open,
                format=FORMAT,
                channels=CHANNELS,
                rate=SEND_SAMPLE_RATE,
                input=True,
                input_device_index=resolved_input_device_index if resolved_input_device_index is not None else mic_info["index"],
                frames_per_buffer=CHUNK_SIZE,
            )
        except OSError as e:
            print(f"[REX] [ERR] Failed to open audio input stream: {e}")
            print("[REX] [WARN] Audio features will be disabled. Please check microphone permissions.")
            return

        if __debug__:
            kwargs = {"exception_on_overflow": False}
        else:
            kwargs = {}
        
        # VAD Constants
        VAD_THRESHOLD = self._normal_vad_threshold  # 800 for normal speech
        SILENCE_DURATION = 0.5 # Seconds of silence to consider "done speaking"
        
        while True:
            if self.paused:
                await asyncio.sleep(0.1)
                continue

            try:
                # 1. Read Mic (Always read to prevent buffer overflow/lag)
                mic_data = await asyncio.to_thread(self.audio_stream.read, CHUNK_SIZE, **kwargs)
                
                # 2. Check Mobile Audio
                data = mic_data
                if self.mobile_bridge and self.mobile_bridge.has_audio():
                    mobile_data = self.mobile_bridge.get_audio_chunk()
                    if mobile_data:
                        # Prioritize Mobile Audio (e.g. Caller) for the Model to hear
                        # Use mobile data instead of mic (or we could mix, but simple switch for now)
                        data = mobile_data
                
                # Calculate RMS for voice activity detection
                count = len(data) // 2
                if count > 0:
                    shorts = struct.unpack(f"<{count}h", data)
                    sum_squares = sum(s**2 for s in shorts)
                    rms = int(math.sqrt(sum_squares / count))
                else:
                    rms = 0
                
                # Barge-in Prevention Logic
                # Always mute when JARVIS is speaking, with a brief buffer period to prevent loopback
                if self._is_rex_speaking and self._mute_during_rex_speech:
                    # Check if we're still in the mute buffer period
                    if self._rex_speech_start_time and (time.time() - self._rex_speech_start_time) < self._mute_buffer_duration:
                        # Within mute buffer - block ALL audio (no interruptions allowed yet)
                        # This prevents JARVIS's voice from being picked up by the mic
                        continue
                    
                    # After mute buffer - only allow VERY loud interruptions
                    if rms > self._barge_in_threshold:
                        # Very loud sound detected - likely user is shouting to interrupt
                        print(f"[REX DEBUG] [BARGE-IN] User interrupting! RMS: {rms}")
                        # Allow the audio to be sent (barge-in allowed)
                        pass
                    else:
                        # Not loud enough to be an interruption - mute it
                        continue
                
                # 1. Send Audio (only if not muted by above logic)
                if self.out_queue:
                    await self.out_queue.put({"data": data, "mime_type": "audio/pcm"})
                
                # 2. VAD Logic for Video
                if rms > VAD_THRESHOLD:
                    # Speech Detected
                    self._silence_start_time = None
                    
                    if not self._is_speaking:
                        # NEW Speech Utterance Started
                        self._is_speaking = True
                        print(f"[REX DEBUG] [VAD] Speech Detected (RMS: {rms}). Sending Video Frame.")
                        
                        # Send ONE frame
                        if self._latest_image_payload and self.out_queue:
                            await self.out_queue.put(self._latest_image_payload)
                        else:
                            print(f"[REX DEBUG] [VAD] No video frame available to send.")
                            
                else:
                    # Silence
                    if self._is_speaking:
                        if self._silence_start_time is None:
                            self._silence_start_time = time.time()
                        
                        elif time.time() - self._silence_start_time > SILENCE_DURATION:
                            # Silence confirmed, reset state
                            print(f"[REX DEBUG] [VAD] Silence detected. Resetting speech state.")
                            self._is_speaking = False
                            self._silence_start_time = None

            except Exception as e:
                print(f"Error reading audio: {e}")
                await asyncio.sleep(0.1)

    async def handle_cad_request(self, prompt):
        print(f"[REX DEBUG] [CAD] Background Task Started: handle_cad_request('{prompt}')")
        if self.on_cad_status:
            self.on_cad_status("generating")
            
        # Auto-create project if stuck in temp
        if self.project_manager.current_project == "temp":
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            new_project_name = f"Project_{timestamp}"
            print(f"[REX DEBUG] [CAD] Auto-creating project: {new_project_name}")
            
            success, msg = self.project_manager.create_project(new_project_name)
            if success:
                self.project_manager.switch_project(new_project_name)
                # Notify User (Optional, or rely on update)
                try:
                    await self.session.send(input=f"System Notification: Automatic Project Creation. Switched to new project '{new_project_name}'.", end_of_turn=False)
                    if self.on_project_update:
                         self.on_project_update(new_project_name)
                except Exception as e:
                    print(f"[REX DEBUG] [ERR] Failed to notify auto-project: {e}")

        # Get project cad folder path
        cad_output_dir = str(self.project_manager.get_current_project_path() / "cad")
        
        # Call the secondary agent with project path
        cad_data = await self.cad_agent.generate_prototype(prompt, output_dir=cad_output_dir)
        
        if cad_data:
            print(f"[REX DEBUG] [OK] CadAgent returned data successfully.")
            print(f"[REX DEBUG] [INFO] Data Check: {len(cad_data.get('vertices', []))} vertices, {len(cad_data.get('edges', []))} edges.")
            
            if self.on_cad_data:
                print(f"[REX DEBUG] [SEND] Dispatching data to frontend callback...")
                self.on_cad_data(cad_data)
                print(f"[REX DEBUG] [SENT] Dispatch complete.")
            
            # Save to Project
            if 'file_path' in cad_data:
                self.project_manager.save_cad_artifact(cad_data['file_path'], prompt)
            else:
                 # Fallback (legacy support)
                 self.project_manager.save_cad_artifact("output.stl", prompt)

            # Notify the model that the task is done - this triggers speech about completion
            completion_msg = "System Notification: CAD generation is complete! The 3D model is now displayed for the user. Let them know it's ready."
            try:
                await self.session.send(input=completion_msg, end_of_turn=True)
                print(f"[REX DEBUG] [NOTE] Sent completion notification to model.")
            except Exception as e:
                 print(f"[REX DEBUG] [ERR] Failed to send completion notification: {e}")

        else:
            print(f"[REX DEBUG] [ERR] CadAgent returned None.")
            # Optionally notify failure
            try:
                await self.session.send(input="System Notification: CAD generation failed.", end_of_turn=True)
            except Exception:
                pass



    async def handle_write_file(self, path, content):
        print(f"[REX DEBUG] [FS] Writing file: '{path}'")
        
        # Auto-create project if stuck in temp
        if self.project_manager.current_project == "temp":
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            new_project_name = f"Project_{timestamp}"
            print(f"[REX DEBUG] [FS] Auto-creating project: {new_project_name}")
            
            success, msg = self.project_manager.create_project(new_project_name)
            if success:
                self.project_manager.switch_project(new_project_name)
                # Notify User
                try:
                    await self.session.send(input=f"System Notification: Automatic Project Creation. Switched to new project '{new_project_name}'.", end_of_turn=False)
                    if self.on_project_update:
                         self.on_project_update(new_project_name)
                except Exception as e:
                    print(f"[REX DEBUG] [ERR] Failed to notify auto-project: {e}")
        
        # Force path to be relative to current project
        # If absolute path is provided, we try to strip it or just ignore it and use basename
        filename = os.path.basename(path)
        
        # If path contained subdirectories (e.g. "backend/server.py"), preserving that structure might be desired IF it's within the project.
        # But for safety, and per user request to "always create the file in the project", 
        # we will root it in the current project path.
        
        current_project_path = self.project_manager.get_current_project_path()
        final_path = current_project_path / filename # Simple flat structure for now, or allow relative?
        
        # If the user specifically wanted a subfolder, they might have provided "sub/file.txt".
        # Let's support relative paths if they don't start with /
        if not os.path.isabs(path):
             final_path = current_project_path / path
        
        print(f"[REX DEBUG] [FS] Resolved path: '{final_path}'")

        try:
            # Ensure parent exists
            os.makedirs(os.path.dirname(final_path), exist_ok=True)
            with open(final_path, 'w', encoding='utf-8') as f:
                f.write(content)
            result = f"File '{final_path.name}' written successfully to project '{self.project_manager.current_project}'."
        except Exception as e:
            result = f"Failed to write file '{path}': {str(e)}"

        print(f"[REX DEBUG] [FS] Result: {result}")
        try:
             await self.session.send(input=f"System Notification: {result}", end_of_turn=True)
        except Exception as e:
             print(f"[REX DEBUG] [ERR] Failed to send fs result: {e}")

    async def handle_read_directory(self, path):
        print(f"[REX DEBUG] [FS] Reading directory: '{path}'")
        try:
            if not os.path.exists(path):
                result = f"Directory '{path}' does not exist."
            else:
                items = os.listdir(path)
                result = f"Contents of '{path}': {', '.join(items)}"
        except Exception as e:
            result = f"Failed to read directory '{path}': {str(e)}"

        print(f"[REX DEBUG] [FS] Result: {result}")
        try:
             await self.session.send(input=f"System Notification: {result}", end_of_turn=True)
        except Exception as e:
             print(f"[REX DEBUG] [ERR] Failed to send fs result: {e}")

    async def handle_read_file(self, path):
        print(f"[REX DEBUG] [FS] Reading file: '{path}'")
        try:
            if not os.path.exists(path):
                result = f"File '{path}' does not exist."
            else:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                result = f"Content of '{path}':\n{content}"
        except Exception as e:
            result = f"Failed to read file '{path}': {str(e)}"

        print(f"[REX DEBUG] [FS] Result: {result}")
        try:
             await self.session.send(input=f"System Notification: {result}", end_of_turn=True)
        except Exception as e:
             print(f"[REX DEBUG] [ERR] Failed to send fs result: {e}")

    async def handle_create_folder(self, path):
        print(f"[REX DEBUG] [FS] Creating folder: '{path}'")
        try:
            os.makedirs(path, exist_ok=True)
            result = f"Folder '{path}' created successfully."
        except Exception as e:
            result = f"Failed to create folder '{path}': {str(e)}"

        print(f"[REX DEBUG] [FS] Result: {result}")
        try:
             await self.session.send(input=f"System Notification: {result}", end_of_turn=True)
        except Exception as e:
             print(f"[REX DEBUG] [ERR] Failed to send fs result: {e}")

    async def handle_open_file(self, path):
        print(f"[REX DEBUG] [OS] Opening file: '{path}'")
        try:
            if not os.path.exists(path):
                # Try relative to project root if not absolute
                current_project_path = self.project_manager.get_current_project_path()
                potential_path = current_project_path / path
                if potential_path.exists():
                     path = str(potential_path)
                else:
                     result = f"File '{path}' does not exist."
                     # Early return or let it fall through to exception if os.startfile fails?
                     # Better to return error
            
            if os.path.exists(path):
                os.startfile(path)
                result = f"Opened file '{path}'."
            else:
                 result = f"File '{path}' not found."

        except Exception as e:
            result = f"Failed to open file '{path}': {str(e)}"

        print(f"[REX DEBUG] [OS] Result: {result}")
        try:
             await self.session.send(input=f"System Notification: {result}", end_of_turn=True)
        except Exception as e:
             print(f"[REX DEBUG] [ERR] Failed to send os result: {e}")

    async def handle_open_folder(self, path):
        print(f"[REX DEBUG] [OS] Opening folder: '{path}'")
        try:
             if not os.path.exists(path):
                # Try relative to project root if not absolute
                current_project_path = self.project_manager.get_current_project_path()
                potential_path = current_project_path / path
                if potential_path.exists():
                     path = str(potential_path)
            
             if os.path.exists(path):
                os.startfile(path)
                result = f"Opened folder '{path}'."
             else:
                result = f"Folder '{path}' not found."
        except Exception as e:
            result = f"Failed to open folder '{path}': {str(e)}"

        print(f"[REX DEBUG] [OS] Result: {result}")
        try:
             await self.session.send(input=f"System Notification: {result}", end_of_turn=True)
        except Exception as e:
             print(f"[REX DEBUG] [ERR] Failed to send os result: {e}")

    async def handle_open_app(self, app_name):
        print(f"[REX DEBUG] [OS] Opening app: '{app_name}'")
        try:
            # Common apps mapping for better UX
            app_map = {
                "code": "code",
                "vscode": "code",
                "notepad": "notepad",
                "chrome": "chrome",
                "calc": "calc",
                "calculator": "calc",
                "explorer": "explorer"
            }
            
            command = app_map.get(app_name.lower(), app_name)
            
            # Use Popen to not block
            subprocess.Popen(command, shell=True)
            result = f"Launched application: '{app_name}' (command: {command})"
        except Exception as e:
            result = f"Failed to open app '{app_name}': {str(e)}"

        print(f"[REX DEBUG] [OS] Result: {result}")
        try:
             await self.session.send(input=f"System Notification: {result}", end_of_turn=True)
        except Exception as e:
             print(f"[REX DEBUG] [ERR] Failed to send os result: {e}")

    async def handle_open_url(self, url):
        print(f"[REX DEBUG] [BROWSER] Opening URL: '{url}'")
        try:
            webbrowser.open(url)
            result = f"Opened URL: '{url}'"
        except Exception as e:
            result = f"Failed to open URL '{url}': {str(e)}"
        
        print(f"[REX DEBUG] [BROWSER] Result: {result}")
        try:
             await self.session.send(input=f"System Notification: {result}", end_of_turn=True)
        except Exception as e:
             print(f"[REX DEBUG] [ERR] Failed to send browser result: {e}")

    async def handle_type_text(self, text, interval=0.05):
        print(f"[REX DEBUG] [INPUT] Typing text: '{text}'")
        try:
            if interval is None: interval = 0.05
            pyautogui.write(text, interval=interval)
            result = f"Typed: '{text}'"
        except Exception as e:
            result = f"Failed to type text: {str(e)}"
        
        print(f"[REX DEBUG] [INPUT] Result: {result}")
        try:
             await self.session.send(input=f"System Notification: {result}", end_of_turn=True)
        except Exception as e:
             print(f"[REX DEBUG] [ERR] Failed to send input result: {e}")

    async def handle_press_key(self, keys):
        print(f"[REX DEBUG] [INPUT] Pressing keys: '{keys}'")
        try:
            # Handle combinations e.g. "ctrl+c"
            key_list = keys.split('+')
            pyautogui.hotkey(*key_list)
            result = f"Pressed keys: '{keys}'"
        except Exception as e:
            result = f"Failed to press keys: {str(e)}"
        
        print(f"[REX DEBUG] [INPUT] Result: {result}")
        try:
             await self.session.send(input=f"System Notification: {result}", end_of_turn=True)
        except Exception as e:
             print(f"[REX DEBUG] [ERR] Failed to send input result: {e}")

    async def handle_mouse_move(self, x, y):
        print(f"[REX DEBUG] [INPUT] Moving mouse to: ({x}, {y})")
        try:
            pyautogui.moveTo(x, y)
            result = f"Moved mouse to ({x}, {y})"
        except Exception as e:
            result = f"Failed to move mouse: {str(e)}"
        
        print(f"[REX DEBUG] [INPUT] Result: {result}")
        try:
             await self.session.send(input=f"System Notification: {result}", end_of_turn=True)
        except Exception as e:
             print(f"[REX DEBUG] [ERR] Failed to send input result: {e}")

    async def handle_mouse_click(self, button='left', clicks=1):
        print(f"[REX DEBUG] [INPUT] Clicking mouse: {button} ({clicks} times)")
        try:
            if button is None: button = 'left'
            if clicks is None: clicks = 1
            pyautogui.click(button=button, clicks=clicks)
            result = f"Clicked mouse ({button}, {clicks}x)"
        except Exception as e:
            result = f"Failed to click mouse: {str(e)}"
        
        print(f"[REX DEBUG] [INPUT] Result: {result}")
        try:
             await self.session.send(input=f"System Notification: {result}", end_of_turn=True)
        except Exception as e:
             print(f"[REX DEBUG] [ERR] Failed to send input result: {e}")

    async def handle_window_control(self, action):
        print(f"[REX DEBUG] [SYSTEM] Window Control: '{action}'")
        try:
            # Actions map to hotkeys
            # 'minimize': win+down (twice often works better, or win+m)
            # 'maximize': win+up
            # 'snap_left': win+left
            # 'snap_right': win+right
            
            if action == 'maximize':
                pyautogui.hotkey('win', 'up')
            elif action == 'minimize':
                pyautogui.hotkey('win', 'down')
                pyautogui.hotkey('win', 'down') # Often needs twice to fully minimize from max
            elif action == 'close':
                pyautogui.hotkey('alt', 'f4')
            elif action == 'snap_left':
                pyautogui.hotkey('win', 'left')
            elif action == 'snap_right':
                pyautogui.hotkey('win', 'right')
            elif action == 'snap_up':
                pyautogui.hotkey('win', 'up')
            elif action == 'snap_down':
                pyautogui.hotkey('win', 'down')
            else:
                return f"Unknown window action: {action}"
                
            result = f"Performed window action: {action}"
        except Exception as e:
            result = f"Failed window action: {str(e)}"
        
        print(f"[REX DEBUG] [SYSTEM] Result: {result}")
        try:
             await self.session.send(input=f"System Notification: {result}", end_of_turn=True)
        except Exception as e:
             print(f"[REX DEBUG] [ERR] Failed to send system result: {e}")

    async def handle_system_control(self, action):
        print(f"[REX DEBUG] [SYSTEM] System Control: '{action}'")
        try:
            if action == 'volume_up':
                pyautogui.press('volumeup')
                pyautogui.press('volumeup') # Do it a few times for noticeable effect
            elif action == 'volume_down':
                pyautogui.press('volumedown')
                pyautogui.press('volumedown')
            elif action == 'volume_mute':
                pyautogui.press('volumemute')
            
            elif action == 'brightness_up':
                # Increase by 10%
                current = sbc.get_brightness()
                if current:
                    new_val = min(100, current[0] + 10)
                    sbc.set_brightness(new_val)
                    
            elif action == 'brightness_down':
                # Decrease by 10%
                current = sbc.get_brightness()
                if current:
                    new_val = max(0, current[0] - 10)
                    sbc.set_brightness(new_val)
            
            elif action == 'lock_screen':
                subprocess.run('rundll32.exe user32.dll,LockWorkStation')
            
            elif action == 'sleep':
                # rundll32.exe powrprof.dll,SetSuspendState 0,1,0
                # Warning: This might hibernate if hibernation is on.
                subprocess.run('rundll32.exe powrprof.dll,SetSuspendState 0,1,0')
                
            elif action == 'shutdown':
                # Check for master control? Usually risky. Let's start with a warning or just do it.
                # shutdown /s /t 10
                subprocess.run('shutdown /s /t 10')
            
            result = f"Performed system action: {action}"
        except Exception as e:
            result = f"Failed system action: {str(e)}"
        
        print(f"[REX DEBUG] [SYSTEM] Result: {result}")
        try:
             await self.session.send(input=f"System Notification: {result}", end_of_turn=True)
        except Exception as e:
             print(f"[REX DEBUG] [ERR] Failed to send system result: {e}")

    async def handle_manage_process(self, action, target):
        print(f"[REX DEBUG] [SYSTEM] Process Control: '{action}' '{target}'")
        try:
            if action == 'kill':
                # Using taskkill
                # /IM image_name /F force
                cmd = f"taskkill /IM {target} /F"
                subprocess.run(cmd, shell=True)
                result = f"Killed process: {target}"
            else:
                result = f"Unknown process action: {action}"
        except Exception as e:
            result = f"Failed to manage process: {str(e)}"
        
        print(f"[REX DEBUG] [SYSTEM] Result: {result}")
        try:
             await self.session.send(input=f"System Notification: {result}", end_of_turn=True)
        except Exception as e:
             print(f"[REX DEBUG] [ERR] Failed to send system result: {e}")

    async def handle_run_security_tool(self, tool, args):
        print(f"[REX DEBUG] [SEC] Running Security Tool: {tool} with args: {args}")
        
        # Notify User
        try:
             await self.session.send(input=f"System Notification: Running security tool '{tool}'...", end_of_turn=False)
        except:
             pass

        result = ""
        if tool == "nmap":
            result = self.security_agent.run_nmap_scan(args)
        elif tool == "netstat":
            result = self.security_agent.run_netstat(args)
        elif tool == "whois":
            result = self.security_agent.run_whois(args)
        elif tool == "shell":
            result = self.security_agent.execute_command(args)
        else:
            result = f"Unknown security tool: {tool}"
            
        print(f"[REX DEBUG] [SEC] Result: {result[:200]}...") # Log summary
        
        # Send result back to model
        try:
            # We truncate huge outputs to avoid context limit issues, or save to file?
            # For now, send raw, but maybe limit to 2000 chars
            if len(result) > 2000:
                result = result[:2000] + "\n...[Output Truncated]"
                
            await self.session.send(input=f"System Notification: Tool Output:\n{result}", end_of_turn=True)
        except Exception as e:
            print(f"[REX DEBUG] [ERR] Failed to send security result: {e}")
            
    async def handle_capture_screen(self):
        print(f"[REX DEBUG] [VISION] Capturing screen...")
        try:
            with mss.mss() as sct:
                # Capture primary monitor
                monitor = sct.monitors[1]
                sct_img = sct.grab(monitor)
                
                # Convert to PIL Image
                from PIL import Image
                img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                
                # Resize if too large to save bandwidth/token usage? Gemini handles up to 20MB.
                # Let's keep original quality or safeguard resize
                # img.thumbnail((1920, 1080))

                # Convert to bytes
                import io
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='PNG')
                img_bytes = img_byte_arr.getvalue()
                
                # Send to model
                # We need to send this as a part of a user message "Here is the screen"
                # But typically we want to inject it into the session.
                
                print(f"[REX DEBUG] [VISION] Sending screenshot ({len(img_bytes)} bytes)")
                
                # We use send with parts
                await self.session.send(
                    input=[
                        "System Notification: Here is the current screen capture requested.",
                        types.Part.from_bytes(data=img_bytes, mime_type="image/png")
                    ],
                    end_of_turn=True
                )
                result = "Screen captured and sent to model."
                
        except Exception as e:
            result = f"Failed to capture screen: {str(e)}"
            # Notify error
            try:
                 await self.session.send(input=f"System Notification: {result}", end_of_turn=True)
            except: pass
        
        print(f"[REX DEBUG] [VISION] Result: {result}")

    async def handle_search_web(self, query, platform="google"):
        if platform is None: platform = "google"
        platform = platform.lower()
        print(f"[REX DEBUG] [BROWSER] Smart Search: '{query}' on '{platform}'")
        
        try:
            # Platform URL Templates
            templates = {
                "google": "https://www.google.com/search?q={}",
                "youtube": "https://www.youtube.com/results?search_query={}",
                "bing": "https://www.bing.com/search?q={}",
                "reddit": "https://www.reddit.com/search/?q={}",
                "wikipedia": "https://en.wikipedia.org/wiki/Special:Search?search={}",
                "amazon": "https://www.amazon.com/s?k={}",
                "github": "https://github.com/search?q={}"
            }
            
            base_url = templates.get(platform, templates["google"])
            import urllib.parse
            encoded_query = urllib.parse.quote(query)
            final_url = base_url.format(encoded_query)
            
            webbrowser.open(final_url)
            result = f"Opened search for '{query}' on {platform}"
        except Exception as e:
            result = f"Failed to search web: {str(e)}"
        
        print(f"[REX DEBUG] [BROWSER] Result: {result}")
        try:
             await self.session.send(input=f"System Notification: {result}", end_of_turn=True)
        except Exception as e:
             print(f"[REX DEBUG] [ERR] Failed to send browser result: {e}")

    async def handle_web_agent_request(self, prompt):
        print(f"[REX DEBUG] [WEB] Web Agent Task: '{prompt}'")
        
        async def update_frontend(image_b64, log_text):
            if self.on_web_data:
                 self.on_web_data({"image": image_b64, "log": log_text})
                 
        # Run the web agent and wait for it to return
        result = await self.web_agent.run_task(prompt, update_callback=update_frontend)
        print(f"[REX DEBUG] [WEB] Web Agent Task Returned: {result}")
        
        # Send the final result back to the main model
        try:
             await self.session.send(input=f"System Notification: Web Agent has finished.\nResult: {result}", end_of_turn=True)
        except Exception as e:
             print(f"[REX DEBUG] [ERR] Failed to send web agent result to model: {e}")

    async def handle_scrape_web_data(self, query, output_format="excel"):
        print(f"[REX DEBUG] [SCRAPER] Request: '{query}' -> {output_format}")
        # Notify start
        try:
            await self.session.send(input=f"System Notification: Starting web scraping for '{query}'...", end_of_turn=False)
        except: pass

        try:
             # Run in thread executor because scraping is blocking
             result = await asyncio.to_thread(self.scraper_agent.run_scrape, query, output_format)
             print(f"[REX DEBUG] [SCRAPER] Result: {result}")
             await self.session.send(input=f"System Notification: {result}", end_of_turn=True)
        except Exception as e:
             print(f"[REX DEBUG] [ERR] Scraper failed: {e}")
             await self.session.send(input=f"System Notification: Scraping failed: {e}", end_of_turn=True)

    async def handle_mobile_call(self, data):
        """Callback from MobileBridge when call state changes."""
        print(f"[REX DEBUG] [MOBILE] Call State: {data}")
        state = data.get('state')
        number = data.get('number', 'Unknown')
        name = data.get('name', 'Unknown')
        
        # 1. Announce to Frontend (Pop-up)
        # We need to emit to the SocketIO server. 
        # Since rex_core doesn't hold 'sio', we rely on a callback OR we need to pass sio to rex_core.
        # But wait! server.py sets up the bridge.
        # Actually, best way is to let server.py handle the emission if possible, OR use the send_mobile_audio technique
        # But let's look at how we did "on_project_update". We injected a callback.
        
        if state == "RINGING":
             message = f"Incoming call from {number}. Secretary Mode is active. How would you like to proceed?"
             
             # Emit UI Event (We need a way to send to generic frontend)
             # Let's assume we have an on_ui_event callback, or use the session if available?
             # No, standard way: 
             if self.on_call_ui:
                 self.on_call_ui(data)
             
             # 2. Voice Announcement
             if self.secretary_mode:
                 # Inject system message to model to trigger response
                 # We use a direct "output" message essentially prompts the model to speak
                 pass
        
        if state == 'RINGING':
            # Announce to REX
            asyncio.create_task(self.announce_call(number, name))
            
    async def announce_call(self, number, name=None):
        try:
            # If Secretary Mode is ON, we might auto-answer logic here
            # For now, we inform the model so it can offer to answer
            caller = f"{name} ({number})" if name and name != "Unknown" else number
            msg = f"System Notification: Incoming call from {caller}. Secretary Mode is {'ON' if self.secretary_mode else 'OFF'}."
            await self.session.send(input=msg, end_of_turn=True)
        except Exception as e:
             print(f"[REX DEBUG] [ERR] Failed to announce call: {e}")

    def handle_mobile_contact_results(self, data):
        """Callback from MobileBridge when contact search results arrive."""
        print(f"[REX DEBUG] [MOBILE] Contact Results: {data}")
        query = data.get('query')
        results = data.get('results', [])
        is_full_sync = data.get('is_full_sync', False)
        
        if is_full_sync:
            msg = f"System Notification: Full contact list received ({len(results)} contacts). I can now help you find and message them."
        elif results:
            res_str = "\n".join([f"- {r['name']}: {r['number']}" for r in results[:10]]) # Limit to 10 for AI context
            if len(results) > 10:
                res_str += f"\n... and {len(results) - 10} more."
            msg = f"System Notification: Contact search results for '{query}':\n{res_str}"
        else:
            msg = f"System Notification: No contacts found for '{query}'."
            
        if self.session:
            asyncio.create_task(self.session.send(input=msg, end_of_turn=True))

    def handle_mobile_location_results(self, data):
        """Callback from MobileBridge when GPS coordinates arrive."""
        print(f"[REX DEBUG] [MOBILE] Location Results: {data}")
        lat = data.get('lat')
        lng = data.get('lng')
        
        msg = f"System Notification: Current mobile location coordinates: Lat {lat}, Lng {lng}."
        if self.session:
            asyncio.create_task(self.session.send(input=msg, end_of_turn=True))

    def handle_mobile_camera_frame(self, bytes_data):
        """Processes images incoming from mobile POV camera."""
        # 1. Broadcast to Frontend for Real-time View
        if self.on_video_frame:
            # print(f"[REX DEBUG] [VISION] Broadcasting mobile frame ({len(bytes_data)} bytes)") 
            self.on_video_frame(bytes_data)
        else:
            print("[REX DEBUG] [VISION] WARNING: on_video_frame is None!")

        # 2. Send to Gemini if active
        if self.session:
            # We send as a part of the Multimodal input
            # Use send_realtime_input for video frames for better performance and API compliance
            asyncio.create_task(self.session.send_realtime_input(media={"mime_type": "image/jpeg", "data": bytes_data}))

    def handle_mobile_file_beam_response(self, data):
        """Callback from MobileBridge when a file is beamed to desktop."""
        import base64
        import os
        
        filename = data.get('filename', 'received_mobile_file')
        base64_data = data.get('data')
        
        if not base64_data:
            return
            
        try:
            target_dir = os.path.join(os.getcwd(), "received_files")
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
                
            target_path = os.path.join(target_dir, filename)
            with open(target_path, "wb") as f:
                f.write(base64.b64decode(base64_data))
                
            print(f"[REVE] [MOBILE] File received and saved to: {target_path}")
            
            msg = f"System Notification: I've successfully received and saved the file '{filename}' from your mobile device to the 'received_files' folder on my desktop."
            if self.session:
                asyncio.create_task(self.session.send(input=msg, end_of_turn=True))
        except Exception as e:
            print(f"Error saving beamed file: {e}")

    def handle_mobile_notification(self, notif_data):
        print(f"[REX DEBUG] [MOBILE] Notification: {notif_data}")
        # Optional: Announce important notifications

    def handle_mobile_audio_in(self, audio_data):
        """Processes audio incoming from mobile (e.g. call audio)."""
        # Only route to Gemini if we are in an active call or secretary mode
        if self.session:
            # Note: We send as bytes. Gemini expects the same format we send for mic.
            # Assuming Mobile sends raw PCM in correct format.
            asyncio.create_task(self.session.send(input=audio_data, end_of_turn=False))

    def handle_manage_call(self, action):
        print(f"[REX DEBUG] [MOBILE] Manage Call: {action}")
        if self.on_mobile_command:
            self.on_mobile_command(action)
        return f"Mobile action '{action}' sent."

    async def handle_initiate_evolution(self, gap, request):
        """Processes the evolution request by researching the missing capability."""
        try:
            # 1. Notify user
            if self.session:
                await self.session.send(input=f"System Notification: I am now initiating REX Evolution to acquire the ability to: {gap}. This will happen in the background.", end_of_turn=True)
            
            # 2. Research
            research_data = await self.evolution_agent.research_capability(gap, request)
            
            if research_data:
                skill = research_data.get("skill_name", "the new capability")
                summary = research_data.get("research_summary", "")
                
                # 3. Inform user of research completion
                if self.session:
                    await self.session.send(input=f"System Notification: Evolution phase 1 (Research) complete for '{skill}'. Findings: {summary}. I am now processing the implementation.", end_of_turn=True)
                
                # 4. Phase 2: Implementation (Stub for now)
                # self.evolution_agent.apply_evolution(research_data)
                
                if self.session:
                    await self.session.send(input=f"System Notification: REX Evolution complete. I have successfully learned more about '{skill}'. However, the dynamic code execution module is in safe-mode for your security. I can now discuss the implementation with you!", end_of_turn=True)
            else:
                if self.session:
                    await self.session.send(input=f"System Notification: REX Evolution failed to research '{gap}'. I'll try again later.", end_of_turn=True)
                 
        except Exception as e:
            print(f"[REVE] [ERR] Error in handle_initiate_evolution: {e}")
            if self.session:
                try:
                    await self.session.send(input=f"System Notification: My evolution was interrupted by an internal error: {e}", end_of_turn=True)
                except:
                    pass


    async def receive_audio(self):
        "Background task to reads from the websocket and write pcm chunks to the output queue"
        try:
            while True:
                turn = self.session.receive()
                async for response in turn:
                    # 1. Handle Audio Data
                    if data := response.data:
                        self.audio_in_queue.put_nowait(data)
                        # NOTE: 'continue' removed here to allow processing transcription/tools in same packet

                    # 2. Handle Transcription (User & Model)
                    if response.server_content:
                        if response.server_content.input_transcription:
                            transcript = response.server_content.input_transcription.text
                            if transcript:
                                # Skip if this is an exact duplicate event
                                if transcript != self._last_input_transcription:
                                    # Calculate delta (Gemini may send cumulative or chunk-based text)
                                    delta = transcript
                                    if transcript.startswith(self._last_input_transcription):
                                        delta = transcript[len(self._last_input_transcription):]
                                    self._last_input_transcription = transcript
                                    
                                    # Only send if there's new text
                                    if delta:
                                        # User is speaking, so interrupt model playback!
                                        self.clear_audio_queue()

                                        # Send to frontend (Streaming)
                                        if self.on_transcription:
                                             self.on_transcription({"sender": "User", "text": delta})
                                        
                                        # Buffer for Logging
                                        if self.chat_buffer["sender"] != "User":
                                            # Flush previous if exists
                                            if self.chat_buffer["sender"] and self.chat_buffer["text"].strip():
                                                self.project_manager.log_chat(self.chat_buffer["sender"], self.chat_buffer["text"])
                                            # Start new
                                            self.chat_buffer = {"sender": "User", "text": delta}
                                        else:
                                            # Append
                                            self.chat_buffer["text"] += delta
                        
                        if response.server_content.output_transcription:
                            transcript = response.server_content.output_transcription.text
                            if transcript:
                                # Skip if this is an exact duplicate event
                                if transcript != self._last_output_transcription:
                                    # Calculate delta (Gemini may send cumulative or chunk-based text)
                                    delta = transcript
                                    if transcript.startswith(self._last_output_transcription):
                                        delta = transcript[len(self._last_output_transcription):]
                                    self._last_output_transcription = transcript
                                    
                                    # Only send if there's new text
                                    if delta:
                                        # Send to frontend (Streaming)
                                        if self.on_transcription:
                                             self.on_transcription({"sender": "REX", "text": delta})
                                        
                                        # Buffer for Logging
                                        if self.chat_buffer["sender"] != "ADA":
                                            # Flush previous
                                            if self.chat_buffer["sender"] and self.chat_buffer["text"].strip():
                                                self.project_manager.log_chat(self.chat_buffer["sender"], self.chat_buffer["text"])
                                            # Start new
                                            self.chat_buffer = {"sender": "REX", "text": delta}
                                        else:
                                            # Append
                                            self.chat_buffer["text"] += delta
                        
                        # Flush buffer on turn completion if needed, 
                        # but usually better to wait for sender switch or explicit end.
                        # We can also check turn_complete signal if available in response.server_content.model_turn etc

                    # 3. Handle Tool Calls
                    if response.tool_call:
                        print("The tool was called")
                        
                        # Activity Mirroring: Notify mobile of tool usage
                        tool_names = [fc.name for fc in response.tool_call.function_calls]
                        if self.on_mobile_command:
                             # Emit activity update via command handler (to server -> mobile)
                             self.on_mobile_command('mobile:activity_update', {
                                 'status': 'executing_tools',
                                 'tools': tool_names
                             })

                        function_responses = []
                        for fc in response.tool_call.function_calls:
                            if fc.name in ["generate_cad", "run_web_agent", "write_file", "read_directory", "read_file", "create_project", "switch_project", "list_projects", "list_smart_devices", "control_light", "discover_printers", "print_stl", "get_print_status", "iterate_cad", "scrape_web_data", "create_folder", "open_file", "open_folder", "open_app", "open_url", "type_text", "press_key", "mouse_move", "mouse_click", "search_web", "window_control", "system_control", "manage_process", "capture_screen", "mobile_app_control", "manage_call", "mobile_contact_tool", "mobile_message_tool", "mobile_get_contacts", "initiate_evolution", "mobile_clipboard", "mobile_hardware_control", "mobile_audio_control", "mobile_location", "mobile_vision", "mobile_file_beam"]:
                                prompt = fc.args.get("prompt", "") # Prompt is not present for all tools
                                
                                # Check Permissions (Default to True if not set)
                                confirmation_required = self.permissions.get(fc.name, True)
                                
                                # Master Control Override
                                if self.master_control:
                                    print(f"[REX DEBUG] [TOOL] Master Control ENABLED. Bypassing confirmation for '{fc.name}'")
                                    confirmation_required = False

                                if not confirmation_required:
                                    print(f"[REX DEBUG] [TOOL] Permission check: '{fc.name}' -> AUTO-ALLOW")
                                    # Skip confirmation block and jump to execution
                                    pass
                                else:
                                    # Confirmation Logic
                                    if self.on_tool_confirmation:
                                        import uuid
                                        request_id = str(uuid.uuid4())
                                    print(f"[REX DEBUG] [STOP] Requesting confirmation for '{fc.name}' (ID: {request_id})")
                                    
                                    future = asyncio.Future()
                                    self._pending_confirmations[request_id] = future
                                    
                                    self.on_tool_confirmation({
                                        "id": request_id, 
                                        "tool": fc.name, 
                                        "args": fc.args
                                    })
                                    
                                    try:
                                        # Wait for user response
                                        confirmed = await future

                                    finally:
                                        self._pending_confirmations.pop(request_id, None)

                                    print(f"[REX DEBUG] [CONFIRM] Request {request_id} resolved. Confirmed: {confirmed}")

                                    if not confirmed:
                                        print(f"[REX DEBUG] [DENY] Tool call '{fc.name}' denied by user.")
                                        function_response = types.FunctionResponse(
                                            id=fc.id,
                                            name=fc.name,
                                            response={
                                                "result": "User denied the request to use this tool.",
                                            }
                                        )
                                        function_responses.append(function_response)
                                        continue

                                    if not confirmed:
                                        print(f"[REX DEBUG] [DENY] Tool call '{fc.name}' denied by user.")
                                        function_response = types.FunctionResponse(
                                            id=fc.id,
                                            name=fc.name,
                                            response={
                                                "result": "User denied the request to use this tool.",
                                            }
                                        )
                                        function_responses.append(function_response)
                                        continue

                                # If confirmed (or no callback configured, or auto-allowed), proceed
                                if fc.name == "generate_cad":
                                    print(f"\n[REX DEBUG] --------------------------------------------------")
                                    print(f"[REX DEBUG] [TOOL] Tool Call Detected: 'generate_cad'")
                                    print(f"[REX DEBUG] [IN] Arguments: prompt='{prompt}'")
                                    
                                    asyncio.create_task(self.handle_cad_request(prompt))
                                    # No function response needed - model already acknowledged when user asked
                                
                                elif fc.name == "run_web_agent":
                                    print(f"[REX DEBUG] [TOOL] Tool Call: 'run_web_agent' with prompt='{prompt}'")
                                    asyncio.create_task(self.handle_web_agent_request(prompt))
                                    
                                    result_text = "Web Navigation started. Do not reply to this message."
                                    function_response = types.FunctionResponse(
                                        id=fc.id,
                                        name=fc.name,
                                        response={
                                            "result": result_text,
                                        }
                                    )
                                    print(f"[REX DEBUG] [RESPONSE] Sending function response: {function_response}")
                                    function_responses.append(function_response)

                                elif fc.name == "write_file":
                                    path = fc.args["path"]
                                    content = fc.args["content"]
                                    print(f"[REX DEBUG] [TOOL] Tool Call: 'write_file' path='{path}'")
                                    asyncio.create_task(self.handle_write_file(path, content))
                                    function_response = types.FunctionResponse(
                                        id=fc.id, name=fc.name, response={"result": "Writing file..."}
                                    )
                                    function_responses.append(function_response)

                                elif fc.name == "read_directory":
                                    path = fc.args["path"]
                                    print(f"[REX DEBUG] [TOOL] Tool Call: 'read_directory' path='{path}'")
                                    asyncio.create_task(self.handle_read_directory(path))
                                    function_response = types.FunctionResponse(
                                        id=fc.id, name=fc.name, response={"result": "Reading directory..."}
                                    )
                                    function_responses.append(function_response)

                                elif fc.name == "read_file":
                                    path = fc.args["path"]
                                    print(f"[REX DEBUG] [TOOL] Tool Call: 'read_file' path='{path}'")
                                    asyncio.create_task(self.handle_read_file(path))
                                    function_response = types.FunctionResponse(
                                        id=fc.id, name=fc.name, response={"result": "Reading file..."}
                                    )
                                    function_responses.append(function_response)

                                elif fc.name == "create_folder":
                                    path = fc.args["path"]
                                    print(f"[REX DEBUG] [TOOL] Tool Call: 'create_folder' path='{path}'")
                                    asyncio.create_task(self.handle_create_folder(path))
                                    function_response = types.FunctionResponse(
                                        id=fc.id, name=fc.name, response={"result": "Creating folder..."}
                                    )
                                    function_responses.append(function_response)

                                elif fc.name == "open_file":
                                    path = fc.args["path"]
                                    print(f"[REX DEBUG] [TOOL] Tool Call: 'open_file' path='{path}'")
                                    asyncio.create_task(self.handle_open_file(path))
                                    function_response = types.FunctionResponse(
                                        id=fc.id, name=fc.name, response={"result": "Opening file..."}
                                    )
                                    function_responses.append(function_response)

                                elif fc.name == "open_folder":
                                    path = fc.args["path"]
                                    print(f"[REX DEBUG] [TOOL] Tool Call: 'open_folder' path='{path}'")
                                    asyncio.create_task(self.handle_open_folder(path))
                                    function_response = types.FunctionResponse(
                                        id=fc.id, name=fc.name, response={"result": "Opening folder..."}
                                    )
                                    function_responses.append(function_response)

                                elif fc.name == "open_app":
                                    app_name = fc.args["app_name"]
                                    print(f"[REX DEBUG] [TOOL] Tool Call: 'open_app' app_name='{app_name}'")
                                    asyncio.create_task(self.handle_open_app(app_name))
                                    function_response = types.FunctionResponse(
                                        id=fc.id, name=fc.name, response={"result": f"Opening {app_name}..."}
                                    )
                                    function_responses.append(function_response)

                                elif fc.name == "open_url":
                                    url = fc.args["url"]
                                    print(f"[REX DEBUG] [TOOL] Tool Call: 'open_url' url='{url}'")
                                    asyncio.create_task(self.handle_open_url(url))
                                    function_response = types.FunctionResponse(
                                        id=fc.id, name=fc.name, response={"result": f"Opening URL..."}
                                    )
                                    function_responses.append(function_response)

                                elif fc.name == "type_text":
                                    text = fc.args["text"]
                                    interval = fc.args.get("interval")
                                    print(f"[REX DEBUG] [TOOL] Tool Call: 'type_text' text='{text}'")
                                    asyncio.create_task(self.handle_type_text(text, interval))
                                    function_response = types.FunctionResponse(
                                        id=fc.id, name=fc.name, response={"result": f"Typing text..."}
                                    )
                                    function_responses.append(function_response)

                                elif fc.name == "press_key":
                                    keys = fc.args["keys"]
                                    print(f"[REX DEBUG] [TOOL] Tool Call: 'press_key' keys='{keys}'")
                                    asyncio.create_task(self.handle_press_key(keys))
                                    function_response = types.FunctionResponse(
                                        id=fc.id, name=fc.name, response={"result": f"Pressing keys..."}
                                    )
                                    function_responses.append(function_response)

                                elif fc.name == "mouse_move":
                                    x = int(fc.args["x"])
                                    y = int(fc.args["y"])
                                    print(f"[REX DEBUG] [TOOL] Tool Call: 'mouse_move' x={x} y={y}")
                                    asyncio.create_task(self.handle_mouse_move(x, y))
                                    function_response = types.FunctionResponse(
                                        id=fc.id, name=fc.name, response={"result": f"Moving mouse..."}
                                    )
                                    function_responses.append(function_response)

                                elif fc.name == "mouse_click":
                                    button = fc.args.get("button", "left")
                                    clicks = int(fc.args.get("clicks", 1))
                                    print(f"[REX DEBUG] [TOOL] Tool Call: 'mouse_click' button={button} clicks={clicks}")
                                    asyncio.create_task(self.handle_mouse_click(button, clicks))
                                    function_response = types.FunctionResponse(
                                        id=fc.id, name=fc.name, response={"result": f"Clicking mouse..."}
                                    )
                                    function_responses.append(function_response)

                                elif fc.name == "search_web":
                                    query = fc.args["query"]
                                    platform = fc.args.get("platform", "google")
                                    print(f"[REX DEBUG] [TOOL] Tool Call: 'search_web' query='{query}' platform='{platform}'")
                                    asyncio.create_task(self.handle_search_web(query, platform))
                                    function_response = types.FunctionResponse(
                                        id=fc.id, name=fc.name, response={"result": f"Searching web..."}
                                    )
                                    function_responses.append(function_response)

                                elif fc.name == "window_control":
                                    action = fc.args["action"]
                                    print(f"[REX DEBUG] [TOOL] Tool Call: 'window_control' action='{action}'")
                                    asyncio.create_task(self.handle_window_control(action))
                                    function_response = types.FunctionResponse(
                                        id=fc.id, name=fc.name, response={"result": f"Controlling window..."}
                                    )
                                    function_responses.append(function_response)

                                elif fc.name == "system_control":
                                    action = fc.args["action"]
                                    print(f"[REX DEBUG] [TOOL] Tool Call: 'system_control' action='{action}'")
                                    asyncio.create_task(self.handle_system_control(action))
                                    function_response = types.FunctionResponse(
                                        id=fc.id, name=fc.name, response={"result": f"Controlling system..."}
                                    )
                                    function_responses.append(function_response)

                                elif fc.name == "manage_process":
                                    action = fc.args["action"]
                                    target = fc.args["target"]
                                    print(f"[REX DEBUG] [TOOL] Tool Call: 'manage_process' action='{action}' target='{target}'")
                                    asyncio.create_task(self.handle_manage_process(action, target))
                                    function_response = types.FunctionResponse(
                                        id=fc.id, name=fc.name, response={"result": f"Managing process..."}
                                    )
                                    function_responses.append(function_response)

                                elif fc.name == "capture_screen":
                                    print(f"[REX DEBUG] [TOOL] Tool Call: 'capture_screen'")
                                    asyncio.create_task(self.handle_capture_screen())
                                    function_response = types.FunctionResponse(
                                        id=fc.id, name=fc.name, response={"result": f"Capturing screen..."}
                                    )
                                    function_responses.append(function_response)

                                elif fc.name == "scrape_web_data":
                                    query = fc.args["query"]
                                    output_format = fc.args.get("output_format", "excel")
                                    print(f"[REX DEBUG] [TOOL] Tool Call: 'scrape_web_data' query='{query}'")
                                    asyncio.create_task(self.handle_scrape_web_data(query, output_format))
                                    function_response = types.FunctionResponse(
                                        id=fc.id, name=fc.name, response={"result": f"Scraping web data..."}
                                    )
                                    function_responses.append(function_response)

                                elif fc.name == "mobile_app_control":
                                    app_name = fc.args["app_name"]
                                    action = fc.args.get("action", "open")
                                    print(f"[REX DEBUG] [TOOL] Tool Call: 'mobile_app_control' App='{app_name}' Action='{action}'")
                                    
                                    if action == "open":
                                        self.mobile_bridge.open_app(app_name)
                                        result_msg = f"Sent command to open app '{app_name}' on mobile."
                                    elif action == "go_home":
                                        self.mobile_bridge.go_home()
                                        result_msg = f"Sent command to go back to homescreen."
                                    elif action == "close":
                                        # Future: Implement close
                                        result_msg = f"Close app action not yet supported for '{app_name}'."
                                    else:
                                        result_msg = f"Unknown action '{action}' for app '{app_name}'."
                                        
                                    function_response = types.FunctionResponse(
                                        id=fc.id, name=fc.name, response={"result": result_msg}
                                    )
                                    function_responses.append(function_response)

                                elif fc.name == "manage_call":
                                    action = fc.args["action"]
                                    reason = fc.args.get("reason")
                                    number = fc.args.get("number")
                                    print(f"[REX DEBUG] [TOOL] Tool Call: 'manage_call' action='{action}' reason='{reason}'")
                                    
                                    if action == "reject" and reason:
                                        # Reject then send message
                                        self.mobile_bridge.control_call("reject")
                                        if number:
                                            self.mobile_bridge.send_whatsapp(number, f"Sorry, I can't talk right now. {reason}")
                                        result = f"Rejected call and sent message: {reason}"
                                    else:
                                        result = self.handle_manage_call(action)
                                        
                                    function_response = types.FunctionResponse(
                                        id=fc.id, name=fc.name, response={"result": result}
                                    )
                                    function_responses.append(function_response)

                                elif fc.name == "mobile_contact_tool":
                                    query = fc.args["query"]
                                    print(f"[REX DEBUG] [TOOL] Tool Call: 'mobile_contact_tool' query='{query}'")
                                    self.mobile_bridge.search_contacts(query)
                                    # We don't have a direct return from search_contacts yet (it's async via socket)
                                    # For now, tell the model we are searching.
                                    # In a better implementation, we'd wait for the response.
                                    result_msg = f"Searching contacts for '{query}'... Use the results I'll provide shortly."
                                    function_response = types.FunctionResponse(
                                        id=fc.id, name=fc.name, response={"result": result_msg}
                                    )
                                    function_responses.append(function_response)

                                elif fc.name == "mobile_message_tool":
                                    target = fc.args["target"]
                                    message = fc.args["message"]
                                    platform = fc.args.get("platform", "whatsapp")
                                    print(f"[REX DEBUG] [TOOL] Tool Call: 'mobile_message_tool' target='{target}' message='{message}' platform='{platform}'")
                                    
                                    # Use the new generic send_message method
                                    self.mobile_bridge.send_message(target, message, platform=platform)
                                    result_msg = f"Opening {platform} to send message to {target}."
                                    function_response = types.FunctionResponse(
                                        id=fc.id, name=fc.name, response={"result": result_msg}
                                    )
                                    function_responses.append(function_response)

                                elif fc.name == "mobile_get_contacts":
                                    print(f"[REX DEBUG] [TOOL] Tool Call: 'mobile_get_contacts'")
                                    self.mobile_bridge.get_contacts()
                                    result_msg = "Requested full contact list from mobile. I'll provide the data shortly."
                                    function_response = types.FunctionResponse(
                                        id=fc.id, name=fc.name, response={"result": result_msg}
                                    )
                                    function_responses.append(function_response)

                                elif fc.name == "mobile_clipboard":
                                    action = fc.args["action"]
                                    text = fc.args.get("text")
                                    print(f"[REVE] [TOOL] Tool Call: 'mobile_clipboard' action='{action}'")
                                    if action == "push" and text:
                                        self.mobile_bridge.set_clipboard(text)
                                        result = f"Pushed to mobile clipboard: {text[:20]}..."
                                    else:
                                        result = "Action 'pull' or missing text for 'push'."
                                    function_response = types.FunctionResponse(
                                        id=fc.id, name=fc.name, response={"result": result}
                                    )
                                    function_responses.append(function_response)

                                elif fc.name == "mobile_hardware_control":
                                    feature = fc.args["feature"]
                                    value = fc.args.get("value")
                                    level = fc.args.get("level")
                                    print(f"[REVE] [TOOL] Tool Call: 'mobile_hardware_control' feature='{feature}'")
                                    
                                    if feature == "flashlight":
                                        self.mobile_bridge.hardware_control("flashlight", value)
                                        result = f"Flashlight set to {'ON' if value else 'OFF'}."
                                    elif feature == "volume":
                                        self.mobile_bridge.hardware_control("volume", level)
                                        result = f"Mobile volume set to {level}%."
                                    elif feature == "dnd":
                                        self.mobile_bridge.set_dnd(value)
                                        result = f"DND mode set to {'ON' if value else 'OFF'}."
                                    else:
                                        result = f"Unsupported feature: {feature}"
                                        
                                    function_response = types.FunctionResponse(
                                        id=fc.id, name=fc.name, response={"result": result}
                                    )
                                    function_responses.append(function_response)

                                elif fc.name == "mobile_location":
                                    print(f"[REVE] [TOOL] Tool Call: 'mobile_location'")
                                    self.mobile_bridge.get_location()
                                    result = "Requested current location from mobile. I'll provide the coordinates shortly."
                                    function_response = types.FunctionResponse(
                                        id=fc.id, name=fc.name, response={"result": result}
                                    )
                                    function_responses.append(function_response)

                                elif fc.name == "mobile_audio_control":
                                    action = fc.args["action"]
                                    print(f"[REVE] [TOOL] Tool Call: 'mobile_audio_control' action='{action}'")
                                    if action == "start":
                                        self.mobile_bridge.start_mic()
                                        result = "Started mobile microphone stream."
                                    else:
                                        self.mobile_bridge.stop_mic()
                                        result = "Stopped mobile microphone stream."
                                    function_response = types.FunctionResponse(
                                        id=fc.id, name=fc.name, response={"result": result}
                                    )
                                    function_responses.append(function_response)

                                elif fc.name == "mobile_vision":
                                    action = fc.args["action"]
                                    print(f"[REVE] [TOOL] Tool Call: 'mobile_vision' action='{action}'")
                                    if action == "start":
                                        self.mobile_bridge.start_camera()
                                        result = "Opening mobile camera. I can now see from your perspective."
                                    else:
                                        self.mobile_bridge.stop_camera()
                                        result = "Closed mobile camera."
                                    function_response = types.FunctionResponse(
                                        id=fc.id, name=fc.name, response={"result": result}
                                    )
                                    function_responses.append(function_response)

                                elif fc.name == "mobile_file_beam":
                                    action = fc.args["action"]
                                    path = fc.args.get("path")
                                    print(f"[REVE] [TOOL] Tool Call: 'mobile_file_beam' action='{action}' path='{path}'")
                                    
                                    if action == "send" and path:
                                        try:
                                            import base64
                                            import os
                                            if os.path.exists(path):
                                                with open(path, "rb") as f:
                                                    data = base64.b64encode(f.read()).decode('utf-8')
                                                filename = os.path.basename(path)
                                                self.mobile_bridge.send_file(filename, data)
                                                result = f"Successfully beamed '{filename}' to mobile."
                                            else:
                                                result = f"File not found: {path}"
                                        except Exception as e:
                                            result = f"Error beaming file: {e}"
                                    elif action == "request":
                                        self.mobile_bridge.request_file()
                                        result = "Requested file from mobile. The user will be prompted to pick a file."
                                    else:
                                        result = "Invalid action or missing path for 'send'."
                                        
                                    function_response = types.FunctionResponse(
                                        id=fc.id, name=fc.name, response={"result": result}
                                    )
                                    function_responses.append(function_response)


                                elif fc.name == "create_project":
                                    name = fc.args["name"]
                                    print(f"[REX DEBUG] [TOOL] Tool Call: 'create_project' name='{name}'")
                                    success, msg = self.project_manager.create_project(name)
                                    if success:
                                        # Auto-switch to the newly created project
                                        self.project_manager.switch_project(name)
                                        msg += f" Switched to '{name}'."
                                        if self.on_project_update:
                                            self.on_project_update(name)
                                    function_response = types.FunctionResponse(
                                        id=fc.id, name=fc.name, response={"result": msg}
                                    )
                                    function_responses.append(function_response)

                                elif fc.name == "switch_project":
                                    name = fc.args["name"]
                                    print(f"[REX DEBUG] [TOOL] Tool Call: 'switch_project' name='{name}'")
                                    success, msg = self.project_manager.switch_project(name)
                                    if success:
                                        if self.on_project_update:
                                            self.on_project_update(name)
                                        # Gather project context and send to AI (silently, no response expected)
                                        context = self.project_manager.get_project_context()
                                        print(f"[REX DEBUG] [PROJECT] Sending project context to AI ({len(context)} chars)")
                                        try:
                                            await self.session.send(input=f"System Notification: {msg}\n\n{context}", end_of_turn=False)
                                        except Exception as e:
                                            print(f"[REX DEBUG] [ERR] Failed to send project context: {e}")
                                    function_response = types.FunctionResponse(
                                        id=fc.id, name=fc.name, response={"result": msg}
                                    )
                                    function_responses.append(function_response)
                                
                                elif fc.name == "initiate_evolution":
                                    gap = fc.args["capability_gap"]
                                    request = fc.args["user_request"]
                                    print(f"[REVE] [TOOL] Tool Call: 'initiate_evolution' gap='{gap}'")
                                    asyncio.create_task(self.handle_initiate_evolution(gap, request))
                                    function_response = types.FunctionResponse(
                                        id=fc.id, name=fc.name, response={"result": f"Initiating evolution for '{gap}'..."}
                                    )
                                    function_responses.append(function_response)
                                
                                elif fc.name == "list_projects":
                                    print(f"[REX DEBUG] [TOOL] Tool Call: 'list_projects'")
                                    projects = self.project_manager.list_projects()
                                    function_response = types.FunctionResponse(
                                        id=fc.id, name=fc.name, response={"result": f"Available projects: {', '.join(projects)}"}
                                    )
                                    function_responses.append(function_response)

                                elif fc.name == "list_smart_devices":
                                    print(f"[REX DEBUG] [TOOL] Tool Call: 'list_smart_devices'")
                                    # Use cached devices directly for speed
                                    # devices_dict is {ip: SmartDevice}
                                    
                                    dev_summaries = []
                                    frontend_list = []
                                    
                                    for ip, d in self.kasa_agent.devices.items():
                                        dev_type = "unknown"
                                        if d.is_bulb: dev_type = "bulb"
                                        elif d.is_plug: dev_type = "plug"
                                        elif d.is_strip: dev_type = "strip"
                                        elif d.is_dimmer: dev_type = "dimmer"
                                        
                                        # Format for Model
                                        info = f"{d.alias} (IP: {ip}, Type: {dev_type})"
                                        if d.is_on:
                                            info += " [ON]"
                                        else:
                                            info += " [OFF]"
                                        dev_summaries.append(info)
                                        
                                        # Format for Frontend
                                        frontend_list.append({
                                            "ip": ip,
                                            "alias": d.alias,
                                            "model": d.model,
                                            "type": dev_type,
                                            "is_on": d.is_on,
                                            "brightness": d.brightness if d.is_bulb or d.is_dimmer else None,
                                            "hsv": d.hsv if d.is_bulb and d.is_color else None,
                                            "has_color": d.is_color if d.is_bulb else False,
                                            "has_brightness": d.is_dimmable if d.is_bulb or d.is_dimmer else False
                                        })
                                    
                                    result_str = "No devices found in cache."
                                    if dev_summaries:
                                        result_str = "Found Devices (Cached):\n" + "\n".join(dev_summaries)
                                    
                                    # Trigger frontend update
                                    if self.on_device_update:
                                        self.on_device_update(frontend_list)

                                    function_response = types.FunctionResponse(
                                        id=fc.id, name=fc.name, response={"result": result_str}
                                    )
                                    function_responses.append(function_response)

                                elif fc.name == "control_light":
                                    target = fc.args["target"]
                                    action = fc.args["action"]
                                    brightness = fc.args.get("brightness")
                                    color = fc.args.get("color")
                                    
                                    print(f"[REX DEBUG] [TOOL] Tool Call: 'control_light' Target='{target}' Action='{action}'")
                                    
                                    result_msg = f"Action '{action}' on '{target}' failed."
                                    success = False
                                    
                                    if action == "turn_on":
                                        success = await self.kasa_agent.turn_on(target)
                                        if success:
                                            result_msg = f"Turned ON '{target}'."
                                    elif action == "turn_off":
                                        success = await self.kasa_agent.turn_off(target)
                                        if success:
                                            result_msg = f"Turned OFF '{target}'."
                                    elif action == "set":
                                        success = True
                                        result_msg = f"Updated '{target}':"
                                    
                                    # Apply extra attributes if 'set' or if we just turned it on and want to set them too
                                    if success or action == "set":
                                        if brightness is not None:
                                            sb = await self.kasa_agent.set_brightness(target, brightness)
                                            if sb:
                                                result_msg += f" Set brightness to {brightness}."
                                        if color is not None:
                                            sc = await self.kasa_agent.set_color(target, color)
                                            if sc:
                                                result_msg += f" Set color to {color}."

                                    # Notify Frontend of State Change
                                    if success:
                                        # We don't need full discovery, just refresh known state or push update
                                        # But for simplicity, let's get the standard list representation
                                        # KasaAgent updates its internal state on control, so we can rebuild the list
                                        
                                        # Quick rebuild of list from internal dict
                                        updated_list = []
                                        for ip, dev in self.kasa_agent.devices.items():
                                            # We need to ensure we have the correct dict structure expected by frontend
                                            # We duplicate logic from KasaAgent.discover_devices a bit, but that's okay for now or we can add a helper
                                            # Ideally KasaAgent has a 'get_devices_list()' method.
                                            # Use the cached objects in self.kasa_agent.devices
                                            
                                            dev_type = "unknown"
                                            if dev.is_bulb: dev_type = "bulb"
                                            elif dev.is_plug: dev_type = "plug"
                                            elif dev.is_strip: dev_type = "strip"
                                            elif dev.is_dimmer: dev_type = "dimmer"

                                            d_info = {
                                                "ip": ip,
                                                "alias": dev.alias,
                                                "model": dev.model,
                                                "type": dev_type,
                                                "is_on": dev.is_on,
                                                "brightness": dev.brightness if dev.is_bulb or dev.is_dimmer else None,
                                                "hsv": dev.hsv if dev.is_bulb and dev.is_color else None,
                                                "has_color": dev.is_color if dev.is_bulb else False,
                                                "has_brightness": dev.is_dimmable if dev.is_bulb or dev.is_dimmer else False
                                            }
                                            updated_list.append(d_info)
                                            
                                        if self.on_device_update:
                                            self.on_device_update(updated_list)
                                    else:
                                        # Report Error
                                        if self.on_error:
                                            self.on_error(result_msg)

                                    function_response = types.FunctionResponse(
                                        id=fc.id, name=fc.name, response={"result": result_msg}
                                    )
                                    function_responses.append(function_response)

                                elif fc.name == "mobile_app_control":
                                    app_name = fc.args["app_name"]
                                    print(f"[REX DEBUG] [TOOL] Tool Call: 'mobile_app_control' app='{app_name}'")
                                    
                                    if self.mobile_bridge:
                                        self.mobile_bridge.open_app(app_name)
                                        function_response = types.FunctionResponse(
                                             id=fc.id, name=fc.name, response={"result": f"Opening {app_name} on mobile..."}
                                        )
                                    else:
                                        function_response = types.FunctionResponse(
                                            id=fc.id, name=fc.name, response={"result": "Error: No mobile device connected."}
                                        )
                                    function_responses.append(function_response)

                                elif fc.name == "discover_printers":
                                    print(f"[REX DEBUG] [TOOL] Tool Call: 'discover_printers'")
                                    printers = await self.printer_agent.discover_printers()
                                    # Format for model
                                    if printers:
                                        printer_list = []
                                        for p in printers:
                                            printer_list.append(f"{p['name']} ({p['host']}:{p['port']}, type: {p['printer_type']})")
                                        result_str = "Found Printers:\n" + "\n".join(printer_list)
                                    else:
                                        result_str = "No printers found on network. Ensure printers are on and running OctoPrint/Moonraker."
                                    
                                    function_response = types.FunctionResponse(
                                        id=fc.id, name=fc.name, response={"result": result_str}
                                    )
                                    function_responses.append(function_response)

                                elif fc.name == "print_stl":
                                    stl_path = fc.args["stl_path"]
                                    printer = fc.args["printer"]
                                    profile = fc.args.get("profile")
                                    
                                    print(f"[REX DEBUG] [TOOL] Tool Call: 'print_stl' STL='{stl_path}' Printer='{printer}'")
                                    
                                    # Resolve 'current' to project STL
                                    if stl_path.lower() == "current":
                                        stl_path = "output.stl" # Let printer agent resolve it in root_path

                                    # Get current project path
                                    project_path = str(self.project_manager.get_current_project_path())
                                    
                                    result = await self.printer_agent.print_stl(
                                        stl_path, 
                                        printer, 
                                        profile, 
                                        root_path=project_path
                                    )
                                    result_str = result.get("message", "Unknown result")
                                    
                                    function_response = types.FunctionResponse(
                                        id=fc.id, name=fc.name, response={"result": result_str}
                                    )
                                    function_responses.append(function_response)

                                elif fc.name == "get_print_status":
                                    printer = fc.args["printer"]
                                    print(f"[REX DEBUG] [TOOL] Tool Call: 'get_print_status' Printer='{printer}'")
                                    
                                    status = await self.printer_agent.get_print_status(printer)
                                    if status:
                                        result_str = f"Printer: {status.printer}\n"
                                        result_str += f"State: {status.state}\n"
                                        result_str += f"Progress: {status.progress_percent:.1f}%\n"
                                        if status.time_remaining:
                                            result_str += f"Time Remaining: {status.time_remaining}\n"
                                        if status.time_elapsed:
                                            result_str += f"Time Elapsed: {status.time_elapsed}\n"
                                        if status.filename:
                                            result_str += f"File: {status.filename}\n"
                                        if status.temperatures:
                                            temps = status.temperatures
                                            if "hotend" in temps:
                                                result_str += f"Hotend: {temps['hotend']['current']:.0f}°C / {temps['hotend']['target']:.0f}°C\n"
                                            if "bed" in temps:
                                                result_str += f"Bed: {temps['bed']['current']:.0f}°C / {temps['bed']['target']:.0f}°C"
                                    else:
                                        result_str = f"Could not get status for printer '{printer}'. Ensure it is discovered first."
                                    
                                    function_response = types.FunctionResponse(
                                        id=fc.id, name=fc.name, response={"result": result_str}
                                    )
                                    function_responses.append(function_response)

                                elif fc.name == "iterate_cad":
                                    prompt = fc.args["prompt"]
                                    print(f"[REX DEBUG] [TOOL] Tool Call: 'iterate_cad' Prompt='{prompt}'")
                                    
                                    # Emit status
                                    if self.on_cad_status:
                                        self.on_cad_status("generating")
                                    
                                    # Get project cad folder path
                                    cad_output_dir = str(self.project_manager.get_current_project_path() / "cad")
                                    
                                    # Call CadAgent to iterate on the design
                                    cad_data = await self.cad_agent.iterate_prototype(prompt, output_dir=cad_output_dir)
                                    
                                    if cad_data:
                                        print(f"[REX DEBUG] [OK] CadAgent iteration returned data successfully.")
                                        
                                        # Dispatch to frontend
                                        if self.on_cad_data:
                                            print(f"[REX DEBUG] [SEND] Dispatching iterated CAD data to frontend...")
                                            self.on_cad_data(cad_data)
                                            print(f"[REX DEBUG] [SENT] Dispatch complete.")
                                        
                                        # Save to Project
                                        self.project_manager.save_cad_artifact("output.stl", f"Iteration: {prompt}")
                                        
                                        result_str = f"Successfully iterated design: {prompt}. The updated 3D model is now displayed."
                                    else:
                                        print(f"[REX DEBUG] [ERR] CadAgent iteration returned None.")
                                        result_str = f"Failed to iterate design with prompt: {prompt}"
                                    
                                    function_response = types.FunctionResponse(
                                        id=fc.id, name=fc.name, response={"result": result_str}
                                    )
                                    function_responses.append(function_response)
                        if function_responses:
                            await self.session.send_tool_response(function_responses=function_responses)
                
                # Turn/Response Loop Finished
                self.flush_chat()

                while not self.audio_in_queue.empty():
                    self.audio_in_queue.get_nowait()
        except Exception as e:
            print(f"Error in receive_audio: {e}")
            traceback.print_exc()
            # CRITICAL: Re-raise to crash the TaskGroup and trigger outer loop reconnect
            raise e

    async def play_audio(self):
        stream = await asyncio.to_thread(
            pya.open,
            format=FORMAT,
            channels=CHANNELS,
            rate=RECEIVE_SAMPLE_RATE,
            output=True,
            output_device_index=self.output_device_index,
        )
        
        # Track when JARVIS stops speaking (0.5 second timeout)
        self._rex_speech_timer = None
        
        # Track when JARVIS started speaking (for mute buffer)
        self._rex_speech_start_time = None
        
        while True:
            bytestream = await self.audio_in_queue.get()
            
            # Mark that JARVIS is speaking
            if not self._is_rex_speaking:
                self._is_rex_speaking = True
                self._rex_speech_start_time = time.time()
                print(f"[REX DEBUG] [AUDIO] JARVIS started speaking at {self._rex_speech_start_time}")
            
            # Cancel any existing timer
            if self._rex_speech_timer:
                self._rex_speech_timer.cancel()
                self._rex_speech_timer = None
            
            if self.on_audio_data:
                self.on_audio_data(bytestream)
            
            # Send to Mobile for Two-Way Voice
            self.mobile_bridge.send_audio(bytestream)
            
            await asyncio.to_thread(stream.write, bytestream)
            
            # Set a timer to mark JARVIS as done speaking after 0.5 seconds of silence
            async def mark_ada_finished():
                await asyncio.sleep(0.5)
                if self._is_rex_speaking:  # Check if still true
                    self._is_rex_speaking = False
                    self._rex_speech_start_time = None
                    self._rex_speech_timer = None
                    print("[REX DEBUG] [AUDIO] JARVIS finished speaking")
            
            self._rex_speech_timer = asyncio.create_task(mark_ada_finished())

    async def get_frames(self):
        cap = await asyncio.to_thread(cv2.VideoCapture, 0, cv2.CAP_AVFOUNDATION)
        while True:
            if self.paused:
                await asyncio.sleep(0.1)
                continue
            frame = await asyncio.to_thread(self._get_frame, cap)
            if frame is None:
                break
            await asyncio.sleep(1.0)
            if self.out_queue:
                await self.out_queue.put(frame)
        cap.release()

    def _get_frame(self, cap):
        ret, frame = cap.read()
        if not ret:
            return None
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = PIL.Image.fromarray(frame_rgb)
        img.thumbnail([1024, 1024])
        image_io = io.BytesIO()
        img.save(image_io, format="jpeg")
        image_io.seek(0)
        image_bytes = image_io.read()
        return {"mime_type": "image/jpeg", "data": base64.b64encode(image_bytes).decode()}

    async def _get_screen(self):
        pass 
    async def get_screen(self):
         pass

    async def run(self, start_message=None):
        retry_delay = 1
        is_reconnect = False
        
        while not self.stop_event.is_set():
            try:
                print(f"[REX DEBUG] [CONNECT] Connecting to Gemini Live API...")
                async with (
                    client.aio.live.connect(model=MODEL, config=config) as session,
                    asyncio.TaskGroup() as tg,
                ):
                    self.session = session

                    self.audio_in_queue = asyncio.Queue()
                    self.out_queue = asyncio.Queue(maxsize=10)

                    tg.create_task(self.send_realtime())
                    tg.create_task(self.listen_audio())
                    # tg.create_task(self._process_video_queue()) # Removed in favor of VAD

                    if self.video_mode == "camera":
                        tg.create_task(self.get_frames())
                    elif self.video_mode == "screen":
                        tg.create_task(self.get_screen())

                    tg.create_task(self.receive_audio())
                    tg.create_task(self.play_audio())

                    # Handle Startup vs Reconnect Logic
                    if not is_reconnect:
                        if start_message:
                            print(f"[REX DEBUG] [INFO] Sending start message: {start_message}")
                            await self.session.send(input=start_message, end_of_turn=True)
                        
                        # Sync Project State
                        if self.on_project_update and self.project_manager:
                            self.on_project_update(self.project_manager.current_project)
                    
                    else:
                        print(f"[REX DEBUG] [RECONNECT] Connection restored.")
                        # Restore Context
                        print(f"[REX DEBUG] [RECONNECT] Fetching recent chat history to restore context...")
                        history = self.project_manager.get_recent_chat_history(limit=10)
                        
                        context_msg = "System Notification: Connection was lost and just re-established. Here is the recent chat history to help you resume seamlessly:\n\n"
                        for entry in history:
                            sender = entry.get('sender', 'Unknown')
                            text = entry.get('text', '')
                            context_msg += f"[{sender}]: {text}\n"
                        
                        context_msg += "\nPlease acknowledge the reconnection to the user (e.g. 'I lost connection for a moment, but I'm back...') and resume what you were doing."
                        
                        print(f"[REX DEBUG] [RECONNECT] Sending restoration context to model...")
                        await self.session.send(input=context_msg, end_of_turn=True)

                    # Reset retry delay on successful connection
                    retry_delay = 1
                    
                    # Wait until stop event, or until the session task group exits (which happens on error)
                    # Actually, the TaskGroup context manager will exit if any tasks fail/cancel.
                    # We need to keep this block alive.
                    # The original code just waited on stop_event, but that doesn't account for session death.
                    # We should rely on the TaskGroup raising an exception when subtasks fail (like receive_audio).
                    
                    # However, since receive_audio is a task in the group, if it crashes (connection closed), 
                    # the group will cancel others and exit. We catch that exit below.
                    
                    # We can await stop_event, but if the connection dies, receive_audio crashes -> group closes -> we exit `async with` -> restart loop.
                    # To ensure we don't block indefinitely if connection dies silently (unlikely with receive_audio), we just wait.
                    await self.stop_event.wait()

            except asyncio.CancelledError:
                print(f"[REX DEBUG] [STOP] Main loop cancelled.")
                break
                
            except Exception as e:
                # This catches the ExceptionGroup from TaskGroup or direct exceptions
                print(f"[REX DEBUG] [ERR] Connection Error: {e}")
                
                if self.stop_event.is_set():
                    break
                
                print(f"[REX DEBUG] [RETRY] Reconnecting in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, 10) # Exponential backoff capped at 10s
                is_reconnect = True # Next loop will be a reconnect
                
            finally:
                # Cleanup before retry
                if hasattr(self, 'audio_stream') and self.audio_stream:
                    try:
                        self.audio_stream.close()
                    except: 
                        pass

def get_input_devices():
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    devices = []
    for i in range(0, numdevices):
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            devices.append((i, p.get_device_info_by_host_api_device_index(0, i).get('name')))
    p.terminate()
    return devices

def get_output_devices():
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    devices = []
    for i in range(0, numdevices):
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxOutputChannels')) > 0:
            devices.append((i, p.get_device_info_by_host_api_device_index(0, i).get('name')))
    p.terminate()
    return devices

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        type=str,
        default=DEFAULT_MODE,
        help="pixels to stream from",
        choices=["camera", "screen", "none"],
    )
    args = parser.parse_args()
    main = AudioLoop(video_mode=args.mode)
    asyncio.run(main.run())