# -*- coding: utf-8 -*-
"""
Re:Zero Live2D Codex & CLI Bridge
코덱스(Codex) 및 AI 에이전트 CLI에서 리제로 마스코트의 말풍선, 캐릭터 변경 및 모션 이벤트를 제어합니다.
사용법:
  # 일반 대사
  python speak.py "작업을 준비하고 있어요!"
  # 코덱스 이벤트 트리거
  python speak.py --event start "코덱스 코드 분석을 시작합니다!"
  python speak.py --event success "빌드 및 테스트가 통과했어요!"
  python speak.py --event error "오류가 발생했습니다!"
  # 캐릭터 변경
  python speak.py --character ac_base_emilia01 "에밀리아로 교체 완료!"
"""

import sys
import json
import argparse
import urllib.request
import urllib.parse

def main():
    parser = argparse.ArgumentParser(description="Re:Zero Live2D Codex & Speak CLI")
    parser.add_argument("text", nargs="?", default="", help="표시할 대사 텍스트")
    parser.add_argument("--event", "-ev", choices=["start", "thinking", "success", "error", "warning", "nod"], help="코덱스 이벤트 유형")
    parser.add_argument("--character", "-c", default="", help="변경 또는 지정할 캐릭터 ID (예: ac_base_rem01, ac_base_emilia01)")
    parser.add_argument("--emotion", "-e", default="normal", help="감정 지정 (joy_cheer, crying, angry_pout, thinking, surprise, love_shy, smug_pride, normal)")
    parser.add_argument("--port", "-p", type=int, default=8990, help="컴패니언 포트 번호 (기본 8990)")

    args = parser.parse_args()

    if not args.text.strip() and not args.character and not args.event:
        print("사용법: python speak.py \"텍스트\" [--event <event>] [--character <id>] [--emotion <emotion>]")
        sys.exit(1)

    port = args.port

    if args.event:
        url = f"http://127.0.0.1:{port}/api/event"
        payload = {
            "event": args.event,
            "message": args.text.strip() if args.text.strip() else None
        }
        if args.character:
            payload["character"] = args.character
    else:
        url = f"http://127.0.0.1:{port}/api/speak"
        payload = {
            "text": args.text.strip(),
            "emotion": args.emotion,
        }
        if args.character:
            payload["character"] = args.character

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})

    try:
        with urllib.request.urlopen(req, timeout=6.0) as resp:
            res_data = json.loads(resp.read().decode("utf-8"))
            if res_data.get("success"):
                p = res_data.get("payload", {})
                print(f"Delivered to Re:Zero Companion (Character: {p.get('character')}, Emotion: {p.get('emotion')})")
            else:
                print(f"Error from companion: {res_data.get('error')}")
    except Exception as e:
        print(f"Failed to communicate with Re:Zero Companion on port {port}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
