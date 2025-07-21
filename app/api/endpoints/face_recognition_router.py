from fastapi import APIRouter, File, UploadFile, HTTPException
from typing import List, Dict
import numpy as np
import json  # JSON 문자열 처리를 위해 추가

# FaceNet 모델 로드 (또는 다른 얼굴 인식 라이브러리)
# 실제 환경에서는 모델 로딩에 시간이 걸리므로, 서버 시작 시 한 번만 로드하도록 구성해야 합니다.
# 예시: from app.services.face_recognition_service import FaceRecognitionModel
# face_model = FaceRecognitionModel() # 실제 FaceNet 또는 유사 모델 로딩 로직

router = APIRouter()


# 가상의 얼굴 임베딩 추출 함수 (실제 FaceNet 모델 로직으로 대체 필요)
# 이 함수는 이미지 바이트를 받아 임베딩 리스트를 반환해야 합니다.
def extract_embedding_from_image(image_bytes: bytes) -> List[float]:
    """
    주어진 이미지 바이트에서 얼굴 임베딩을 추출합니다.
    이것은 플레이스홀더 함수이며 실제 FaceNet 모델 로직으로 대체되어야 합니다.
    얼굴을 찾지 못하거나 임베딩 추출에 실패하면 빈 리스트를 반환합니다.
    """
    try:
        # TODO: 여기에 실제 FaceNet 모델을 사용하여 임베딩을 추출하는 로직을 구현하세요.
        # 예시:
        # image = load_image_from_bytes(image_bytes)
        # faces = detect_faces(image)
        # if not faces:
        #     return [] # 얼굴을 찾지 못함
        # embedding = face_model.get_embedding(faces[0]) # 첫 번째 얼굴의 임베딩
        # return embedding.tolist()

        # 임시 더미 데이터 반환 (실제 구현 시 제거)
        # 실제 임베딩은 보통 128 또는 512차원 실수 벡터입니다.
        # 128차원 더미 임베딩 예시
        dummy_embedding = [float(i) / 100.0 for i in range(128)]
        return dummy_embedding
    except Exception as e:
        print(f"얼굴 임베딩 추출 중 오류 발생: {e}")
        return []  # 오류 발생 시 빈 리스트 반환


# 가상의 임베딩 비교 함수 (실제 FaceNet 모델 로직으로 대체 필요)
# 이 함수는 두 임베딩 간의 거리를 계산하고, 임계값 이하이면 일치한다고 판단합니다.
def compare_embeddings_logic(current_embedding: List[float], known_embeddings: List[List[float]],
                             known_user_ids: List[str]) -> Dict:
    """
    현재 임베딩과 알려진 임베딩들을 비교하여 가장 가까운 일치 항목을 찾습니다.
    이것은 플레이스홀더 함수이며 실제 임베딩 비교 로직으로 대체되어야 합니다.
    """
    min_distance = float('inf')
    matched_user_id = None
    match_found = False
    threshold = 0.8  # 임베딩 비교를 위한 임계값 (모델에 따라 조정 필요)

    current_np_embedding = np.array(current_embedding)

    for i, known_emb in enumerate(known_embeddings):
        if not known_emb:  # 빈 임베딩은 건너뛰기
            continue
        known_np_embedding = np.array(known_emb)

        # 유클리드 거리 계산 (또는 코사인 유사도 등)
        distance = np.linalg.norm(current_np_embedding - known_np_embedding)

        if distance < min_distance:
            min_distance = distance
            matched_user_id = known_user_ids[i]

    if matched_user_id and min_distance <= threshold:
        match_found = True

    return {
        "match_found": match_found,
        "matched_user_id": matched_user_id,
        "distance": float(min_distance)  # JSON 직렬화를 위해 float으로 변환
    }


@router.post("/get-face-embedding/")
async def get_face_embedding_endpoint(file: UploadFile = File(...)):
    """
    이미지 파일로부터 얼굴 임베딩을 추출하여 반환합니다.
    """
    image_bytes = await file.read()
    embedding = extract_embedding_from_image(image_bytes)

    if not embedding:
        raise HTTPException(status_code=404, detail="이미지에서 얼굴을 찾을 수 없거나 임베딩 추출에 실패했습니다.")

    return {"embedding": embedding}


@router.post("/compare-embeddings/")
async def compare_embeddings_endpoint(request_data: Dict):
    """
    현재 얼굴 임베딩과 알려진 얼굴 임베딩들을 비교하여 가장 일치하는 얼굴을 찾습니다.
    """
    current_embedding = request_data.get("current_embedding")
    known_embeddings = request_data.get("known_embeddings")
    known_user_ids = request_data.get("known_user_ids")

    if not current_embedding or not known_embeddings or not known_user_ids:
        raise HTTPException(status_code=400, detail="필수 임베딩 데이터가 누락되었습니다.")

    # FastAPI는 기본적으로 JSON을 파싱하므로, Spring에서 보낸 JSON 문자열을
    # Python 리스트로 변환하는 추가적인 파싱이 필요할 수 있습니다.
    # Spring에서 List<List<Float>>를 JSON으로 보내면 FastAPI는 자동으로 List[List[float]]로 파싱합니다.
    # 하지만 혹시 문자열로 넘어온다면, 여기서 json.loads를 사용해야 합니다.
    # 현재 Spring Boot 코드에서는 List<List<Float>>를 직접 보내므로 자동 파싱될 것입니다.

    result = compare_embeddings_logic(current_embedding, known_embeddings, known_user_ids)
    return result
