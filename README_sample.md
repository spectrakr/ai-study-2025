# AI 학습 환경 설정 가이드

## 1. Python 설치
### Windows
1. Python 공식 웹사이트(https://www.python.org)에서 Python 3.9+ 버전 다운로드
2. 설치 시 "Add Python to PATH" 옵션 체크
3. 설치 완료 후 명령 프롬프트에서 확인:
```bash
python --version
```

### macOS
1. Homebrew를 통한 설치:
```bash
brew install python@3.9
```
2. 버전 확인:
```bash
python3 --version
```

## 2. Poetry 설치
### Windows
```bash
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

### macOS/Linux
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

## 3. 프로젝트 설정
1. 프로젝트 클론:
```bash
git clone https://github.com/your-username/ai-study-2025.git
cd ai-study-2025
```

2. Poetry 가상 환경 생성 및 의존성 설치:
```bash
poetry install
```

3. 환경 변수 설정:
```bash
cp .env.sample .env
```

4. .env 파일 설정:
```env
# OpenAI API 설정
OPENAI_API_KEY=your-api-key-here

# 기타 필요한 API 키 설정
SERPAPI_API_KEY=your-serpapi-key
GOOGLE_API_KEY=your-google-key

# 벡터 저장소 설정
VECTORSTORE_TYPE=chroma
PERSIST_DIRECTORY=./vector_db
```

## 4. IDE 설정
### VSCode 추천 설정
1. 확장 프로그램 설치:
   - Python
   - Pylance
   - Python Test Explorer
   - Python Debugger
   - Python Environment Manager

2. 작업 영역 설정 (`.vscode/settings.json`):
```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true
}
```

## 5. 필수 라이브러리 및 도구
- langchain
- openai
- chromadb
- tiktoken
- python-dotenv
- pytest (테스트용)
- black (코드 포맷팅)
- pylint (코드 검사)

## 6. 프로젝트 실행 확인
1. 가상 환경 활성화:
```bash
poetry shell
```

2. 예제 실행:
```bash
python langgraph_todo_manager.py
```

## 7. 문제 해결
### 일반적인 문제
1. Poetry 가상 환경 인식 문제
```bash
poetry env info
poetry env list
```

2. 의존성 충돌
```bash
poetry update
poetry install --no-cache
```

3. Python 버전 불일치
```bash
pyenv install 3.9.x
pyenv local 3.9.x
poetry env use python3.9
```

### 도움말
문제가 발생하면 다음 채널을 통해 도움을 받을 수 있습니다:
- GitHub Issues
- 프로젝트 Wiki
- 팀 Slack 채널

## 8. 참고 자료
- [Poetry 공식 문서](https://python-poetry.org/docs/)
- [LangChain 문서](https://python.langchain.com/docs/get_started/introduction)
- [OpenAI API 문서](https://platform.openai.com/docs/introduction) 