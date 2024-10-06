from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi import FastAPI, Response
from .controllers import controller

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(controller.router)

AUTH=""

def verify_authorization_header(req):
    auth_header = req.headers["Authorization"] if "Authorization" in req.headers else ""
    if auth_header != AUTH:
        return Response(status_code=401)
    return None

@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    error_response = verify_authorization_header(request)
    if error_response:
        return error_response

    response = await call_next(request)
    return response

@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI Application!"}

def custom_openapi_message():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="API",
        version="1.0",
        summary="API documentation",
        description="All the routes are specified below, with their respective **OpenAPI** schemas",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi_message