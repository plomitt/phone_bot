import asyncio
import threading


stop_event = threading.Event()
msg_queue = asyncio.Queue()