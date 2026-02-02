import React, { useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const Visualizer = ({ audioData, isListening, intensity = 0, width = 600, height = 400 }) => {
    const canvasRef = useRef(null);

    // Refs for animation loop
    const intensityRef = useRef(intensity);
    const isListeningRef = useRef(isListening);
    const phaseRef = useRef(0); // For breathing animation

    useEffect(() => {
        intensityRef.current = intensity;
        isListeningRef.current = isListening;
    }, [intensity, isListening]);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        // Set higher resolution for sharpness on retina displays
        const dpr = window.devicePixelRatio || 1;
        canvas.width = width * dpr;
        canvas.height = height * dpr;
        const ctx = canvas.getContext('2d');
        ctx.scale(dpr, dpr);

        let animationId;

        const draw = () => {
            const w = width; // Logical width
            const h = height; // Logical height
            const centerX = w / 2;
            const centerY = h / 2;

            phaseRef.current += 0.02; // Breathing speed

            const currentIntensity = intensityRef.current;
            const currentIsListening = isListeningRef.current;

            // Clear canvas
            ctx.clearRect(0, 0, w, h);

            // Base Orb Radius
            // Breathing when idle, expanding when active
            const breath = Math.sin(phaseRef.current) * 5;
            const baseRadius = 80 + (currentIntensity * 60) + (currentIsListening ? 0 : breath);

            // 1. Outer Glow (Soft Halo)
            const gradient1 = ctx.createRadialGradient(centerX, centerY, baseRadius * 0.5, centerX, centerY, baseRadius * 2.5);
            gradient1.addColorStop(0, 'rgba(255, 255, 255, 0.1)');
            gradient1.addColorStop(0.5, 'rgba(255, 255, 255, 0.02)');
            gradient1.addColorStop(1, 'rgba(255, 255, 255, 0)');

            ctx.fillStyle = gradient1;
            ctx.fillRect(0, 0, w, h);

            // 2. Core Orb (The actual white sphere)
            ctx.beginPath();
            ctx.arc(centerX, centerY, baseRadius, 0, Math.PI * 2);

            // Ethereal White Core Gradient
            const gradient2 = ctx.createRadialGradient(centerX, centerY, 0, centerX, centerY, baseRadius);
            gradient2.addColorStop(0, 'rgba(255, 255, 255, 0.95)'); // Bright center
            gradient2.addColorStop(0.4, 'rgba(255, 255, 255, 0.8)');
            gradient2.addColorStop(0.8, 'rgba(200, 220, 255, 0.4)'); // Slight blue tint at edge
            gradient2.addColorStop(1, 'rgba(255, 255, 255, 0.1)'); // Fade out

            ctx.fillStyle = gradient2;
            ctx.fill();

            // 3. Reactive Inner Flare (When Talking)
            if (currentIsListening && currentIntensity > 0.1) {
                const flareRadius = baseRadius * (0.5 + currentIntensity);
                ctx.beginPath();
                ctx.arc(centerX, centerY, flareRadius, 0, Math.PI * 2);
                const flareGrad = ctx.createRadialGradient(centerX, centerY, 0, centerX, centerY, flareRadius);
                flareGrad.addColorStop(0, 'rgba(180, 220, 255, 0.8)');
                flareGrad.addColorStop(1, 'rgba(180, 220, 255, 0)');
                ctx.fillStyle = flareGrad;
                ctx.fill();
            }

            // 4. Subtle Ring (Saturn-like aesthetic detail)
            ctx.beginPath();
            ctx.ellipse(centerX, centerY, baseRadius * 1.8, baseRadius * 0.4, Math.PI / 8, 0, Math.PI * 2);
            ctx.strokeStyle = `rgba(255, 255, 255, ${0.1 + (currentIntensity * 0.2)})`;
            ctx.lineWidth = 1;
            ctx.stroke();

            animationId = requestAnimationFrame(draw);
        };

        draw();
        return () => cancelAnimationFrame(animationId);
    }, [width, height]);

    return (
        <div className="relative flex items-center justify-center p-10" style={{ width, height }}>
            {/* Soft background light behind the canvas */}
            <div className="absolute inset-0 bg-white/5 blur-3xl rounded-full opacity-20 pointer-events-none" />

            <canvas
                ref={canvasRef}
                style={{ width: '100%', height: '100%' }}
                className="z-10"
            />

            {/* Minimalist Label */}
            <div className="absolute bottom-10 text-white/30 font-light tracking-[0.5em] text-xs pointer-events-none uppercase">
                R.E.X System Active
            </div>
        </div>
    );
};

export default Visualizer;
