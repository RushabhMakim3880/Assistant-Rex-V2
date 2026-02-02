import React, { useEffect, useRef } from 'react';
import { Globe, X } from 'lucide-react';

const BrowserWindow = ({ imageSrc, logs, onClose, socket }) => {
    const [input, setInput] = React.useState('');
    const logsEndRef = useRef(null);

    // Auto-scroll logs to bottom
    useEffect(() => {
        if (logsEndRef.current) {
            logsEndRef.current.scrollIntoView({ behavior: 'smooth' });
        }
    }, [logs]);

    const handleSend = () => {
        if (!input.trim()) return;
        if (socket) {
            socket.emit('prompt_web_agent', { prompt: input });
        }
        setInput('');
    };

    return (
        <div className="w-full h-full relative group glass-panel flex flex-col overflow-hidden rounded-2xl">
            {/* Header Bar - Drag Handle */}
            <div data-drag-handle className="h-10 border-b border-white/5 flex items-center justify-between px-3 shrink-0 cursor-grab active:cursor-grabbing bg-white/5 backdrop-blur-md">
                <div className="flex items-center gap-2 text-cyan-200/80 text-xs font-light tracking-widest">
                    <Globe size={14} className="text-cyan-400" />
                    <span>WEB_AGENT</span>
                </div>
                <button onClick={onClose} className="hover:bg-red-500/20 text-white/40 hover:text-red-400 p-1.5 rounded-full transition-colors">
                    <X size={14} />
                </button>
            </div>

            {/* Browser Content */}
            <div className="flex-1 relative bg-black/40 flex items-center justify-center overflow-hidden">
                {imageSrc ? (
                    <img
                        src={`data:image/jpeg;base64,${imageSrc}`}
                        alt="Browser View"
                        className="max-w-full max-h-full object-contain shadow-2xl"
                    />
                ) : (
                    <div className="flex flex-col items-center gap-2">
                        <div className="text-cyan-500/50 text-xs font-light tracking-widest animate-pulse">Waiting for stream...</div>
                    </div>
                )}
            </div>

            {/* Input Bar */}
            <div className="h-12 bg-white/5 border-t border-white/5 flex items-center px-4 gap-3 backdrop-blur-sm">
                <span className="text-cyan-400 font-mono text-xs">{'>'}</span>
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                    placeholder="Navigate or search..."
                    className="flex-1 bg-transparent border-none outline-none text-white/90 text-sm font-light placeholder-white/20"
                />
            </div>

            {/* Logs Overlay (Bottom) */}
            <div className="h-24 bg-black/60 backdrop-blur-md border-t border-white/5 p-3 font-mono text-[10px] overflow-y-auto text-cyan-300/80">
                {logs.map((log, i) => (
                    <div key={i} className="mb-1 border-l-2 border-cyan-500/30 pl-2 break-words opacity-80 hover:opacity-100 transition-opacity">
                        <span className="opacity-40 mr-2 text-white">[{new Date().toLocaleTimeString().split(' ')[0]}]</span>
                        {log}
                    </div>
                ))}
                <div ref={logsEndRef} />
            </div>
        </div>
    );
};

export default BrowserWindow;
