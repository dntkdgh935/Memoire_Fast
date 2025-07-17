# path : common\\dbConnectTemplate.py
# module : common.deBonnectTemplate
# 오라클 db 연결 관리용 공통 모듈 (oracledb 모듈 사용 기반)

# oracledb 모듈 :
# 오라클 공식 python 모듈임
# 두 가지 실행 모드를 제공함 : Thin 모드, Thick 모드
'''
Thin 모드 (기본 모드)
- Thick 보다 성능 떨어짐 (보통)
- 오라클 사용 일부 제한됨 => 인증/보안/고급 연결 제한됨
- 클라우드 간편 실행 환경에 적합

Thick 모드 (cx_Oracle 방식과 같음, 성능도 같음)
- 반드시 환경변수 path 등록과 oracle instant client 설치 필수임
- C 기반 Oracle 네이티브 라이브러리 사용함 => 더 빠르고 최적화됨
- 오라클 전체 기능 사용을 지원함 => 인증/보안/고급 연결 모두 사용 가능함
'''


import oracledb
import os

# Oracle Instant Client  설치 경로 지정 (Thick 모드 사용시 필요함)
# Thin 모드만 사용할 경우 이 초기화는 생략해도 됨
def oracle_init():
    location = 'D:\\instantclient_21_18'
    os.environ['PATH'] = location + ';' + os.environ['PATH']  # 환경변수 PATH 에 경로 추가함
    oracledb.init_oracle_client(lib_dir=location)
    print('oracledb 모드 : ', oracledb.is_thin_mode())   # True 이면 Thin 모드, False 이면 Thick 모드임
# oracle_init() ------------------------------------------------------

# 오라클 연결에 필요한 정보를 전역변수로 설정
# oracledb 는 user/passwd/dsn 형태로 연결하는 것을 권장함
url = 'localhost:1521/xe'  # dsn (Data Source Name)
user = 'c##memoire'
passwd = 'memoire'


# 오라클 db 연결 함수 -------------------
def connect():
    try:
        # 연결시 autocommit = False 가 기본임, 명시해도 됨
        conn = oracledb.connect(user=user, password=passwd, dsn=url)
        conn.autocommit = False
        return conn
    except Exception as e:
        print('오라클 연결 에러 발생 : ', e)
# connect() -------------------------------------

# 연결 종료 함수 ----------------------
def close(conn):
    try:
        if conn:
            conn.close()
    except Exception as e:
        print('오라클 접속 종료 실패 : ', e)
# close(conn) ---------------------------------------

# 트랜잭션 커밋 함수 --------------------
def commit(conn):
    try:
        if conn:
            conn.commit()
    except Exception as e:
        print('오라클 트랜잭션 커밋 실패 : ', e)
# commit(conn) -----------------------------------------

# 트랜잭션 롤백 함수 ------------------
def rollback(conn):
    try:
        if conn:
            conn.rollback()
    except Exception as e:
        print('오라클 트랜잭션 롤백 실패 : ', e)
# rollback(conn) ----------------------------------------











