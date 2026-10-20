from fastapi import FastAPI
from typing import Optional

app = FastAPI()

@app.get('/health')
async def health():
    return {'status': 'ok'}