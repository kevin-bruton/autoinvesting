import json
import time
import asyncio
from sse_starlette.sse import EventSourceResponse
from fastapi import APIRouter, Request, Response
from queue import Queue

EVENT_SEND_FREQ = 0.1    # seconds
RETRY_TIMEOUT = 15000  # miliseconds

sse_queue = Queue()

route = APIRouter()

def send_sse (topic: str, message: str):
    sse_queue.put([topic, message])

async def _send_event(request: Request):
    print('SSE client connected!!!')
    while True:
        if await request.is_disconnected():
            print("SSE client disconnected!!!")
            break
        # If there are messages in the queue, send them
        while not sse_queue.empty():
            #print("Checking for messages in the queue")
            topic, message = sse_queue.get()
            yield {
                "event": "message",
                "id": topic,
                "retry": RETRY_TIMEOUT,
                "data": message
            }
        await asyncio.sleep(EVENT_SEND_FREQ)

@route.get('/sse')
async def message_stream(request: Request):
    return EventSourceResponse(_send_event(request))

""" 
STREAM_DELAY = 3  # second
RETRY_TIMEOUT = 15000  # milisecond

@route.get('/sse')
async def message_stream(request: Request):
    print('SSE client connected!!!')
    def new_messages():
        # Add logic here to check for new messages
        yield 'Hello World'
    async def event_generator():
        counter = 0
        while True:
            # If client closes connection, stop sending events
            if await request.is_disconnected():
                break

            # Checks for new messages and return them to client if any
            if new_messages():
                counter += 1
                yield {
                        "event": "message",
                        "id": "message_id",
                        "retry": RETRY_TIMEOUT,
                        "data": '{"counter": ' + str(counter)  + '}'
                }

            await asyncio.sleep(STREAM_DELAY)

    return EventSourceResponse(event_generator())
 """
