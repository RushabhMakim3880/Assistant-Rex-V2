import React, { useState, useEffect } from 'react';
import QRCode from "react-qr-code";
import { X, Smartphone, RefreshCw } from 'lucide-react';

const MobileConnect = ({ onClose }) => {
    const [networkInfo, setNetworkInfo] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchNetworkInfo = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await fetch('http://localhost:8000/network-info');
            if (!response.ok) throw new Error("Failed to fetch network info");
            const data = await response.json();
            setNetworkInfo(data);
        } catch (err) {
            console.error("Error fetching network info:", err);
            setError("Could not get IP address. Make sure backend is running.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchNetworkInfo();
    }, []);

    return (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 animate-in fade-in zoom-in duration-200">
            <div className="bg-[#1a1a1a] border border-[#333] rounded-2xl p-6 w-[350px] shadow-2xl relative">
                <button
                    onClick={onClose}
                    className="absolute top-4 right-4 text-gray-400 hover:text-white transition-colors"
                >
                    <X size={20} />
                </button>

                <div className="flex flex-col items-center gap-6">
                    <div className="flex flex-col items-center gap-2">
                        <div className="w-12 h-12 rounded-full bg-blue-500/10 flex items-center justify-center text-blue-400 mb-2">
                            <Smartphone size={24} />
                        </div>
                        <h2 className="text-xl font-semibold text-white">Connect REX Companion</h2>
                        <p className="text-sm text-gray-400 text-center">
                            Scan this QR code with the REX Companion App to connect instantly.
                        </p>
                    </div>

                    <div className="bg-white p-4 rounded-xl">
                        {loading ? (
                            <div className="w-48 h-48 flex items-center justify-center">
                                <RefreshCw className="animate-spin text-gray-400" />
                            </div>
                        ) : error ? (
                            <div className="w-48 h-48 flex flex-col items-center justify-center text-center gap-2">
                                <span className="text-red-400 text-xs">{error}</span>
                                <button onClick={fetchNetworkInfo} className="text-blue-400 text-xs hover:underline">Retry</button>
                            </div>
                        ) : (
                            <div className="flex flex-col items-center gap-2">
                                <QRCode
                                    value={networkInfo.url}
                                    size={180}
                                    style={{ height: "auto", maxWidth: "100%", width: "100%" }}
                                    viewBox={`0 0 256 256`}
                                />
                            </div>
                        )}
                    </div>

                    {networkInfo && (
                        <div className="flex flex-col items-center gap-1">
                            <span className="text-xs text-gray-500 uppercase tracking-wider">Manual Connection</span>
                            <code className="bg-black/30 px-3 py-1.5 rounded text-blue-400 font-mono text-sm border border-white/5">
                                {networkInfo.ip}:{networkInfo.port}
                            </code>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default MobileConnect;
