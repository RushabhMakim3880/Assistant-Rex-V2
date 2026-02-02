import React, { useState, useEffect } from 'react';
import { X } from 'lucide-react';

const TOOLS = [
    { id: 'run_web_agent', label: 'Web Agent' },
    { id: 'create_directory', label: 'Create Folder' },
    { id: 'write_file', label: 'Write File' },
    { id: 'read_directory', label: 'Read Directory' },
    { id: 'read_file', label: 'Read File' },
    { id: 'create_project', label: 'Create Project' },
    { id: 'switch_project', label: 'Switch Project' },
    { id: 'list_projects', label: 'List Projects' },
];

const SettingsWindow = ({
    socket,
    micDevices,
    speakerDevices,
    webcamDevices,
    selectedMicId,
    setSelectedMicId,
    selectedSpeakerId,
    setSelectedSpeakerId,
    selectedWebcamId,
    setSelectedWebcamId,
    cursorSensitivity,
    setCursorSensitivity,
    isCameraFlipped,
    setIsCameraFlipped,
    handleFileUpload,
    onClose
}) => {
    const [permissions, setPermissions] = useState({});
    const [faceAuthEnabled, setFaceAuthEnabled] = useState(false);
    const [masterControlEnabled, setMasterControlEnabled] = useState(false);

    useEffect(() => {
        socket.emit('get_settings');
        const handleSettings = (settings) => {
            if (settings) {
                if (settings.tool_permissions) setPermissions(settings.tool_permissions);
                if (typeof settings.face_auth_enabled !== 'undefined') {
                    setFaceAuthEnabled(settings.face_auth_enabled);
                    localStorage.setItem('face_auth_enabled', settings.face_auth_enabled);
                }
                if (typeof settings.master_control !== 'undefined') {
                    setMasterControlEnabled(settings.master_control);
                }
            }
        };
        socket.on('settings', handleSettings);
        return () => socket.off('settings', handleSettings);
    }, [socket]);

    const togglePermission = (toolId) => {
        const nextVal = !(permissions[toolId] !== false);
        socket.emit('update_settings', { tool_permissions: { [toolId]: nextVal } });
    };

    const toggleFaceAuth = () => {
        const newVal = !faceAuthEnabled;
        setFaceAuthEnabled(newVal);
        localStorage.setItem('face_auth_enabled', newVal);
        socket.emit('update_settings', { face_auth_enabled: newVal });
    };

    const toggleMasterControl = () => {
        const newVal = !masterControlEnabled;
        setMasterControlEnabled(newVal);
        socket.emit('update_settings', { master_control: newVal });
    };

    const toggleCameraFlip = () => {
        const newVal = !isCameraFlipped;
        setIsCameraFlipped(newVal);
        socket.emit('update_settings', { camera_flipped: newVal });
    };

    return (
        <div className="absolute top-20 right-10 glass-panel p-6 rounded-3xl z-50 w-80 animate-fade-in">
            <div className="flex justify-between items-center mb-6 pl-1">
                <h2 className="text-white/90 font-light text-sm uppercase tracking-[0.2em]">Settings</h2>
                <button onClick={onClose} className="text-white/40 hover:text-white transition-colors">
                    <X size={18} />
                </button>
            </div>

            {/* Authentication */}
            <div className="mb-6 space-y-3">
                <h3 className="text-cyan-400/80 font-bold text-[10px] uppercase tracking-wider pl-1">Security</h3>
                <div className="flex items-center justify-between text-xs bg-white/5 p-3 rounded-xl border border-white/5 hover:bg-white/10 transition-colors">
                    <span className="text-white/80">Face Authenticator</span>
                    <button onClick={toggleFaceAuth} className={`relative w-9 h-5 rounded-full transition-all duration-300 ${faceAuthEnabled ? 'bg-cyan-500 shadow-[0_0_10px_rgba(6,182,212,0.5)]' : 'bg-white/10'}`}>
                        <div className={`absolute top-1 left-1 w-3 h-3 bg-white rounded-full transition-transform duration-300 ${faceAuthEnabled ? 'translate-x-4' : 'translate-x-0'}`} />
                    </button>
                </div>
            </div>

            {/* Devices */}
            <div className="mb-6 space-y-3">
                <h3 className="text-cyan-400/80 font-bold text-[10px] uppercase tracking-wider pl-1">Devices</h3>
                {[{ label: 'Mic', val: selectedMicId, set: setSelectedMicId, opts: micDevices },
                { label: 'Speaker', val: selectedSpeakerId, set: setSelectedSpeakerId, opts: speakerDevices },
                { label: 'Camera', val: selectedWebcamId, set: setSelectedWebcamId, opts: webcamDevices }].map((dev, i) => (
                    <div key={i} className="space-y-1">
                        <label className="text-[10px] text-white/40 pl-1 uppercase">{dev.label}</label>
                        <select
                            value={dev.val}
                            onChange={(e) => dev.set(e.target.value)}
                            className="w-full bg-white/5 border border-white/10 rounded-xl p-2 text-xs text-white/90 outline-none focus:border-cyan-500/50 transition-colors appearance-none cursor-pointer hover:bg-white/10"
                        >
                            {dev.opts.map((d, idx) => (
                                <option key={d.deviceId} value={d.deviceId} className="bg-gray-900 text-gray-300">
                                    {d.label || `${dev.label} ${idx + 1}`}
                                </option>
                            ))}
                        </select>
                    </div>
                ))}
            </div>

            {/* Controls */}
            <div className="mb-6 space-y-3">
                <h3 className="text-cyan-400/80 font-bold text-[10px] uppercase tracking-wider pl-1">Controls</h3>

                {/* Sensitivity */}
                <div className="bg-white/5 p-3 rounded-xl border border-white/5">
                    <div className="flex justify-between mb-2">
                        <span className="text-xs text-white/80">Cursor Speed</span>
                        <span className="text-xs text-cyan-400">{cursorSensitivity}x</span>
                    </div>
                    <input
                        type="range" min="1.0" max="5.0" step="0.1"
                        value={cursorSensitivity}
                        onChange={(e) => setCursorSensitivity(parseFloat(e.target.value))}
                        className="w-full accent-cyan-400 h-1 bg-white/20 rounded-lg appearance-none cursor-pointer"
                    />
                </div>

                {/* Camera Flip */}
                <div className="flex items-center justify-between text-xs bg-white/5 p-3 rounded-xl border border-white/5">
                    <span className="text-white/80">Mirror Camera</span>
                    <button onClick={toggleCameraFlip} className={`relative w-9 h-5 rounded-full transition-all duration-300 ${isCameraFlipped ? 'bg-cyan-500 shadow-[0_0_10px_rgba(6,182,212,0.5)]' : 'bg-white/10'}`}>
                        <div className={`absolute top-1 left-1 w-3 h-3 bg-white rounded-full transition-transform duration-300 ${isCameraFlipped ? 'translate-x-4' : 'translate-x-0'}`} />
                    </button>
                </div>
            </div>

            {/* Permissions */}
            <div className="mb-6 space-y-3">
                <div className="flex justify-between items-center pl-1">
                    <h3 className="text-cyan-400/80 font-bold text-[10px] uppercase tracking-wider">Confirmations</h3>
                    <div className="flex items-center gap-2">
                        <span className="text-[9px] text-red-400 font-bold tracking-widest">MASTER</span>
                        <button onClick={toggleMasterControl} className={`relative w-7 h-4 rounded-full transition-colors duration-200 ${masterControlEnabled ? 'bg-red-500 shadow-lg shadow-red-500/30' : 'bg-white/10'}`}>
                            <div className={`absolute top-0.5 left-0.5 w-3 h-3 bg-white rounded-full transition-transform duration-200 ${masterControlEnabled ? 'translate-x-3' : 'translate-x-0'}`} />
                        </button>
                    </div>
                </div>

                <div className={`space-y-1 max-h-32 overflow-y-auto pr-1 custom-scrollbar ${masterControlEnabled ? 'opacity-30 pointer-events-none grayscale' : ''}`}>
                    {TOOLS.map(tool => {
                        const isRequired = permissions[tool.id] !== false;
                        return (
                            <div key={tool.id} className="flex items-center justify-between text-[11px] bg-white/5 px-3 py-2 rounded-lg border border-transparent hover:border-white/10 transition-colors">
                                <span className="text-white/70">{tool.label}</span>
                                <button onClick={() => togglePermission(tool.id)} className={`relative w-7 h-4 rounded-full transition-colors duration-200 ${isRequired ? 'bg-cyan-500/60' : 'bg-white/10'}`}>
                                    <div className={`absolute top-0.5 left-0.5 w-3 h-3 bg-white rounded-full transition-transform duration-200 ${isRequired ? 'translate-x-3' : 'translate-x-0'}`} />
                                </button>
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* Memory Upload */}
            <div>
                <h3 className="text-cyan-400/80 font-bold mb-2 text-[10px] uppercase tracking-wider pl-1">Inject Memory</h3>
                <label className="block bg-white/5 hover:bg-white/10 border border-white/10 border-dashed rounded-xl p-3 text-center cursor-pointer transition-all">
                    <span className="text-xs text-white/50">Drop .txt file or click</span>
                    <input type="file" accept=".txt" onChange={handleFileUpload} className="hidden" />
                </label>
            </div>
        </div>
    );
};

export default SettingsWindow;
