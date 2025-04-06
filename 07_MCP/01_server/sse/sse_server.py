from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator
import asyncio
import json
import random
from datetime import datetime

app = FastAPI()

async def generate_random_events() -> AsyncGenerator[str, None]:
    """무작위 이벤트를 생성하는 제너레이터"""
    events = ["알림", "경고", "정보", "에러"]
    while True:
        event = {
            "type": random.choice(events),
            "message": f"테스트 메시지 #{random.randint(1, 100)}",
            "timestamp": datetime.now().isoformat()
        }
        yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
        await asyncio.sleep(2)  # 2초마다 이벤트 전송

@app.get("/events")
async def events(request: Request) -> StreamingResponse:
    """SSE 엔드포인트"""
    return StreamingResponse(
        generate_random_events(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*"
        }
    )

@app.get("/health")
async def health_check():
    """헬스체크 엔드포인트"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)