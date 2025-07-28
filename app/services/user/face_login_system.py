from fastapi import APIRouter, File, UploadFile, HTTPException # APIRouter 임포트
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import cv2
import numpy as np
import face_recognition
import os
import io
from typing import List, Dict, Any
import logging
import sys # sys 모듈 임포트

# 로거 설정
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO) # 로거 레벨을 INFO로 명시적으로 설정합니다.

# 기존 핸들러가 없으면 StreamHandler를 추가합니다. (디버깅 목적)
# 이 코드는 로거가 이미 핸들러를 가지고 있다면 중복 추가를 방지합니다.
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout) # sys.stdout으로 출력하는 핸들러 생성
    formatter = logging.Formatter('%(levelname)s:     %(message)s') # Uvicorn과 유사한 포맷
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.info("디버깅을 위해 StreamHandler를 로거에 추가했습니다.")


# 등록할 사용자들의 얼굴 이미지와 이름을 설정합니다.
KNOWN_FACES_DIR = "known_faces"

# 이 변수들은 router가 로드될 때 초기화되지만,
# 실제 임베딩은 Spring Boot에서 관리하므로 이 부분은 기존 로직 호환을 위해 유지됩니다.
known_face_encodings = []
known_face_names = []

# APIRouter 인스턴스 생성
router = APIRouter()

# load_known_faces 함수는 router의 startup 이벤트에서 호출되거나,
# main.py의 lifespan에서 필요에 따라 호출될 수 있습니다.
# 여기서는 함수 정의만 유지합니다.
def load_known_faces():
    global known_face_encodings, known_face_names
    known_face_encodings = []
    known_face_names = []
    logger.info("등록된 얼굴 데이터를 로드 중...")
    for name in os.listdir(KNOWN_FACES_DIR):
        person_dir = os.path.join(KNOWN_FACES_DIR, name)
        if os.path.isdir(person_dir):
            for filename in os.listdir(person_dir):
                if filename.endswith((".jpg", ".png", ".jpeg")):
                    image_path = os.path.join(person_dir, filename)
                    try:
                        image = face_recognition.load_image_file(image_path)
                        face_encodings = face_recognition.face_encodings(image)
                        if face_encodings:
                            known_face_encodings.append(face_encodings[0])
                            known_face_names.append(name)
                            logger.info(f"  - {name}의 얼굴 이미지 로드 완료: {filename}")
                        else:
                            logger.warning(f"  - 경고: {image_path} 에서 얼굴을 찾을 수 없습니다.")
                    except Exception as e:
                        logger.error(f"  - 오류: {image_path} 로드 중 오류 발생: {e}")
    logger.info(f"총 {len(known_face_names)}개의 등록된 얼굴 데이터 로드 완료.")

# Pydantic 모델 정의
class CompareEmbeddingsRequest(BaseModel):
    current_embedding: List[float]
    known_embeddings: List[List[float]]
    known_user_ids: List[str]

# 이제 모든 엔드포인트는 `router` 인스턴스를 사용합니다.
@router.get("/")
async def read_root():
    return {"message": "얼굴 인식 FastAPI 라우터입니다."} # 메시지 변경

@router.post("/recognize-face/")
async def recognize_face(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="이미지 파일만 업로드할 수 있습니다.")

    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if frame is None:
        raise HTTPException(status_code=400, detail="이미지 파일을 디코딩할 수 없습니다.")

    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = np.ascontiguousarray(small_frame[:, :, ::-1])

    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    results = []
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        name = "Unknown"
        is_matched = False

        if known_face_encodings:
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.5)
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)

            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]
                    is_matched = True

        results.append({
            "name": name,
            "is_matched": is_matched,
            "location": {
                "top": top * 4,
                "right": right * 4,
                "bottom": bottom * 4,
                "left": left * 4
            }
        })

    return JSONResponse(content={"faces": results})

