# =============================================================================
# OCR_mobile.py - 모바일 전용 UI
# =============================================================================
# 담당: 프론트엔드
# 설명: 모바일 기기에 최적화된 영수증 OCR 시스템 UI
#       - app.py에서 모바일 감지 시 이 파일로 분기
#       - OCR_front.py와 동일한 기능 (로그인/회원가입 + 메인)
#       - 세로 레이아웃, 큰 버튼, 터치 친화적 구성
#
# 주요 차이점 (OCR_front.py 대비):
#       - layout="centered" (좁은 화면에 최적화)
#       - 2컬럼 → 1컬럼 세로 배치
#       - 사이드바 없음 → 상단 메뉴로 대체
#       - 모바일 친화적 CSS 적용
# =============================================================================

import streamlit as st
import pandas as pd
import time
import sys
from pathlib import Path

# 프로젝트 루트를 path에 추가 (backend 모듈 import를 위해)
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.api.users import get_user_by_user_id, create_user


# =============================================================================
# 1. 모바일 전용 CSS 스타일
# =============================================================================
# 모바일 화면에서 터치하기 쉽도록 버튼, 입력창 크기를 키움
# =============================================================================
def apply_mobile_style():
    st.markdown("""
    <style>
        /* 메인 컨테이너 패딩 축소 */
        .block-container {
            padding-top: 1rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }

        /* 입력창 높이 확대 (터치 친화적) */
        .stTextInput > div > div > input {
            font-size: 16px;
            padding: 12px;
        }

        /* 버튼 크기 확대 */
        .stButton > button {
            font-size: 18px;
            padding: 12px;
            border-radius: 10px;
        }

        /* 사이드바 숨기기 */
        [data-testid="stSidebar"] {
            display: none;
        }

        /* 파일 업로더 확대 */
        [data-testid="stFileUploader"] {
            padding: 10px;
        }

        /* 탭 폰트 크기 확대 */
        .stTabs [data-baseweb="tab"] {
            font-size: 16px;
            padding: 10px 16px;
        }
    </style>
    """, unsafe_allow_html=True)


# =============================================================================
# 2. Supabase 연동 로그인/회원가입 함수
# =============================================================================
# OCR_front.py와 동일한 로직
# =============================================================================

def check_login(user_id: str, password: str) -> dict:
    """로그인 확인 - Supabase users 테이블 조회"""
    try:
        user = get_user_by_user_id(user_id)
        if user and user.get("password") == password:
            return user
        return None
    except Exception as e:
        st.error(f"DB 연결 오류: {e}")
        return None


def register_user(user_id: str, password: str, name: str = None) -> bool:
    """회원가입 - Supabase users 테이블에 추가"""
    try:
        existing = get_user_by_user_id(user_id)
        if existing:
            return False
        result = create_user(
            name=name or user_id,
            user_id=user_id,
            password=password
        )
        return result is not None
    except Exception as e:
        st.error(f"회원가입 오류: {e}")
        return False


# =============================================================================
# 3. 세션 상태 초기화
# =============================================================================
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = None
if 'user_pk' not in st.session_state:
    st.session_state['user_pk'] = None
if 'history' not in st.session_state:
    st.session_state['history'] = []


