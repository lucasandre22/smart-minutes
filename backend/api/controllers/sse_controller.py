from fastapi import Request, APIRouter
from api.schemas import *
from api.services.service import Service
from core.config import *
from fastapi.responses import StreamingResponse

STREAM_DELAY = 1
STREAM_RETRY_TIMEOUT = 15000


router = APIRouter(
    prefix="/stream/v1"
)

@router.get('/stream')
async def message_stream(request: Request):
    return StreamingResponse(Service.event_generator(), media_type="text/event-stream")


@router.get('/clear', status_code=204)
async def message_stream(request: Request):
    Service.clear_current_task()
    return None