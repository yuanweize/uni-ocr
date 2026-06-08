import asyncio
import json
import logging
import tempfile
import threading
import re
from pathlib import Path
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse

from . import UniOCR
from .routers_auth import verify_public_or_authenticated
from .cache import ocr_cache

router = APIRouter(prefix="/extract", tags=["Stream"])

class ThreadQueueHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.queues = {}
        
    def register_thread(self, thread_id: int, queue: asyncio.Queue, loop: asyncio.AbstractEventLoop):
        self.queues[thread_id] = (queue, loop)
        
    def unregister_thread(self, thread_id: int):
        self.queues.pop(thread_id, None)

    def emit(self, record):
        thread_id = threading.get_ident()
        if thread_id in self.queues:
            msg = self.format(record)
            msg = re.sub(r'(/Users/[^/]+/[^\s\'"]+)', '[HIDDEN_PATH]', msg)
            msg = re.sub(r'(/home/[^/]+/[^\s\'"]+)', '[HIDDEN_PATH]', msg)
            msg = re.sub(r'(C:\\Users\\[^\\]+\\[^\s\'"]+)', '[HIDDEN_PATH]', msg)
            queue, loop = self.queues[thread_id]
            loop.call_soon_threadsafe(queue.put_nowait, msg)

# Global custom handler attached to root logger
stream_handler = ThreadQueueHandler()
stream_handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
logging.getLogger().addHandler(stream_handler)
logging.getLogger('paddlex').addHandler(stream_handler)
logging.getLogger('ppocr').addHandler(stream_handler)

@router.post("/stream", dependencies=[Depends(verify_public_or_authenticated)])
async def extract_stream(
    file: UploadFile = File(...),
    engine: str = Form("auto"),
    format: str = Form("json")
):
    queue = asyncio.Queue()
    loop = asyncio.get_running_loop()
    
    def process_ocr(content: bytes):
        thread_id = threading.get_ident()
        stream_handler.register_thread(thread_id, queue, loop)
        try:
            loop.call_soon_threadsafe(queue.put_nowait, f"INFO - Initializing engine: {engine}")
            
            # Using cache to avoid redundant extraction
            doc = ocr_cache.get_or_extract(engine, content)
            
            result_data = None
            if format == "json":
                result_data = doc.to_dict()
            elif format == "markdown":
                result_data = {"markdown": doc.markdown}
            else:
                result_data = {"text": doc.text}
                
            loop.call_soon_threadsafe(
                queue.put_nowait, 
                {"type": "result", "data": result_data}
            )
        except Exception as e:
            loop.call_soon_threadsafe(
                queue.put_nowait, 
                {"type": "error", "message": str(e)}
            )
        finally:
            stream_handler.unregister_thread(thread_id)
            loop.call_soon_threadsafe(queue.put_nowait, None) # EOF marker

    async def event_generator(content: bytes):
        try:
            asyncio.create_task(asyncio.to_thread(process_ocr, content))
            
            while True:
                msg = await queue.get()
                if msg is None:
                    break
                    
                if isinstance(msg, str):
                    yield f"data: {json.dumps({'type': 'log', 'message': msg})}\n\n"
                elif isinstance(msg, dict):
                    yield f"data: {json.dumps(msg)}\n\n"
                    
        finally:
            pass
            
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file uploaded.")
        
    return StreamingResponse(event_generator(content), media_type="text/event-stream")
