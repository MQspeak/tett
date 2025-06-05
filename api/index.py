from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import io
from PIL import Image
from pydantic import BaseModel

app = FastAPI()

# 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ImageRequest(BaseModel):
    image_url: str
    record_id: str = None

@app.post("/upload-image")
async def upload_image(request: ImageRequest):
    try:
        # 这里放入你原来的 main 函数逻辑
        # 示例简化版：
        response = requests.get(request.image_url)
        if response.status_code == 200:
            return {"success": True, "message": "Image processed"}
        else:
            raise HTTPException(status_code=400, detail="Image download failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))