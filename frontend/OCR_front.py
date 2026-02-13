import streamlit as st
import pandas as pd
import time
import sys
from pathlib import Path

# 프로젝트 루트를 path에 추가 (backend 모듈 import를 위해)
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.api.users import get_user_by_user_id, create_user

# --- 1. Supabase 연동 로그인/회원가입 함수 ---

def check_login(user_id: str, password: str) -> dict:
    """
    로그인 확인 - Supabase users 테이블 조회

    Args:
        user_id: 로그인 ID
        password: 비밀번호

    Returns:
        dict: 로그인 성공 시 사용자 정보, 실패 시 None
    """
    try:
        user = get_user_by_user_id(user_id)
        if user and user.get("password") == password:
            return user
        return None
    except Exception as e:
        st.error(f"DB 연결 오류: {e}")
        return None


def register_user(user_id: str, password: str, name: str = None) -> bool:
    """
    회원가입 - Supabase users 테이블에 추가

    Args:
        user_id: 로그인 ID
        password: 비밀번호
        name: 사용자 이름 (선택, 없으면 user_id 사용)

    Returns:
        bool: 성공 여부
    """
    try:
        # 이미 존재하는지 확인
        existing = get_user_by_user_id(user_id)
        if existing:
            return False

        # 새 사용자 생성
        result = create_user(
            name=name or user_id,
            user_id=user_id,
            password=password
        )
        return result is not None
    except Exception as e:
        st.error(f"회원가입 오류: {e}")
        return False

# --- 2. 페이지 설정 및 세션 상태 초기화 ---
st.set_page_config(page_title="영수증 OCR 장부", layout="wide")

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = None
if 'user_pk' not in st.session_state:
    st.session_state['user_pk'] = None  # DB의 users.id (FK로 사용)
if 'history' not in st.session_state:
    st.session_state['history'] = []

# --- 3. 로그인 / 회원가입 화면 (auth_page) ---
def auth_page():
    st.title("🔐 OCR 장부 시스템")
    tab1, tab2 = st.tabs(["로그인", "회원가입"])
    
    with tab1:
        st.subheader("로그인")
        login_id = st.text_input("아이디", key="login_id")
        login_pw = st.text_input("비밀번호", type="password", key="login_pw")
        if st.button("로그인", use_container_width=True):
            # Supabase users 테이블에서 확인
            user = check_login(login_id, login_pw)
            if user:
                st.session_state['logged_in'] = True
                st.session_state['user_id'] = login_id
                st.session_state['user_pk'] = user.get("id")  # DB의 PK 저장 (영수증 저장 시 필요)
                st.success(f"{login_id}님 환영합니다!")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("아이디 또는 비밀번호가 잘못되었습니다.")
                
    with tab2:
        st.subheader("새 계정 만들기")
        new_id = st.text_input("사용할 아이디", key="new_id")
        new_pw = st.text_input("사용할 비밀번호", type="password", key="new_pw")
        confirm_pw = st.text_input("비밀번호 확인", type="password", key="confirm_pw")
        
        if st.button("회원가입 완료", use_container_width=True):
            if not new_id or not new_pw:
                st.warning("아이디와 비밀번호를 모두 입력해주세요.")
            elif new_pw != confirm_pw:
                st.error("비밀번호가 일치하지 않습니다.")
            else:
                # Supabase users 테이블에 추가
                if register_user(new_id, new_pw):
                    st.success("회원가입 성공! 로그인 탭에서 로그인해주세요.")
                else:
                    st.error("이미 존재하는 아이디입니다.")

# --- 4. 메인 앱 화면 (main_app) ---
def main_app():
    # 사이드바
    st.sidebar.write(f"👤 **{st.session_state['user_id']}**님 접속 중")
    if st.sidebar.button("로그아웃"):
        st.session_state['logged_in'] = False
        st.session_state['user_id'] = None
        st.session_state['user_pk'] = None
        st.rerun()

    st.title("🧾 영수증 OCR 자동 장부 시스템")
    st.info("이미지를 업로드하면 AI가 자동으로 장부를 작성해줍니다. (현재는 데모 모드)")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("1. 영수증 업로드")
        uploaded_file = st.file_uploader("영수증 사진을 선택하세요", type=['jpg', 'jpeg', 'png'])
        if uploaded_file:
            st.image(uploaded_file, caption="업로드된 영수증", use_container_width=True)

    with col2:
        st.subheader("2. 데이터 추출 결과")
        if uploaded_file:
            with st.spinner("이미지에서 텍스트를 추출하는 중..."):
                time.sleep(2) 
                mock_data = {"상호명": "스타벅스 강남점", "날짜": "2026-02-04", "금액": 15600, "카테고리": "식비"}
            
            st.success("추출 완료!")
            with st.form("receipt_form"):
                store_name = st.text_input("상호명", value=mock_data["상호명"])
                date_val = st.text_input("날짜", value=mock_data["날짜"])
                amount = st.number_input("금액", value=mock_data["금액"], step=100)
                category = st.selectbox("카테고리", ["식비", "교통비", "생활용품", "기타"], index=0)
                submit_btn = st.form_submit_button("장부에 저장하기")
                
                if submit_btn:
                    st.balloons()
                    new_data = {"날짜": date_val, "상호명": store_name, "금액": amount, "카테고리": category}
                    st.session_state['history'].append(new_data)
                    st.success(f"✅ {store_name} 저장 완료!")

    st.divider()
    st.subheader("📅 최근 기록된 장부 내역")
    if st.session_state['history']:
        df = pd.DataFrame(st.session_state['history'])
        st.dataframe(df, use_container_width=True)
    else:
        st.write("아직 저장된 내역이 없습니다.")

# --- 5. 실행 로직 (이 부분이 있어야 작동합니다!) ---
if not st.session_state['logged_in']:
    auth_page()
else:
    main_app()
    