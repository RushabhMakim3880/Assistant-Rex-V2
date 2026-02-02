generate_cad_prototype_tool = {
    "name": "generate_cad_prototype",
    "description": "Generates a 3D wireframe prototype based on a user's description. Use this when the user asks to 'visualize', 'prototype', 'create a wireframe', or 'design' something in 3D.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "prompt": {
                "type": "STRING",
                "description": "The user's description of the object to prototype."
            }
        },
        "required": ["prompt"]
    }
}




write_file_tool = {
    "name": "write_file",
    "description": "Writes content to a file at the specified path. Overwrites if exists.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "path": {
                "type": "STRING",
                "description": "The path of the file to write to."
            },
            "content": {
                "type": "STRING",
                "description": "The content to write to the file."
            }
        },
        "required": ["path", "content"]
    }
}

read_directory_tool = {
    "name": "read_directory",
    "description": "Lists the contents of a directory.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "path": {
                "type": "STRING",
                "description": "The path of the directory to list."
            }
        },
        "required": ["path"]
    }
}

read_file_tool = {
    "name": "read_file",
    "description": "Reads the content of a file.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "path": {
                "type": "STRING",
                "description": "The path of the file to read."
            }
        },
        "required": ["path"]
    }
}

create_folder_tool = {
    "name": "create_folder",
    "description": "Creates a new folder at the specified path.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "path": {
                "type": "STRING",
                "description": "The path of the folder to create."
            }
        },
        "required": ["path"]
    }
}

open_file_tool = {
    "name": "open_file",
    "description": "Opens a file with the default associated application.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "path": {
                "type": "STRING",
                "description": "The path of the file to open."
            }
        },
        "required": ["path"]
    }
}

open_folder_tool = {
    "name": "open_folder",
    "description": "Opens a folder in File Explorer.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "path": {
                "type": "STRING",
                "description": "The path of the folder to open."
            }
        },
        "required": ["path"]
    }
}

open_app_tool = {
    "name": "open_app",
    "description": "Opens an application installed on the computer (e.g. 'notepad', 'code', 'chrome').",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "app_name": {
                "type": "STRING",
                "description": "The name of the application or command to run."
            }
        },
        "required": ["app_name"]
    }
}

open_url_tool = {
    "name": "open_url",
    "description": "Opens a specific URL in the default web browser.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "url": {
                "type": "STRING",
                "description": "The URL to open (e.g. 'https://youtube.com')."
            }
        },
        "required": ["url"]
    }
}

type_text_tool = {
    "name": "type_text",
    "description": "Types text using the keyboard.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "text": {
                "type": "STRING",
                "description": "The text to type."
            },
            "interval": {
                "type": "NUMBER",
                "description": "Delay between keystrokes in seconds (default 0.05).",
                "nullable": True
            }
        },
        "required": ["text"]
    }
}

press_key_tool = {
    "name": "press_key",
    "description": "Presses a key or key combination (e.g. 'enter', 'ctrl+c').",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "keys": {
                "type": "STRING",
                "description": "The key or combination to press (e.g. 'enter', 'ctrl+v')."
            }
        },
        "required": ["keys"]
    }
}

mouse_move_tool = {
    "name": "mouse_move",
    "description": "Moves the mouse cursor to specific coordinates.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "x": {
                "type": "INTEGER",
                "description": "X coordinate."
            },
            "y": {
                "type": "INTEGER",
                "description": "Y coordinate."
            }
        },
        "required": ["x", "y"]
    }
}

mouse_click_tool = {
    "name": "mouse_click",
    "description": "Clicks the mouse.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "button": {
                "type": "STRING",
                "description": "Button to click ('left', 'right', 'middle'). Default 'left'.",
                "nullable": True
            },
            "clicks": {
                "type": "INTEGER",
                "description": "Number of clicks (default 1).",
                "nullable": True
            }
        },
        "required": []
    }
}

