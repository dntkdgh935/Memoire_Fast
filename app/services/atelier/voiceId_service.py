import re

def sanitize_voice_id(voice_id: str) -> str:
    # 순수 ID가 유효한 경우 그대로 사용
    if voice_id in VOICE_NAME_TO_ID.values():
        return voice_id

    # "Name (ID)" 형식이면 괄호 안만 추출
    match = re.search(r'\(([^)]+)\)', voice_id)
    if match:
        possible_id = match.group(1)
        if possible_id in VOICE_NAME_TO_ID.values():
            return possible_id

    # 이름으로만 들어온 경우
    if voice_id in VOICE_NAME_TO_ID:
        return VOICE_NAME_TO_ID[voice_id]

    raise ValueError(f"Invalid voice_id received: {voice_id}")

VOICE_NAME_TO_ID = {
    "Adam": "pNInz6obpgDQGcFmaJgB",
    "Alice": "Xb7hH8MSUJpSbSDYk0k2",
    "Antoni": "ErXwobaYiN019PkySvjV",
    "Arnold": "VR6AewLTigWG4xSOukaG",
    "Bill": "pqHfZKP75CvOlQylNhV4",
    "Brian": "nPczCjzI2devNBz1zQrb",
    "Callum": "N2lVS1w4EtoT3dr4eOWO",
    "Charlie": "IKne3meq5aSn9XLyUdCD",
    "Charlotte": "XB0fDUnXU5powFXDhCwa",
    "Chris": "iP95p4xoKVk53GoZ742B",
    "Clyde": "2EiwWnXFnvU5JabPnv8n",
    "Daniel": "onwK4e9ZLuTAKqWW03F9",
    "Dave": "CYw3kZ02Hs0563khs1Fj",
    "Domi": "AZnzlk1XvdvE nXmlld",
    "Dorothy": "ThT5KcBeYPX3keUQqHPh",
    "Drew": "29vD33N1CtxCmqQRPOHJ",
    "Emily": "LcfcDJNUP1GQjkzn1xUU",
    "Ethan": "g5CIjZEefAph4nQFvHAz",
    "Fin": "D38z5RcWu1voky8WS1ja",
    "Freya": "jsCqWAovK2LkecY7zXl4",
    "George": "JBFqnCBsd6RMkjVDRZzb",
    "Gigi": "jBpfuIE2acCO8z3wKNLl",
    "Giovanni": "zcAOhNBS3c14rBihAFp1",
    "Glinda": "z9fAnlkpzviPz146aGWa",
    "Grace": "oWAxZDx7w5VEj9dCyTzz",
    "Harry": "SOYHLrjzK2X1ezoPC6cr",
    "James": "ZQe5CZNOzWyzPSCn5a3c",
    "Jeremy": "bVMeCyTHy58xNoL34h3p",
    "Jessie": "t0jbNlBVZ17f02VDIeMI",
    "Joseph": "Zlb1dXrM653N07WRdFW3",
    "Josh": "TxGEqnHWrfWFTfGW9XjX",
    "Liam": "TX3LPaxmHKxFdv7VOQHJ",
    "Lily": "pFZP5JQG7iQjIQuC4Bku",
    "Matilda": "XrExE9yKIg1WjnnlVkGX",
    "Michael": "flq6f7yk4E4fJM5XTYuZ",
    "Mimi": "zrHiDhphv9ZnVXBqCLjz",
    "Nicole": "piTKgcLEGmPE4e6mEKli",
    "Patrick": "ODq5zmih8GrVes37Dizd",
    "Paul": "5Q0t7uMcjvnagumLfvZi",
    "Rachel": "21m00Tcm4TlvDq8ikWAM",
    "Sam": "yoZ06aMxZJJ28mfd3POQ",
    "Sarah": "EXAVITQu4vr4xnSDxMaL",
    "Serena": "pMsXgVXv3BLzUgSXRplE",
    "Thomas": "GBv7mTt0atIp3Br8iCZE",
    "Santa Claus": "knrPHWnBmmDHMoiMeP3l"
}
