import React, { useEffect, useRef } from 'react';
import { Send } from 'lucide-react';

const ChatModule = ({
    messages,
    inputValue,
    setInputValue,
    handleSend,
    isModularMode,
    activeDragElement,
    position,
    width = 600,
    height,
    onMouseDown
}) => {
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    return (
        <div
            id="chat"
            onMouseDown={onMouseDown}
            className={`absolute pointer-events-auto transition-all duration-300
            ${isModularMode ? (activeDragElement === 'chat' ? 'ring-1 ring-white/20' : 'ring-1 ring-transparent') : ''}
        `}
            style={{
                left: position.x,
                top: position.y,
                transform: 'translate(-50%, 0)', // Aligned top-center
                width: width,
                height: height
            }}
        >
            {/* Messages Area - No Container Background (Truly Floating) */}
            <div
                className="flex flex-col gap-4 overflow-y-auto mb-4 scrollbar-hide mask-image-gradient relative z-10 px-4"
                style={{ height: height ? `calc(${height}px - 70px)` : '15rem' }}
            >
                {messages.slice(-5).map((msg, i) => (
                    <div key={i} className={`flex flex-col ${msg.sender === 'User' ? 'items-end' : 'items-start'}`}>
                        <div className={`
                            max-w-[90%] px-5 py-3 rounded-2xl backdrop-blur-md text-sm leading-relaxed shadow-lg
                            ${msg.sender === 'User'
                                ? 'bg-white/10 text-white rounded-br-none border border-white/10'
                                : 'bg-black/40 text-gray-200 rounded-bl-none border border-white/5'}
                        `}>
                            {msg.text}
                        </div>
                        <span className="text-[10px] text-white/20 mt-1 px-2 font-light tracking-wider uppercase">
                            {msg.sender} • {msg.time}
                        </span>
                    </div>
                ))}
                <div ref={messagesEndRef} />
            </div>

            {/* Input Area - Floating Capsule */}
            <div className="absolute bottom-0 left-0 right-0 px-4">
                <div className="glass-panel rounded-full flex items-center p-1 pl-5">
                    <input
                        type="text"
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        onKeyDown={handleSend}
                        placeholder="Ask R.E.X..."
                        className="flex-1 bg-transparent border-none text-white focus:ring-0 placeholder-white/20 text-sm font-light focus:outline-none"
                    />
                    <button
                        onClick={() => handleSend({ key: 'Enter' })}
                        className="p-2 glass-button text-white/50 hover:text-cyan-400"
                    >
                        <Send size={16} />
                    </button>
                </div>
            </div>

            {isModularMode && <div className="absolute -top-6 left-0 text-[10px] tracking-widest text-white/20 uppercase">Chat Module</div>}
        </div>
    );
};

export default ChatModule;