@router.post("/register-face/{user_name}")
async def register_face(user_name: str, file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="이미지 파일만 업로드할 수 있습니다.")

    user_dir = os.path.join(KNOWN_FACES_DIR, user_name)
    os.makedirs(user_dir, exist_ok=True)

    file_path = os.path.join(user_dir, file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    load_known_faces()

    return JSONResponse(content={"message": f"{user_name}의 얼굴이 성공적으로 등록되었습니다."})

def extract_embedding_from_image(image_bytes: bytes) -> List[float]:
    """
    주어진 이미지 바이트에서 얼굴 임베딩을 추출합니다.
    얼굴을 찾지 못하거나 임베딩 추출에 실패하면 ValueError를 발생시킵니다.
    """
    logger.info("extract_embedding_from_image 함수 호출됨.")
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if frame is None:
            logger.error("이미지 파일을 디코딩할 수 없습니다. frame is None.")
            raise ValueError("이미지 파일을 디코딩할 수 없습니다.")

        # 디버깅을 위해 수신된 이미지 저장 (선택 사항, 필요시 주석 해제)
        # cv2.imwrite("received_image_for_embedding.jpg", frame)
        # logger.info("수신된 이미지를 'received_image_for_embedding.jpg'로 저장했습니다.")

        # 성능을 위해 프레임 크기 조절
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = np.ascontiguousarray(small_frame[:, :, ::-1])

        logger.info("face_recognition.face_locations 호출 중...")
        face_locations = face_recognition.face_locations(rgb_small_frame)
        logger.info(f"감지된 얼굴 수: {len(face_locations)}")

        if not face_locations:
            logger.warning("이미지에서 얼굴을 찾을 수 없습니다. face_locations is empty.")
            raise ValueError("이미지에서 얼굴을 찾을 수 없습니다.")

        logger.info("face_recognition.face_encodings 호출 중...")
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        logger.info(f"추출된 임베딩 수: {len(face_encodings)}")

        if not face_encodings:
            logger.error("얼굴은 감지되었으나 임베딩을 추출할 수 없습니다. face_encodings is empty.")
            raise ValueError("얼굴 임베딩을 추출할 수 없습니다.")

        embedding = face_encodings[0].tolist()
        logger.info(f"추출된 임베딩 (첫 5개 요소): {embedding[:5]}...")
        logger.info(f"추출된 임베딩 (마지막 5개 요소): {embedding[-5:]}...")
        logger.info(f"추출된 임베딩 길이: {len(embedding)}")

        if len(embedding) != 128:
            logger.error(f"경고: 추출된 임베딩 길이가 128이 아닙니다: {len(embedding)}")

        return embedding

    except ValueError as ve:
        logger.error(f"ValueError 발생: {ve}")
        raise ve
    except Exception as e:
        logger.error(f"extract_embedding_from_image 함수에서 예기치 않은 오류 발생: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"서버 내부 오류: {e}")

@router.post("/get-face-embedding/")
async def get_face_embedding_endpoint(file: UploadFile = File(...)):
    logger.info(f"/get-face-embedding/ 엔드포인트 호출됨. 파일 타입: {file.content_type}")
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="이미지 파일만 업로드할 수 있습니다.")

    contents = await file.read()
    try:
        embedding = extract_embedding_from_image(contents)
    except ValueError as e:
        logger.warning(f"임베딩 추출 실패 (ValueError): {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"얼굴 임베딩 추출 중 예상치 못한 오류 발생: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"얼굴 임베딩 추출 중 오류 발생: {e}")

    return JSONResponse(content={"embedding": embedding})

@router.post("/compare-embeddings/")
async def compare_embeddings(request: CompareEmbeddingsRequest):
    logger.info("/compare-embeddings/ 엔드포인트 호출됨.")
    current_embedding_np = np.array(request.current_embedding)
    known_embeddings_np = np.array(request.known_embeddings)
    known_user_ids = request.known_user_ids

    logger.info(f"비교할 known_embeddings 개수: {len(known_embeddings_np)}")
    logger.info(f"비교할 known_user_ids 개수: {len(known_user_ids)}")

    if not known_embeddings_np.shape[0] > 0:
        logger.warning("비교할 등록된 임베딩이 없습니다.")
        return JSONResponse(content={"matched_user_id": None, "match_found": False, "distance": None})

    face_distances = face_recognition.face_distance(known_embeddings_np, current_embedding_np)

    best_match_index = np.argmin(face_distances)
    min_distance = face_distances[best_match_index]

    TOLERANCE = 0.10
    logger.info(f"최소 거리: {min_distance}, TOLERANCE: {TOLERANCE}")

    if min_distance < TOLERANCE:
        matched_user_id = known_user_ids[best_match_index]
        logger.info(f"일치하는 사용자 ID 발견: {matched_user_id}, 거리: {min_distance}")
        return JSONResponse(content={
            "matched_user_id": matched_user_id,
            "match_found": True,
            "distance": float(min_distance)
        })
    else:
        logger.info(f"일치하는 사용자 없음. 최소 거리 {min_distance}가 TOLERANCE {TOLERANCE}보다 큽니다.")
        return JSONResponse(content={"matched_user_id": None, "match_found": False, "distance": float(min_distance)})

# 임시 테스트 엔드포인트: 이 엔드포인트를 호출하여 로그가 잘 찍히는지 확인합니다.
@router.get("/test-log")
async def test_log():
    logger.info("FastAPI /test-log 엔드포인트가 호출되었습니다. 이 로그가 보인다면 로깅 설정은 정상입니다.")
    return {"message": "로그를 확인해주세요!"}

# 이 파일은 router로 사용되므로, if __name__ == "__main__": 블록은 실행되지 않아야 합니다.
# FastAPI 애플리케이션은 main.py에서 uvicorn에 의해 시작됩니다.
# if __name__ == "__main__":
#     uvicorn.run(app, host="127.0.0.1", port=8000)
