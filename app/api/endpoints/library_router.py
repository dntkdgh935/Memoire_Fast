# # app/api/endpoints/library_router.py
# import os
#
# from fastapi import APIRouter, Body
# from typing import List
# from dotenv import load_dotenv
# from openai import OpenAI
# from app.services.library import keyword_search_service
# from app.core import dbConnectTemplate as dbconn
# import numpy as np
#
# load_dotenv()
# api_key = os.getenv("OPENAI_API_KEY")
# client = OpenAI(api_key=api_key)
#
# router = APIRouter()
#
# # POST /library/search
# # 1. 유저가 검색한 keyword를 받음
# # 2. embedding함
# # 3. DB에서 유사한 순서대로 최대 100개 가져옴.(전체가 더 적을시 있는 만큼)
# @router.post("/search", response_model=List[int])
# def search_collections(query: str = Body(..., embed=True)):
#     print("📥 검색어 수신됨:", query) # ex. "모음"
#     query_embedding = get_embedding(query) #str(get_embedding(query))
#
#     #1. 쿼리 임베딩
#     #print(query+"임베딩 결과:"+ str(get_embedding(query)))
#
#     #2. db에 접속해 query_embedding과 유사한 순서로 id(integer) 리스트 리턴
#     # 2. Oracle DB 연결
#     conn = dbconn.connect()
#     cursor = conn.cursor()
#
#     # 3. 벡터 테이블에서 모든 collection_id와 벡터 가져오기
#     cursor.execute("SELECT collectionid, title_embedding FROM TB_COLLECTION")
#     rows = cursor.fetchall()
#
#     # 4. 코사인 유사도 계산
#     similarity_list = []
#     for row in rows:
#         collection_id = row[0]
#         embedding_str = row[1]  # DB에 저장된 벡터가 문자열 형태라고 가정: "[0.1, 0.2, ...]"
#         if embedding_str is None:
#             # 🔽 title_embedding이 null이면 유사도 최저값(-1.0)으로 간주
#             similarity_list.append((collection_id, -1.0))
#             continue
#         try:
#             vector = np.array(eval(embedding_str))  # 안전하지 않지만 여기선 임시로 eval 사용
#             sim = cosine_similarity(query_embedding, vector)
#             similarity_list.append((collection_id, sim))
#         except Exception as e:
#             print(f"❌ 벡터 변환 실패: {e}")
#             similarity_list.append((collection_id, -1.0))
#
#     # 5. 유사도 순 정렬 및 ID 추출
#     similarity_list.sort(key=lambda x: x[1], reverse=True)
#     ordered_ids = [cid for cid, _ in similarity_list[:100]]
#
#     # 6. 연결 종료
#     cursor.close()
#     dbconn.close(conn)
#
#     print("순서 적용:")
#     print(ordered_ids)
#     return ordered_ids
# #    return #[1001,1002,1003] # 유사도 순서에 따른 리스트 리턴
#
# def get_embedding(text: str, model: str = "text-embedding-3-small") -> list:
#     response = client.embeddings.create(
#         model=model,
#         input=[text]  # 주의: 리스트로 입력해야 함
#     )
#     return response.data[0].embedding
#
# def cosine_similarity(vec1, vec2):
#     vec1 = np.array(vec1)
#     vec2 = np.array(vec2)
#     if np.linalg.norm(vec1) == 0 or np.linalg.norm(vec2) == 0:
#         return 0.0
#     return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))



import os
import ast  # 안전하게 문자열을 리스트로 변환

import oracledb
from fastapi import APIRouter, Body
from typing import List
from dotenv import load_dotenv
from openai import OpenAI
from app.services.library import keyword_search_service
from app.core import dbConnectTemplate as dbconn
import numpy as np

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

router = APIRouter()

# POST /library/search
# 1. 유저가 검색한 keyword를 받음
# 2. embedding함
# 3. DB에서 유사한 순서대로 최대 100개 가져옴.(전체가 더 적을시 있는 만큼)
@router.post("/search", response_model=List[int])
def search_collections(query: str = Body(..., embed=True)):
    print("📥 검색어 수신됨:", query) # ex. "모음"
    logger.info(f"📥 검색어 수신됨: {query}")
    query_embedding = get_embedding(query) #str(get_embedding(query))

    #1. 쿼리 임베딩
    #print(query+"임베딩 결과:"+ str(get_embedding(query)))

    #2. db에 접속해 query_embedding과 유사한 순서로 id(integer) 리스트 리턴
    # 2. Oracle DB 연결
    conn = dbconn.connect()
    cursor = conn.cursor()

    # 3. 벡터 테이블에서 모든 collection_id와 벡터 가져오기
    cursor.execute("SELECT collectionid, title_embedding FROM TB_COLLECTION")
    rows = cursor.fetchall()
    print(type(rows))

    # 4. 코사인 유사도 계산
    similarity_list = []
    for row in rows:
        print("hello", flush=True)
        collection_id = row[0]
        embedding_str = row[1]  # DB에 저장된 벡터가 문자열 형태라고 가정: "[0.1, 0.2, ...]"
        print(type(embedding_str)) #<-- 이게 출력 안 됨

        if embedding_str is None:
            # 🔽 title_embedding이 null이면 유사도 최저값(-1.0)으로 간주
            similarity_list.append((collection_id, -1.0))
            continue
        try:
            # oracledb.LOB 객체가 있는지 확인
            if isinstance(embedding_str, oracledb.LOB):
                embedding_str = embedding_str.read()  # LOB 객체에서 문자열을 읽음

            # 안전하게 문자열을 리스트로 변환
            vector = np.array(ast.literal_eval(embedding_str))  # eval 대신 literal_eval 사용
            sim = cosine_similarity(query_embedding, vector)
            print("유사도 similarity:" + str(sim))
            similarity_list.append((collection_id, sim))
        except Exception as e:
            print(f"❌ 벡터 변환 실패: {e}")
            similarity_list.append((collection_id, -1.0))

    # 5. 유사도 순 정렬 및 ID 추출
    similarity_list.sort(key=lambda x: x[1], reverse=True)
    ordered_ids = [cid for cid, _ in similarity_list[:100]]

    # 6. 연결 종료
    cursor.close()  # 커서 먼저 닫음
    dbconn.close(conn)  # 그 다음 DB 연결 종료

    print("순서 적용:")
    print(ordered_ids)
    return ordered_ids
#    return #[1001,1002,1003] # 유사도 순서에 따른 리스트 리턴

def get_embedding(text: str, model: str = "text-embedding-3-small") -> list:
    response = client.embeddings.create(
        model=model,
        input=[text]  # 주의: 리스트로 입력해야 함
    )
    return response.data[0].embedding

def cosine_similarity(vec1, vec2):
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    if np.linalg.norm(vec1) == 0 or np.linalg.norm(vec2) == 0:
        return 0.0
    return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))
