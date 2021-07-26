from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from prometheus_client import generate_latest, REGISTRY
from starlette.responses import JSONResponse

router = APIRouter()


@router.get('/metrics', response_class=PlainTextResponse)
async def get_test_info() -> str:
    return generate_latest(REGISTRY)


@router.get('/health_check')
async def check_live_status() -> JSONResponse:
    return JSONResponse(content={'success': True})