search_web_tool = {
    "name": "search_web",
    "description": "Searches for a query on a specific platform or search engine. Use this for 'Play X on Y' or 'Search X on Y' requests.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "query": {
                "type": "STRING",
                "description": "The search query (e.g. 'Arijit Singh songs', 'Python tutorial')."
            },
            "platform": {
                "type": "STRING",
                "description": "The platform to search on (e.g. 'google', 'youtube', 'bing', 'reddit', 'wikipedia'). Defaults to 'google'.",
                "nullable": True
            }
        },
        "required": ["query"]
    }
}

window_control_tool = {
    "name": "window_control",
    "description": "Controls the active window (minimize, maximize, snap).",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": "The action to perform: 'minimize', 'maximize', 'restore', 'close', 'snap_left', 'snap_right', 'snap_up', 'snap_down'."
            }
        },
        "required": ["action"]
    }
}

system_control_tool = {
    "name": "system_control",
    "description": "Controls system state (volume, brightness, lock, sleep).",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": "Action: 'volume_up', 'volume_down', 'volume_mute', 'brightness_up', 'brightness_down', 'lock_screen', 'sleep', 'shutdown'."
            }
        },
        "required": ["action"]
    }
}

manage_process_tool = {
    "name": "manage_process",
    "description": "Manages running processes (kill/close applications).",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": "Action to perform, currently only 'kill' is supported."
            },
            "target": {
                "type": "STRING",
                "description": "The name of the process or application to kill (e.g., 'notepad', 'python')."
            }
        },
        "required": ["action", "target"]
    }
}

capture_screen_tool = {
    "name": "capture_screen",
    "description": "Captures a screenshot of the primary screen for visual analysis. Use this when asked to 'look at' something or 'check' the screen.",
    "parameters": {
        "type": "OBJECT",
        "properties": {},
        "required": []
    },
    "behavior": "NON_BLOCKING"
}

manage_call_tool = {
    "name": "manage_call",
    "description": "Manage phone calls (answer, end) on the connected mobile device.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "enum": ["answer", "end", "reject", "dial"],
                "description": "The action to perform on the call. 'dial' requires 'number'."
            },
            "number": {
                "type": "STRING",
                "description": "The phone number to dial (required for 'dial' action, optional for others)."
            },
            "reason": {
                "type": "STRING",
                "description": "Optional reason for rejecting the call (sent as a message)."
            }
        },
        "required": ["action"]
    }
}

mobile_app_tool = {
    "name": "mobile_app_control",
    "description": "Controls apps on the connected mobile device (Phone). Use this to open/launch apps like WhatsApp, Camera, YouTube, etc.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "app_name": {
                "type": "STRING",
                "description": "The name of the app to launch (e.g., 'WhatsApp', 'YouTube', 'Camera', 'Maps')."
            },
            "action": {
                "type": "STRING",
                "enum": ["open", "close", "go_home"],
                "description": "The action to perform (default is 'open'). 'go_home' returns to the homescreen."
            }
        },
        "required": ["app_name"]
    }
}

mobile_contact_tool = {
    "name": "mobile_contact_tool",
    "description": "Search for contacts on the connected mobile device by name. Returns a list of matching names and numbers.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "query": {
                "type": "STRING",
                "description": "The name or partial name to search for."
            }
        },
        "required": ["query"]
    }
}

mobile_message_tool = {
    "name": "mobile_message_tool",
    "description": "Send a message (WhatsApp or SMS) to a contact or number on mobile.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "target": {
                "type": "STRING",
                "description": "The phone number or contact name."
            },
            "message": {
                "type": "STRING",
                "description": "The message text to send."
            },
            "platform": {
                "type": "STRING",
                "enum": ["whatsapp", "sms", "telegram", "signal"],
                "default": "whatsapp",
                "description": "Messaging platform to use."
            }
        },
        "required": ["target", "message"]
    }
}


mobile_get_contacts_tool = {
    "name": "mobile_get_contacts",
    "description": "Fetch the entire contact list from the connected mobile device. Use this for synchronization or when the user asks to 'sync contacts'.",
    "parameters": {
        "type": "OBJECT",
        "properties": {},
        "required": []
    }
}

