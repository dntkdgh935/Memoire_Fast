from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel # Pydantic BaseModel import 추가
import uvicorn
import cv2
import numpy as np
import face_recognition
import os
import io
from typing import List, Dict, Any # 타입 힌트 추가

# 등록할 사용자들의 얼굴 이미지와 이름을 설정합니다.
# 이 디렉토리는 기존 로직을 위해 유지되지만, 새로운 임베딩 저장 방식에서는 Spring Boot가 임베딩을 관리합니다.
KNOWN_FACES_DIR = "known_faces"

# Known face encodings and names (전역 변수로 선언)
# 이 변수들은 향후 Spring Boot에서 관리될 예정입니다.
known_face_encodings = []
known_face_names = []

app = FastAPI()

# CORS 설정: React 애플리케이션에서 접근할 수 있도록 허용합니다.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React 개발 서버 주소
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic 모델 정의: 임베딩 비교 요청을 위한 데이터 구조
class CompareEmbeddingsRequest(BaseModel):
    current_embedding: List[float]
    known_embeddings: List[List[float]]
    known_user_ids: List[str] # 각 임베딩에 해당하는 사용자 ID

# 애플리케이션 시작 시 얼굴 데이터 로드 (기존 로직 유지, 필요에 따라 제거 가능)
@app.on_event("startup")
async def startup_event():
    print("FastAPI 애플리케이션 시작 중...")
    if not os.path.exists(KNOWN_FACES_DIR):
        os.makedirs(KNOWN_FACES_DIR)
        print(f"'{KNOWN_FACES_DIR}' 디렉토리가 생성되었습니다. 이 안에 사용자별 얼굴 이미지를 넣어주세요.")
        print("예: known_faces/홍길동/hong_1.jpg")

    # 새로운 흐름에서는 이 초기 로딩이 덜 중요해질 수 있습니다.
    load_known_faces()


def load_known_faces():
    global known_face_encodings, known_face_names  # 전역 변수 사용 명시
    known_face_encodings = []
    known_face_names = []
    print("등록된 얼굴 데이터를 로드 중...")
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
                            print(f"  - {name}의 얼굴 이미지 로드 완료: {filename}")
                        else:
                            print(f"  - 경고: {image_path} 에서 얼굴을 찾을 수 없습니다.")
                    except Exception as e:
                        print(f"  - 오류: {image_path} 로드 중 오류 발생: {e}")
    print(f"총 {len(known_face_names)}개의 등록된 얼굴 데이터 로드 완료.")


@app.get("/")
async def read_root():
    return {"message": "얼굴 인식 FastAPI 서버입니다."}


