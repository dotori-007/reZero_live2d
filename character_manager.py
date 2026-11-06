# -*- coding: utf-8 -*-
import os
import re
import json

APP_DIR = os.path.dirname(os.path.abspath(__file__))
CHARACTERS_DIR = os.path.join(APP_DIR, "Live2D Characters")

NAME_MAP = {
    "rem": "렘 (Rem)",
    "emilia": "에밀리아 (Emilia)",
    "ram": "람 (Ram)",
    "beatrice": "베아트리스 (Beatrice)",
    "subaru": "스바루 (Subaru)",
    "echidna": "에키드나 (Echidna)",
    "felt": "펠트 (Felt)",
    "ferris": "페리스 (Ferris)",
    "crusch": "크루쉬 (Crusch)",
    "priscilla": "프리실라 (Priscilla)",
    "reinhard": "라인하르트 (Reinhard)",
    "petelgeuse": "페텔기우스 (Petelgeuse)",
    "roswaal": "로즈월 (Roswaal)",
    "otto": "오토 (Otto)",
    "garfiel": "가필 (Garfiel)",
    "frederica": "프레데리카 (Frederica)",
    "petra": "페트라 (Petra)",
    "wilhelm": "빌헬름 (Wilhelm)",
    "julius": "율리우스 (Julius)",
    "anastasia": "아나스타시아 (Anastasia)",
    "mimi": "미미 (Mimi)",
    "hetaro": "헤타로 (Hetaro)",
    "tibby": "티비 (Tibby)",
    "ricardo": "리카도 (Ricardo)",
    "elsa": "엘자 (Elsa)",
    "pack": "팩 (Pack)",
    "patrasche": "파트라슈 (Patrasche)",
    "satella": "사텔라 (Satella)",
    "theresia": "테레시아 (Theresia)",
    "regulus": "레굴루스 (Regulus)",
    "shion": "시온 (Shion)",
    "alcor": "알코르 (Alcor)",
    "cain": "카인 (Cain)",
    "whitewhale": "백경 (하쿠게이)",
    "al": "알 (Al)",
    "bordeaux": "보르도 (Bordeaux)",
    "kadomon": "카도몬 (Kadomon)",
    "rom": "롬영감 (Rom)",
    "mild": "밀드 (Mild)",
    "milde": "밀데 (Milde)",
    "marcos": "마르코스 (Marcos)",
    "miklotov": "미클로토프 (Miklotov)",
    "russell": "러셀 (Russell)",
    "zelga": "젤가 (Zelga)",
    "witchcult": "마녀교도 (Witch Cult)",
}

COSTUME_MAP = {
    "dress": "드레스",
    "kimono": "기모노",
    "nemaki": "잠옷",
    "mizugi": "수영복",
    "wedding": "웨딩",
    "halloween": "할로윈",
    "xmas": "크리스마스",
    "valentine": "발렌타인",
    "newyear": "신년",
    "childhood": "유년기",
    "after20y": "20년 후",
    "ogre": "오니화",
    "armor": "갑옷",
    "prison": "죄수복",
    "formal": "정장",
    "butler": "집사복",
    "jersey": "저지",
    "robe": "로브",
    "hood": "후드",
    "maid": "메이드복",
    "private": "사복",
    "shadow": "그림자",
    "pokerface": "포커페이스",
    "undead": "언데드",
    "young": "청년기",
    "true": "진형태",
}

def parse_character_info(folder_name):
    # e.g. ac_base_rem_mizugi01 -> base: rem, costume: mizugi, ver: 01
    name_clean = folder_name.replace("ac_base_", "")
    
    char_key = None
    costume_key = None
    
    for k in sorted(NAME_MAP.keys(), key=lambda x: -len(x)):
        if name_clean.startswith(k):
            char_key = k
            remainder = name_clean[len(k):].strip("_")
            break
            
    if not char_key:
        char_key = name_clean.split("_")[0]
        display_base = char_key.capitalize()
    else:
        display_base = NAME_MAP.get(char_key, char_key.capitalize())
        
    costume_label = "기본"
    if char_key and name_clean[len(char_key):]:
        remainder = name_clean[len(char_key):].strip("_")
        for ck in sorted(COSTUME_MAP.keys(), key=lambda x: -len(x)):
            if ck in remainder:
                costume_label = COSTUME_MAP[ck]
                break
        if costume_label == "기본" and remainder:
            m = re.search(r'([a-zA-Z]+)', remainder)
            if m and m.group(1) not in ["", "01", "02", "03"]:
                costume_label = m.group(1).capitalize()

    full_display = f"{display_base} - {costume_label}"
    category = display_base.split(" ")[0]
    
    return {
        "id": folder_name,
        "base_key": char_key,
        "category": category,
        "displayName": full_display,
        "baseName": display_base,
        "costume": costume_label,
    }

class CharacterManager:
    def __init__(self, root_dir=CHARACTERS_DIR):
        self.root_dir = root_dir
        self.characters = {}
        self.categories = set()
        self.scan_characters()

    def scan_characters(self):
        self.characters.clear()
        self.categories.clear()
        
        if not os.path.exists(self.root_dir):
            return

        for folder in sorted(os.listdir(self.root_dir)):
            folder_path = os.path.join(self.root_dir, folder)
            if not os.path.isdir(folder_path):
                continue
            
            # Find .model3.json
            mjs_list = [f for f in os.listdir(folder_path) if f.endswith(".model3.json")]
            if not mjs_list:
                continue
            
            model_file = mjs_list[0]
            info = parse_character_info(folder)
            info["modelFile"] = model_file
            info["folder"] = folder
            
            # Check motions and expressions
            motions_dir = os.path.join(folder_path, "motions")
            if os.path.isdir(motions_dir):
                info["motions"] = sorted(os.listdir(motions_dir))
            else:
                info["motions"] = []

            expressions_dir = os.path.join(folder_path, "expressions")
            if os.path.isdir(expressions_dir):
                info["expressions"] = sorted(os.listdir(expressions_dir))
            else:
                info["expressions"] = []
                
            self.characters[folder] = info
            self.categories.add(info["category"])

    def get_character(self, char_id):
        return self.characters.get(char_id)

    def list_characters(self):
        return list(self.characters.values())

    def get_motion_for_emotion(self, char_id, emotion):
        info = self.get_character(char_id)
        if not info or not info["motions"]:
            return None
        
        motions = info["motions"]
        
        # Keyword mappings for Re:Zero motions
        keywords = {
            "joy_cheer": ["egao", "hohoemu", "zerokara"],
            "crying": ["kurushimu", "kanashimu", "uru"],
            "angry_pout": ["punpun", "ikaru", "suneru"],
            "thinking": ["kangaeru", "nayamu", "shinken"],
            "surprise": ["odoroku", "bikkuri"],
            "smug_pride": ["egao", "hohoemu", "unazuku"],
            "love_shy": ["tere", "hohoemu", "uru"],
            "nod": ["unazuku", "normal"],
            "normal": ["normal", "hohoemu", "talk_normal"]
        }
        
        target_keys = keywords.get(emotion, ["normal", "egao"])
        
        # First priority: body act motion
        for tk in target_keys:
            for m in motions:
                m_lower = m.lower()
                if "act" in m_lower and tk in m_lower and not m_lower.endswith("_w.motion3.json"):
                    return m
        # Second priority: any motion with keyword
        for tk in target_keys:
            for m in motions:
                m_lower = m.lower()
                if tk in m_lower:
                    return m
                    
        # Fallback to first motion
        return motions[0] if motions else None

char_mgr = CharacterManager()
