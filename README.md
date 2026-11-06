# 🌸 Re:Zero Live2D 데스크톱 컴패니언 (reZero_live2d)

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%2F%2011-0078D6?logo=windows)](https://microsoft.com)
[![Live2D](https://img.shields.io/badge/Live2D-Cubism%204-purple)](https://www.live2d.com/)
[![Codex](https://img.shields.io/badge/Codex%20Agent-Compatible-brightgreen)](https://github.com)

Windows 바탕화면 위에 상주하는 투명 **Live2D Re:Zero (리제로) 데스크톱 마스코트**이자, **198종 캐릭터 실시간 교체**, **코덱스(Codex) AI 개발 에이전트 연동**, **마우스 시선 추적**을 지원하는 경량 올인원 데스크톱 컴패니언입니다.

*(외부 TTS 엔진 없이 만화 말풍선, 대사 자막 및 캐릭터별 네이티브 모션으로 가볍고 빠르게 동작합니다.)*

---

## ✨ 주요 기능 (Features)

- 👥 **198종 리제로 캐릭터 실시간 교체 (Character Switcher)**:
  - 렘(Rem), 에밀리아(Emilia), 람(Ram), 베아트리스(Beatrice), 스바루(Subaru), 에키드나(Echidna), 펠트(Felt), 페리스(Ferris), 크루쉬(Crusch), 라인하르트(Reinhard) 등 198종의 다양한 코스튬(기본, 수영복, 웨딩, 드레스, 사복, 오니화 등)을 프로그램 재시작 없이 0.5초 만에 실시간으로 변경할 수 있습니다.
  - 마스코트 우클릭 또는 `🔄` 버튼을 누르면 나타나는 퀵 픽커 및 전용 설정창에서 검색과 필터링 지원.
- 🤖 **코덱스(Codex) AI 개발 에이전트 연동**:
  - `start`, `thinking`, `success`, `error`, `warning` 등의 개발 라이프사이클 이벤트에 맞춰 캐릭터가 알맞은 표정과 모션(생각하기, 환호, 울음 등)을 취하며 말풍선으로 작업 상태를 보고합니다.
- 🪟 **완전 투명 데스크톱 오버레이**:
  - Windows DWM Glass 프레임 투명화를 통해 네모난 창 테두리나 배경 없이 캐릭터 모델만 바탕화면에 자연스럽게 떠 있습니다.
- 👀 **실시간 마우스 시선 & 고개 추적**:
  - 마우스 커서의 전역 위치를 실시간 추적하여 눈동자(`ParamEyeBallX/Y`)와 머리/상체 각도(`ParamAngleX/Y/Z`, `ParamBodyAngleX`)가 자연스럽게 커서를 바라봅니다.
- 💬 **모던 만화 말풍선 (Comic Bubble) & 자막 UI**:
  - 대사 및 알림 수신 시 캐릭터 머리 위에 깔끔한 말풍선 팝업 또는 하단 반투명 자막 바 선택 가능.
- 🎭 **감정 대응 모션 엔진**:
  - 텍스트 키워드 또는 이벤트 태그에 따라 198종 캐릭터 각각에 내장된 모션을 자동으로 찾아 최적의 리액션을 보여줍니다.

---

## 🚀 빠른 시작 (Quick Start)

### 1. 패키지 설치
```powershell
pip install -r requirements.txt
```

### 2. 마스코트 실행
콘솔 창 없이 바탕화면에 즉시 실행하려면:
```powershell
# 배치 파일 실행
start_rezero.bat

# 또는 무소음 VBScript 실행
wscript.exe start_rezero.vbs
```

---

## 🛠️ 코덱스 및 CLI 사용법 (`speak.py`)

AI 에이전트 또는 터미널에서 리제로 컴패니언으로 상태를 전달할 수 있습니다:

```powershell
# 코덱스 작업 시작 알림
python speak.py --event start "작업 분석을 시작합니다!"

# 코덱스 성공 알림 (환호 모션)
python speak.py --event success "빌드 및 테스트가 통과했습니다!"

# 코덱스 오류 알림 (슬픈 모션)
python speak.py --event error "컴파일 에러가 발생했습니다."

# 캐릭터 변경 및 일반 대사
python speak.py --character ac_base_rem01 "스바루 군, 무엇이든 맡겨주세요!"
```

상세한 에이전트 연동 규격은 [CODEX.md](file:///C:/2026591001/source/reZero_live2d/CODEX.md)를 참고하세요.

---

## 📡 REST API 엔드포인트

컴패니언은 로컬 HTTP 서버(`http://127.0.0.1:8990`)를 통해 외부와 통신합니다:

| 엔드포인트 | 메서드 | 설명 |
| :--- | :--- | :--- |
| `/api/event` | `POST` | 코덱스 이벤트(`start`, `thinking`, `success`, `error` 등) 전달 |
| `/api/characters` | `GET` | 사용 가능한 전체 198종 캐릭터 목록 및 메타데이터 반환 |
| `/api/character` | `GET` / `POST` | 현재 선택된 캐릭터 조회 및 실시간 캐릭터 변경 |
| `/api/character_info?id=<id>` | `GET` | 특정 캐릭터의 모델 파일 및 모션 상세 정보 조회 |
| `/api/speak` | `POST` | 대사 말풍선 출력 및 모션 재생 요청 |
| `/api/config` | `GET` / `POST` | 컴패니언 크기, 자막 환경설정 조회 및 갱신 |
| `/api/toggle_settings` | `POST` | 설정 UI 창 토글 |

---

## 📁 프로젝트 구조

```
reZero_live2d/
├── Live2D Characters/       # 198종 리제로 Cubism 3/4 모델 및 모션 에셋
├── static/                  # Pixi.js, Cubism 4 Core 런타임 라이브러리
├── app.py                   # 메인 백엔드 & 투명 Webview2 윈도우 컨트롤러
├── character_manager.py     # 198종 캐릭터 스캔 및 모션 매퍼
├── emotion_engine.py        # 감정 및 코덱스 이벤트 대응 엔진
├── speak.py                 # 코덱스 및 CLI 브릿지 스크립트
├── index.html               # 투명 WebGL 캔버스 및 말풍선 UI
├── settings.html            # 198종 캐릭터 선택 및 환경설정 대시보드
├── config.json              # 사용자 환경설정
├── CODEX.md                 # 코덱스(Codex) AI 연동 상세 가이드
├── start_rezero.bat         # 실행 배치 파일
└── README.md                # 프로젝트 안내 문서
```

---

## 📜 라이선스 및 크레딧
* 본 프로젝트의 Re:Zero 에셋 저작권은 원작자 및 공식 게임 제작사에 있습니다.
* Live2D Cubism SDK for Web 규정을 준수합니다.