initiate_evolution_tool = {
    "name": "initiate_evolution",
    "description": "Initiate the REX Evolution process to learn a new capability or tool that is currently missing. Use this when you detect you cannot fulfill a user request due to missing tools.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "capability_gap": {
                "type": "STRING",
                "description": "Description of what you are missing (e.g., 'controlling a Tesla', 'generating stock charts')."
            },
            "user_request": {
                "type": "STRING",
                "description": "The original user request that triggered this gap."
            }
        },
        "required": ["capability_gap", "user_request"]
    }
}

mobile_clipboard_tool = {
    "name": "mobile_clipboard",
    "description": "Sync text to/from the mobile clipboard.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "enum": ["push", "pull"],
                "description": "'push' sends text to mobile, 'pull' gets text from mobile (not yet implemented)."
            },
            "text": {
                "type": "STRING",
                "description": "The text to push to the mobile clipboard."
            }
        },
        "required": ["action"]
    }
}

mobile_hardware_control_tool = {
    "name": "mobile_hardware_control",
    "description": "Control mobile hardware features like flashlight, volume, or Do Not Disturb (DND).",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "feature": {
                "type": "STRING",
                "enum": ["flashlight", "volume", "dnd"],
                "description": "The hardware feature to control."
            },
            "value": {
                "type": "BOOLEAN",
                "description": "True to turn on, False to turn off (for binary features like flashlight and dnd)."
            },
            "level": {
                "type": "INTEGER",
                "description": "Volume level percentage (0-100)."
            }
        },
        "required": ["feature"]
    }
}

mobile_location_tool = {
    "name": "mobile_location",
    "description": "Get the current GPS location coordinates from the connected mobile device.",
    "parameters": {
        "type": "OBJECT",
        "properties": {},
        "required": []
    }
}

mobile_vision_tool = {
    "name": "mobile_vision",
    "description": "Start or stop the remote camera POV stream from the mobile device. Use this when you need to see what the user is seeing.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "enum": ["start", "stop"],
                "description": "'start' opens the camera and begins streaming frames, 'stop' closes it."
            }
        },
        "required": ["action"]
    }
}

mobile_file_beam_tool = {
    "name": "mobile_file_beam",
    "description": "Transfer files between PC and mobile. Use 'send' to beam a file from PC to phone, or 'request' to ask the user to pick a file to beam back.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "enum": ["send", "request"],
                "description": "The transfer action."
            },
            "path": {
                "type": "STRING",
                "description": "The absolute path of the file to send (required for 'send' action)."
            }
        },
        "required": ["action"]
    }
}


mobile_audio_control_tool = {
    "name": "mobile_audio_control",
    "description": "Start or stop audio streaming from the mobile microphone.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "enum": ["start", "stop"],
                "description": "'start' begins streaming mobile audio to REX, 'stop' ends it."
            }
        },
        "required": ["action"]
    }
}


scrape_web_data = {
    "name": "scrape_web_data",
    "description": "Scrapes data from the web based on a search query and saves it to a file (Excel or Word). Use this for requests like 'find companies near me and save to excel' or 'get job listings for python developers'.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "query": {
                "type": "STRING",
                "description": "The search query to find the data (e.g., 'AI companies in San Francisco', 'Python jobs in New York')."
            },
            "output_format": {
                "type": "STRING",
                "description": "The desired output format: 'excel' or 'word'. Default to 'excel' if not specified.",
                "enum": ["excel", "word"]
            }
        },
        "required": ["query"]
    },
    "behavior": "NON_BLOCKING"
}

tools_list = [{"function_declarations": [
    generate_cad_prototype_tool,
    write_file_tool,
    read_directory_tool,
    read_file_tool,
    create_folder_tool,
    open_file_tool,
    open_folder_tool,
    open_app_tool,
    open_url_tool,
    type_text_tool,
    press_key_tool,
    mouse_move_tool,
    mouse_click_tool,
    search_web_tool,
    window_control_tool,
    system_control_tool,
    manage_process_tool,
    capture_screen_tool,
    manage_call_tool,
    mobile_app_tool,
    mobile_contact_tool,
    mobile_message_tool,
    mobile_get_contacts_tool,
    initiate_evolution_tool,
    mobile_clipboard_tool,
    mobile_hardware_control_tool,
    mobile_audio_control_tool,
    mobile_location_tool,
    mobile_vision_tool,
    mobile_file_beam_tool
]}]
