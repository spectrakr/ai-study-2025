from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator
import asyncio
import json
import random
from datetime import datetime

app = FastAPI()


async def get_weather_info() -> dict:
    """서울 날씨 정보를 가져오는 함수"""
    # OpenWeatherMap API를 사용하여 실제 날씨 정보를 가져올 수 있습니다
    # 여기서는 예시 데이터를 반환합니다
    weather_conditions = [
        {
            "temp": random.uniform(15, 25),
            "condition": "맑음",
            "humidity": random.randint(30, 70),
        },
        {
            "temp": random.uniform(10, 20),
            "condition": "흐림",
            "humidity": random.randint(40, 80),
        },
        {
            "temp": random.uniform(12, 22),
            "condition": "비",
            "humidity": random.randint(60, 90),
        },
    ]
    return random.choice(weather_conditions)


async def generate_weather_events() -> AsyncGenerator[str, None]:
    """날씨 이벤트를 생성하는 제너레이터"""
    while True:
        weather = await get_weather_info()
        event = {
            "type": "날씨",
            "location": "서울",
            "temperature": f"{weather['temp']:.1f}°C",
            "condition": weather["condition"],
            "humidity": f"{weather['humidity']}%",
            "timestamp": datetime.now().isoformat(),
        }
        yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
        await asyncio.sleep(5)  # 5초마다 날씨 정보 업데이트


@app.get("/weather")
async def weather_events(request: Request) -> StreamingResponse:
    """날씨 SSE 엔드포인트"""
    return StreamingResponse(
        generate_weather_events(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        },
    )


@app.get("/health")
async def health_check():
    """헬스체크 엔드포인트"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
