# -*- coding: utf-8 -*-
"""
Re:Zero Companion Emotion & Codex Event Engine
텍스트 키워드 및 코덱스(Codex) AI 개발 이벤트에 맞춰 198종 캐릭터의 모션과 표정을 실시간 매핑합니다.
"""

import re

# Codex Events Mapping
CODEX_EVENTS = {
    "start": {
        "emotion": "thinking",
        "default_msg": "코덱스 작업 분석을 시작합니다!",
        "desc": "작업 시작 및 분석"
    },
    "thinking": {
        "emotion": "thinking",
        "default_msg": "코드를 면밀히 분석하고 있습니다...",
        "desc": "심층 분석 및 계획 수립"
    },
    "success": {
        "emotion": "joy_cheer",
        "default_msg": "작업이 성공적으로 완료되었습니다!",
        "desc": "빌드/테스트/작업 성공"
    },
    "error": {
        "emotion": "crying",
        "default_msg": "오류가 발생하여 확인이 필요합니다 ㅠㅠ",
        "desc": "빌드 오류 또는 예외 발생"
    },
    "warning": {
        "emotion": "surprise",
        "default_msg": "주의할 점이 발견되었습니다!",
        "desc": "경고 또는 주의 사항"
    },
    "nod": {
        "emotion": "smug_pride",
        "default_msg": "네, 확인했습니다!",
        "desc": "확인 및 긍정 응답"
    }
}

EMOTIONS = {
    "joy_cheer": "환호/기쁨 (성공·행복)",
    "crying": "슬픔/눈물 (오류·실패)",
    "angry_pout": "화남/삐짐/반박",
    "thinking": "고민/생각/진단",
    "surprise": "놀람/당황",
    "love_shy": "부끄러움/애정",
    "smug_pride": "자신감/당당",
    "normal": "일반/대화"
}

KEYWORD_PATTERNS = [
    ("crying", [r"ㅠㅠ", r"ㅜㅜ", r"흑흑", r"슬픈", r"실패", r"오류", r"에러", r"망했", r"아쉽", r"괴로"]),
    ("surprise", [r"경고", r"비상", r"위험", r"과부하", r"초과", r"사고", r"큰일", r"헉", r"깜짝"]),
    ("angry_pout", [r"화나", r"삐졌", r"바보", r"아니야", r"그만", r"틀렸", r"싫어", r"흥"]),
    ("joy_cheer", [r"성공", r"완료", r"해결", r"대박", r"최고", r"만세", r"축하", r"기뻐", r"좋아", r"신나"]),
    ("love_shy", [r"사랑", r"좋아해", r"고마워", r"감사", r"부끄", r"헤헤", r"스바루 군"]),
    ("smug_pride", [r"당연", r"맡겨", r"자신", r"식은 죽", r"완벽", r"훌륭"]),
    ("thinking", [r"생각", r"고민", r"분석", r"확인", r"검토", r"조사", r"점검", r"진행 중"])
]

def analyze_emotion(text):
    raw_text = text or ""
    clean_text = raw_text.strip()

    # Check explicit tag: [joy_cheer], [crying], etc.
    tag_match = re.match(r"^\[([a-zA-Z_]+)\]\s*", clean_text)
    if tag_match:
        emo_tag = tag_match.group(1).lower()
        if emo_tag in EMOTIONS:
            clean_text = clean_text[tag_match.end():]
            return {
                "key": emo_tag,
                "name": EMOTIONS[emo_tag],
                "clean_text": clean_text
            }

    # Keyword search
    for emo_key, patterns in KEYWORD_PATTERNS:
        for p in patterns:
            if re.search(p, clean_text, re.IGNORECASE):
                return {
                    "key": emo_key,
                    "name": EMOTIONS.get(emo_key, "일반"),
                    "clean_text": clean_text
                }

    return {
        "key": "normal",
        "name": "일반/대화",
        "clean_text": clean_text
    }
