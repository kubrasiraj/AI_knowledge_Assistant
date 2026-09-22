
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.log import logger
from app.routers import auth, chat, documents


app = FastAPI(
    title="AI Knowledge Assistant",
    description="A production-style RAG-based knowledge assistant",
    version="1.0.0",
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    logger.warning(
        "Validation error | path=%s | errors=%s",
        request.url.path,
        exc.errors(),
    )

    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "message": "Invalid request data",
            "details": exc.errors(),
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request,
    exc: HTTPException,
):
    logger.warning(
        "HTTP exception | method=%s | path=%s | status_code=%s | detail=%s",
        request.method,
        request.url.path,
        exc.status_code,
        exc.detail,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "Request Error",
            "message": exc.detail,
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception,
):
    logger.exception(
        "Unhandled exception | method=%s | path=%s",
        request.method,
        request.url.path,
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
        },
    )


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "AI Knowledge Assistant",
    }


app.include_router(auth.router)

app.include_router(documents.router)

app.include_router(chat.router)

