import json

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from langchain_core.prompts import PromptTemplate

load_dotenv()

techTalk_conversation = """작성자: 민정
:spiral_calendar_pad:  2:03 PM
:loudspeaker: 2025년 세 번째 테크톡에 여러분을 초대합니다! :tada:
:tulip: 봄바람 살랑이는 3월, 새로운 시작을 테크톡과 함께해보아요!
       이번에는 A팀 & D팀 @정호 님의 AI 에 관련된 흥미로운 발표가 준비되어 있습니다!!!
:microphone: 발표 주제  "AI 패러다임 변화와 우리의 미래" : 이정호
:date: 일정: 2025년 3월 7일 (금) 오후 2시 30분 ~ 4시 00분
:round_pushpin: 장소: 오프라인 - 세미나실 / 온라인 - ZOOM  (사내에 계시다면 세미나실로 참석 부탁드립니다! :two_hearts:)
:cherry_blossom: 참석 포인트!
      :white_check_mark: Tech-Talk 책갈피에서 지난 발표 자료와 영상도 확인 가능! (Slack #all-notices 채널)
      :white_check_mark: 전 직원 대상 행사 :confetti_ball: 참석만 해도 새로운 인사이트 + 동료와 교류 기회 :gift:
:love_letter: 2025년 세 번째 테크톡, 놓치면 아쉽겠죠? 부담 없이 참여하고 유익한 인사이트 가져가세요! 다 함께 만드는 멋진 시작, 기대하겠습니다! :muscle::sparkles:
"""


class TechTalkSummary(BaseModel):
    발표자: str = Field(description="발표 하는 사람")
    주제: str = Field(description="발표 주제")
    일정: str = Field(description="발표 일정")
    장소: str = Field(description="발표 장소")


prompt = PromptTemplate.from_template(
    """
You are a helpful assistant. Please answer the following questions in KOREAN.

QUESTION:
{question}

TechTalk CONVERSATION:
{techTalk_conversation}
"""
)

llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini")
llm_with_structured = llm.with_structured_output(TechTalkSummary)

chain = prompt | llm_with_structured

answer = chain.stream(
    {
        "techTalk_conversation": techTalk_conversation,
        "question": "테크톡 발표 내용을 추출해 주세요.",
    }
)

last_token = None

for token in answer:
    last_token = token

if last_token:
    print("\n")
    print(
        json.dumps(
            json.loads(last_token.model_dump_json()), indent=4, ensure_ascii=False
        ),
        flush=True,
    )