# =============================================================================
# 4. 모바일 로그인 / 회원가입 화면
# =============================================================================
# - 세로 중앙 정렬
# - 큰 입력창과 버튼
# =============================================================================
def auth_page():
    st.markdown("<h2 style='text-align: center;'>🔐 OCR 장부</h2>", unsafe_allow_html=True)
    st.markdown("---")

    tab1, tab2 = st.tabs(["로그인", "회원가입"])

    # --- 로그인 탭 ---
    with tab1:
        login_id = st.text_input("아이디", key="m_login_id", placeholder="아이디를 입력하세요")
        login_pw = st.text_input("비밀번호", type="password", key="m_login_pw", placeholder="비밀번호를 입력하세요")

        st.markdown("")  # 여백

        if st.button("로그인", use_container_width=True, type="primary"):
            # Supabase users 테이블에서 확인
            user = check_login(login_id, login_pw)
            if user:
                st.session_state['logged_in'] = True
                st.session_state['user_id'] = login_id
                st.session_state['user_pk'] = user.get("id")
                st.success(f"{login_id}님 환영합니다!")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("아이디 또는 비밀번호가 잘못되었습니다.")

    # --- 회원가입 탭 ---
    with tab2:
        new_id = st.text_input("사용할 아이디", key="m_new_id", placeholder="아이디")
        new_pw = st.text_input("사용할 비밀번호", type="password", key="m_new_pw", placeholder="비밀번호")
        confirm_pw = st.text_input("비밀번호 확인", type="password", key="m_confirm_pw", placeholder="비밀번호 확인")

        st.markdown("")  # 여백

        if st.button("회원가입 완료", use_container_width=True, type="primary"):
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


# =============================================================================
# 5. 모바일 메인 앱 화면
# =============================================================================
# - 사이드바 대신 상단에 사용자 정보 + 로그아웃
# - 2컬럼 대신 세로 1컬럼 배치
# - 영수증 업로드 → 추출 결과 → 장부 내역 순서
# =============================================================================
def main_app():
    # --- 상단 헤더 (사이드바 대체) ---
    header_col1, header_col2 = st.columns([3, 1])
    with header_col1:
        st.markdown(f"👤 **{st.session_state['user_id']}**님")
    with header_col2:
        if st.button("로그아웃", use_container_width=True):
            st.session_state['logged_in'] = False
            st.session_state['user_id'] = None
            st.session_state['user_pk'] = None
            st.rerun()

    st.markdown("---")
    st.markdown("<h3 style='text-align: center;'>🧾 영수증 OCR 장부</h3>", unsafe_allow_html=True)
    st.info("이미지를 업로드하면 AI가 자동으로 장부를 작성해줍니다. (현재는 데모 모드)")

    # --- 영수증 업로드 (세로 배치) ---
    st.subheader("📸 영수증 업로드")
    uploaded_file = st.file_uploader("영수증 사진을 선택하세요", type=['jpg', 'jpeg', 'png'])
    if uploaded_file:
        st.image(uploaded_file, caption="업로드된 영수증", use_container_width=True)

    # --- 데이터 추출 결과 (세로 배치) ---
    if uploaded_file:
        st.markdown("---")
        st.subheader("📝 데이터 추출 결과")

        with st.spinner("이미지에서 텍스트를 추출하는 중..."):
            time.sleep(2)
            mock_data = {"상호명": "스타벅스 강남점", "날짜": "2026-02-04", "금액": 15600, "카테고리": "식비"}

        st.success("추출 완료!")

        with st.form("m_receipt_form"):
            store_name = st.text_input("상호명", value=mock_data["상호명"])
            date_val = st.text_input("날짜", value=mock_data["날짜"])
            amount = st.number_input("금액", value=mock_data["금액"], step=100)
            category = st.selectbox("카테고리", ["식비", "교통비", "생활용품", "기타"], index=0)
            submit_btn = st.form_submit_button("💾 장부에 저장하기", use_container_width=True)

            if submit_btn:
                st.balloons()
                new_data = {"날짜": date_val, "상호명": store_name, "금액": amount, "카테고리": category}
                st.session_state['history'].append(new_data)
                st.success(f"✅ {store_name} 저장 완료!")

    # --- 장부 내역 (세로 배치) ---
    st.markdown("---")
    st.subheader("📅 최근 장부 내역")
    if st.session_state['history']:
        df = pd.DataFrame(st.session_state['history'])
        st.dataframe(df, use_container_width=True)
    else:
        st.write("아직 저장된 내역이 없습니다.")


# =============================================================================
# 6. 실행 로직
# =============================================================================
# 모바일 CSS 적용 후, 로그인 상태에 따라 분기
# =============================================================================
apply_mobile_style()

if not st.session_state['logged_in']:
    auth_page()
else:
    main_app()