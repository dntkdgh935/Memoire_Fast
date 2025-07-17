# app/services/library/recommend_service.py

# import cx_Oracle
import numpy as np
import faiss
from sklearn.preprocessing import normalize

import app.core.dbConnectTemplate as dbtemp
import oracledb

dbtemp.oracle_init()
conn=dbtemp.connect()

# Oracle DB 연결 함수
# DB 연결을 바탕으로, user_id가 좋아요한 컬렉션들을 조회해 옴
def get_liked_items_from_db(user_id: str):
    pass

def get_bookmarked_items_from_db(user_id: str):
    pass

def recommend_items():
    pass
    # 유저가 인터랙션한 아이템 리스트들(collid, titleEmbedding)을 받음
    #