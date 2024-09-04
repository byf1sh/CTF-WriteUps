from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import FileResponse, JSONResponse
from starlette.exceptions import HTTPException
import os

async def download(request):
    file_path = request.query_params.get("file")
    if not file_path:
        return JSONResponse({"error": "file parameter is missing"}, status_code=400)

    if not os.path.exists(file_path):
        return JSONResponse({"error": "file not found"}, status_code=404)

    return FileResponse(file_path)

app = Starlette(routes=[Route("/", endpoint=download)])
