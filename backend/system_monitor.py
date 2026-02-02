import asyncio
import psutil
import socketio

class SystemMonitor:
    def __init__(self, sio):
        self.sio = sio
        self.running = False

    async def start(self):
        self.running = True
        print("[SystemMonitor] Started monitoring...")
        while self.running:
            stats = self.get_stats()
            # print(f"[SystemMonitor] Broadcasting: {stats}")
            await self.sio.emit('system_stats', stats)
            await asyncio.sleep(2) # Update every 2 seconds

    def stop(self):
        self.running = False

    def get_stats(self):
        return {
            "cpu": psutil.cpu_percent(interval=None),
            "ram": psutil.virtual_memory().percent,
            "disk": psutil.disk_usage('/').percent,
            # GPU is harder without nvidia-smi, skipping for now or adding stub
        }
