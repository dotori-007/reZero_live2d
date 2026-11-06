# 🤖 Re:Zero Live2D 코덱스(Codex) 및 AI 에이전트 연동 가이드

`reZero_live2d`는 OpenAI Codex, GitHub Copilot, Antigravity CLI 등 다양한 AI 코딩 에이전트와 완벽하게 연동되어, 작업 진행 상황과 상태를 바탕화면의 리제로 Live2D 마스코트를 통해 시각적(말풍선, 감정 모션, 시선 추적)으로 전달합니다.

---

## 1. 코덱스 이벤트 유형 (Events)

| 이벤트 키 | 표정/모션 | 기본 메시지 | 사용 시점 |
| :--- | :--- | :--- | :--- |
| `start` | `thinking` | 코덱스 작업 분석을 시작합니다! | 프롬프트 접수 및 작업 시작 시 |
| `thinking` | `thinking` | 코드를 면밀히 분석하고 있습니다... | 코드베이스 탐색, 계획 수립 중 |
| `success` | `joy_cheer` | 작업이 성공적으로 완료되었습니다! | 빌드 성공, 테스트 통과, 작업 완료 시 |
| `error` | `crying` | 오류가 발생하여 확인이 필요합니다 ㅠㅠ | 컴파일 에러, 테스트 실패, 예외 발생 시 |
| `warning` | `surprise` | 주의할 점이 발견되었습니다! | 린트 경고, 보안 주의점 발견 시 |
| `nod` | `smug_pride` | 네, 확인했습니다! | 사용자 지시 확인 및 긍정 응답 시 |

---

## 2. CLI 연동 방법 (`speak.py`)

코덱스 실행 스크립트나 터미널 훅에서 다음과 같이 한 줄로 호출할 수 있습니다:

```powershell
# 1. 작업 시작 알림
python speak.py --event start "로그인 API 구현을 시작합니다!"

# 2. 코드 분석/생각 중 알림
python speak.py --event thinking "데이터베이스 스키마를 검토하고 있어요..."

# 3. 작업 성공 알림 (환호 모션)
python speak.py --event success "모든 단위 테스트가 무사히 통과했습니다!"

# 4. 오류 발생 알림 (슬픈 모션)
python speak.py --event error "빌드 과정에서 의존성 충돌이 발생했어요."

# 5. 캐릭터 교체하며 알림 (예: 에밀리아로 교체)
python speak.py --character ac_base_emilia01 --event success "스바루, 작업이 완벽하게 끝났어!"
```

---

## 3. REST API 직접 호출 (HTTP JSON)

에이전트 내부에서 HTTP 통신을 사용하는 경우 포트 8990으로 JSON POST 요청을 전송합니다:

```json
POST http://127.0.0.1:8990/api/event
Content-Type: application/json

{
  "event": "success",
  "message": "코덱스 기능 구현 및 검증 완료!",
  "character": "ac_base_rem01"
}
```
