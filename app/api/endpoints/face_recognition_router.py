from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse # JSONResponse 임포트 추가
from typing import List, Dict, Any # Any 임포트 추가
import numpy as np
import json
import cv2 # OpenCV 임포트 추가
import face_recognition # face_recognition 임포트 추가
import logging # 로깅 모듈 임포트
import sys # sys 모듈 임포트

# 로거 설정
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 기존 핸들러가 없으면 StreamHandler를 추가합니다. (디버깅 목적)
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(levelname)s:     %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.info("디버깅을 위해 StreamHandler를 로거에 추가했습니다.")

router = APIRouter()

# 실제 얼굴 임베딩 추출 함수
def extract_embedding_from_image(image_bytes: bytes) -> List[float]:
    """
    주어진 이미지 바이트에서 얼굴 임베딩을 추출합니다.
    얼굴을 찾지 못하거나 임베딩 추출에 실패하면 빈 리스트를 반환합니다.
    """
    logger.info("extract_embedding_from_image 함수 호출됨.")
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if frame is None:
            logger.error("이미지 파일을 디코딩할 수 없습니다. frame is None.")
            raise ValueError("이미지 파일을 디코딩할 수 없습니다.")

        # 성능 향상을 위해 프레임 크기 조절 (선택 사항, 그러나 권장)
        # face_recognition은 작은 이미지에서도 잘 작동합니다.
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = np.ascontiguousarray(small_frame[:, :, ::-1]) # OpenCV BGR -> RGB

        logger.info("face_recognition.face_locations 호출 중...")
        face_locations = face_recognition.face_locations(rgb_small_frame)
        logger.info(f"감지된 얼굴 수: {len(face_locations)}")

        if not face_locations:
            logger.warning("이미지에서 얼굴을 찾을 수 없습니다. face_locations is empty.")
            return [] # 얼굴을 찾지 못함

        logger.info("face_recognition.face_encodings 호출 중...")
        # 감지된 첫 번째 얼굴의 임베딩만 추출 (여러 얼굴이 있을 경우 첫 번째 얼굴 사용)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        logger.info(f"추출된 임베딩 수: {len(face_encodings)}")

        if not face_encodings:
            logger.error("얼굴은 감지되었으나 임베딩을 추출할 수 없습니다. face_encodings is empty.")
            return [] # 임베딩 추출 실패

        embedding = face_encodings[0].tolist()
        logger.info(f"추출된 임베딩 (첫 5개 요소): {embedding[:5]}...")
        logger.info(f"추출된 임베딩 (마지막 5개 요소): {embedding[-5:]}...")
        logger.info(f"추출된 임베딩 길이: {len(embedding)}")

        if len(embedding) != 128: # FaceNet의 일반적인 임베딩 차원
            logger.error(f"경고: 추출된 임베딩 길이가 128이 아닙니다: {len(embedding)}")

        return embedding
    except Exception as e:
        logger.error(f"얼굴 임베딩 추출 중 오류 발생: {e}", exc_info=True)
        return [] # 오류 발생 시 빈 리스트 반환