@app.post("/recognize-face/")
async def recognize_face(file: UploadFile = File(...)):
    """
    클라이언트로부터 이미지 파일을 받아 얼굴 인식을 수행합니다.
    (이 엔드포인트는 향후 Spring Boot에서 임베딩 비교를 수행할 경우 사용되지 않을 수 있습니다.)
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="이미지 파일만 업로드할 수 있습니다.")

    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if frame is None:
        raise HTTPException(status_code=400, detail="이미지 파일을 디코딩할 수 없습니다.")

    # 성능 향상을 위해 프레임 크기 조절
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = np.ascontiguousarray(small_frame[:, :, ::-1])

    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    results = []
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        name = "Unknown"
        is_matched = False

        if known_face_encodings:  # 등록된 얼굴이 있을 경우에만 비교
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding,
                                                     tolerance=0.5)  # tolerance 조절 가능
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


@app.post("/register-face/{user_name}")
async def register_face(user_name: str, file: UploadFile = File(...)):
    """
    새로운 사용자 얼굴을 등록합니다.
    (이 엔드포인트는 향후 Spring Boot에서 임베딩을 관리할 경우 사용되지 않을 수 있습니다.)
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="이미지 파일만 업로드할 수 있습니다.")

    user_dir = os.path.join(KNOWN_FACES_DIR, user_name)
    os.makedirs(user_dir, exist_ok=True)

    file_path = os.path.join(user_dir, file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    # 새로운 얼굴 등록 후 데이터 다시 로드
    load_known_faces()

    return JSONResponse(content={"message": f"{user_name}의 얼굴이 성공적으로 등록되었습니다."})


# Refactor: Move actual embedding extraction logic into this helper function
def extract_embedding_from_image(image_bytes: bytes) -> List[float]:
    """
    주어진 이미지 바이트에서 얼굴 임베딩을 추출합니다.
    얼굴을 찾지 못하거나 임베딩 추출에 실패하면 ValueError를 발생시킵니다.
    """
    nparr = np.frombuffer(image_bytes, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if frame is None:
        raise ValueError("이미지 파일을 디코딩할 수 없습니다.")

    # 얼굴 위치 찾기 (성능을 위해 크기 조절)
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = np.ascontiguousarray(small_frame[:, :, ::-1])

    face_locations = face_recognition.face_locations(rgb_small_frame)

    if not face_locations:
        raise ValueError("이미지에서 얼굴을 찾을 수 없습니다.")

    # 첫 번째 얼굴의 임베딩 추출
    # 여러 얼굴이 있을 경우, 어떤 얼굴을 사용할지 정책이 필요합니다.
    # 여기서는 단순히 첫 번째 얼굴을 사용합니다.
    face_encoding = face_recognition.face_encodings(rgb_small_frame, face_locations)[0]
    return face_encoding.tolist()


@app.post("/get-face-embedding/")
async def get_face_embedding_endpoint(file: UploadFile = File(...)):
    """
    이미지 파일로부터 얼굴 임베딩(embedding) 값을 추출하여 반환합니다.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="이미지 파일만 업로드할 수 있습니다.")

    contents = await file.read()
    try:
        embedding = extract_embedding_from_image(contents)
    except ValueError as e:
        # 얼굴을 찾지 못했거나 디코딩 실패 시 404 Not Found 반환
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        # 그 외 예외 발생 시 500 Internal Server Error 반환
        raise HTTPException(status_code=500, detail=f"얼굴 임베딩 추출 중 오류 발생: {e}")

    return JSONResponse(content={"embedding": embedding})

@app.post("/compare-embeddings/")
async def compare_embeddings(request: CompareEmbeddingsRequest):
    """
    현재 얼굴 임베딩과 알려진 얼굴 임베딩들을 비교하여 가장 일치하는 얼굴을 찾습니다.
    Spring Boot에서 임베딩 데이터를 관리하고, 비교 로직만 FastAPI에 위임합니다.
    """
    current_embedding_np = np.array(request.current_embedding)
    known_embeddings_np = np.array(request.known_embeddings)
    known_user_ids = request.known_user_ids

    if not known_embeddings_np.shape[0] > 0:
        return JSONResponse(content={"matched_user_id": None, "match_found": False, "distance": None})

    # 임베딩 비교 (tolerance는 Spring Boot에서 관리할 수도 있습니다)
    # 여기서는 FastAPI에서 비교하여 결과를 반환합니다.
    face_distances = face_recognition.face_distance(known_embeddings_np, current_embedding_np)

    # 가장 가까운 얼굴 찾기
    best_match_index = np.argmin(face_distances)
    min_distance = face_distances[best_match_index]

    # 임계값(tolerance) 설정 (조절 가능)
    TOLERANCE = 0.5 # 이 값은 Spring Boot에서도 사용될 수 있습니다.

    if min_distance < TOLERANCE:
        matched_user_id = known_user_ids[best_match_index]
        return JSONResponse(content={
            "matched_user_id": matched_user_id,
            "match_found": True,
            "distance": float(min_distance) # JSON 직렬화를 위해 float으로 변환
        })
    else:
        return JSONResponse(content={"matched_user_id": None, "match_found": False, "distance": float(min_distance)})


# 로컬에서 FastAPI 서버 실행 (개발용)
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
