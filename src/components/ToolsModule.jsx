import React from 'react';
import { Mic, MicOff, Settings, Power, Video, VideoOff, Hand, Smartphone } from 'lucide-react';

const ToolsModule = ({
    isConnected,
    isMuted,
    isVideoOn,
    isHandTrackingEnabled,
    showSettings,
    onTogglePower,
    onToggleMute,
    onToggleVideo,
    onToggleSettings,

    onToggleHand,
    onToggleMobile,
    showMobileConnect,

    position,
    onMouseDown
}) => {
    return (
        <div
            id="tools"
            onMouseDown={onMouseDown}
            className={`absolute px-4 py-3 transition-all duration-300 
                        glass-panel rounded-full flex gap-4 items-center`}
            style={{
                left: position.x,
                top: position.y,
                transform: 'translate(-50%, -50%)',
                pointerEvents: 'auto'
            }}
        >
            {/* Power Button */}
            <button
                onClick={onTogglePower}
                className={`p-3 glass-button ${isConnected
                    ? 'text-green-400 bg-green-500/10 shadow-[0_0_15px_rgba(74,222,128,0.2)]'
                    : 'text-gray-500'
                    } `}
                title="System Power"
            >
                <Power size={20} />
            </button>

            <div className="w-px h-8 bg-white/10 mx-1"></div>

            {/* Mute Button */}
            <button
                onClick={onToggleMute}
                disabled={!isConnected}
                className={`p-3 glass-button ${!isConnected
                    ? 'opacity-50 cursor-not-allowed'
                    : isMuted
                        ? 'text-red-400 bg-red-500/10'
                        : 'text-cyan-400 bg-cyan-500/10 shadow-[0_0_15px_rgba(34,211,238,0.2)]'
                    } `}
                title="Microphone"
            >
                {isMuted ? <MicOff size={20} /> : <Mic size={20} />}
            </button>

            {/* Video Button */}
            <button
                onClick={onToggleVideo}
                className={`p-3 glass-button ${isVideoOn
                    ? 'text-purple-400 bg-purple-500/10 shadow-[0_0_15px_rgba(192,132,252,0.2)]'
                    : 'text-gray-400'
                    } `}
                title="Camera Vision"
            >
                {isVideoOn ? <Video size={20} /> : <VideoOff size={20} />}
            </button>

            {/* Hand Tracking Toggle */}
            <button
                onClick={onToggleHand}
                className={`p-3 glass-button ${isHandTrackingEnabled
                    ? 'text-orange-400 bg-orange-500/10 shadow-[0_0_15px_rgba(251,146,60,0.2)]'
                    : 'text-gray-400'
                    } `}
                title="Gesture Control"
            >
                <Hand size={20} />
            </button>

            <div className="w-px h-8 bg-white/10 mx-1"></div>

            {/* Mobile Connect Toggle */}
            <button
                onClick={onToggleMobile}
                className={`p-3 glass-button relative ${showMobileConnect
                    ? 'text-indigo-400 bg-indigo-500/10'
                    : 'text-gray-400'
                    } `}
                title="Mobile Companion"
            >
                {showMobileConnect && <span className="absolute top-0 right-0 w-2 h-2 bg-indigo-400 rounded-full animate-ping" />}
                <Smartphone size={20} />
            </button>

            {/* Settings Button */}
            <button
                onClick={onToggleSettings}
                className={`p-3 glass-button ${showSettings ? 'text-cyan-400 bg-cyan-500/10' : 'text-gray-400'}`}
                title="Settings"
            >
                <Settings size={20} />
            </button>
        </div>
    );
};

export default ToolsModule;