# 실제 임베딩 비교 함수
def compare_embeddings_logic(current_embedding: List[float], known_embeddings: List[List[float]], known_user_ids: List[str]) -> Dict[str, Any]:
    """
    현재 임베딩과 알려진 임베딩들을 비교하여 가장 가까운 일치 항목을 찾습니다.
    face_recognition 라이브러리의 face_distance를 사용합니다.
    """
    logger.info("compare_embeddings_logic 함수 호출됨.")
    min_distance = float('inf')
    matched_user_id = None
    match_found = False
    # 임베딩 비교를 위한 임계값 (0.6 미만이 일반적으로 좋은 일치로 간주됨, 조정 가능)
    # 다른 사람의 얼굴이 인식되는 문제를 해결하기 위해 tolerance를 더 엄격하게 조정합니다.
    threshold = 0.45 # 0.5에서 0.45로 조정 (더 엄격한 일치 요구)

    if not known_embeddings:
        logger.warning("비교할 known_embeddings가 없습니다.")
        return {
            "match_found": False,
            "matched_user_id": None,
            "distance": None
        }

    current_np_embedding = np.array(current_embedding)
    known_np_embeddings = np.array(known_embeddings)

    # face_recognition 라이브러리의 face_distance 함수 사용
    # 이는 current_embedding과 known_embeddings의 각 요소 간 유클리드 거리를 계산합니다.
    face_distances = face_recognition.face_distance(known_np_embeddings, current_np_embedding)

    logger.info(f"계산된 얼굴 거리: {face_distances}")

    if len(face_distances) > 0:
        best_match_index = np.argmin(face_distances)
        min_distance = face_distances[best_match_index]
        logger.info(f"최소 거리: {min_distance}, 최적 일치 인덱스: {best_match_index}")

        if min_distance <= threshold:
            matched_user_id = known_user_ids[best_match_index]
            match_found = True
            logger.info(f"일치하는 사용자 발견: ID={matched_user_id}, 거리={min_distance}")
        else:
            logger.info(f"임계값({threshold}) 초과: 일치하는 사용자를 찾을 수 없습니다. 최소 거리={min_distance}")
    else:
        logger.warning("face_distance 계산 결과가 비어 있습니다.")

    return {
        "match_found": match_found,
        "matched_user_id": matched_user_id,
        "distance": float(min_distance) if min_distance != float('inf') else None # JSON 직렬화를 위해 float으로 변환
    }

@router.post("/get-face-embedding/")
async def get_face_embedding_endpoint(file: UploadFile = File(...)):
    """
    이미지 파일로부터 얼굴 임베딩을 추출하여 반환합니다.
    """
    logger.info(f"/get-face-embedding/ 엔드포인트 호출됨. 파일 타입: {file.content_type}")
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="이미지 파일만 업로드할 수 있습니다.")

    contents = await file.read()
    embedding = extract_embedding_from_image(contents)

    if not embedding:
        logger.warning("/get-face-embedding/: 얼굴을 찾을 수 없거나 임베딩 추출에 실패했습니다.")
        raise HTTPException(status_code=404, detail="이미지에서 얼굴을 찾을 수 없거나 임베딩 추출에 실패했습니다.")

    return JSONResponse(content={"embedding": embedding}) # JSONResponse 명시적 사용

@router.post("/compare-embeddings/")
async def compare_embeddings_endpoint(request_data: Dict[str, Any]): # 타입 힌트 Any 추가
    """
    현재 얼굴 임베딩과 알려진 얼굴 임베딩들을 비교하여 가장 일치하는 얼굴을 찾습니다.
    """
    logger.info("/compare-embeddings/ 엔드포인트 호출됨.")
    current_embedding = request_data.get("current_embedding")
    known_embeddings = request_data.get("known_embeddings")
    known_user_ids = request_data.get("known_user_ids")

    if not current_embedding or not known_embeddings or not known_user_ids:
        logger.error("필수 임베딩 데이터가 누락되었습니다.")
        raise HTTPException(status_code=400, detail="필수 임베딩 데이터가 누락되었습니다.")

    # Spring Boot에서 List<List<Float>>를 JSON으로 보내면 FastAPI는 자동으로 List[List[float]]로 파싱합니다.
    # 따라서 여기서 추가적인 json.loads는 필요 없습니다.

    result = compare_embeddings_logic(current_embedding, known_embeddings, known_user_ids)
    return JSONResponse(content=result) # JSONResponse 명시적 사용

# 임시 테스트 엔드포인트: 이 엔드포인트를 호출하여 로그가 잘 찍히는지 확인합니다.
@router.get("/test-log")
async def test_log():
    logger.info("FastAPI /test-log 엔드포인트가 호출되었습니다. 이 로그가 보인다면 로깅 설정은 정상입니다.")
    return {"message": "로그를 확인해주세요!"}
