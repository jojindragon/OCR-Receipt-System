import streamlit as st
import pandas as pd
import time
import tempfile
import os
import sys
from pathlib import Path

# 프로젝트 루트를 path에 추가 (backend 모듈 import를 위해)
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.api.users import get_user_by_user_id, create_user
from backend.api.categories import get_all_categories
from backend.api.receipts import create_receipt
from services.ocr_pipeline2.pipeline.run_pipeline import run_pipeline
from services.ocr_pipeline2.persistence.db_mapper import CATEGORY_MAP, PAYMENT_MAP

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
    # --- [사용자 정보 및 로그아웃] ---
    st.sidebar.write(f"👤 **{st.session_state['user_id']}**님 접속 중")
    if st.sidebar.button("로그아웃"):
        st.session_state['logged_in'] = False
        st.session_state['user_id'] = None
        st.session_state['user_pk'] = None
        st.rerun()

    st.title("🧾 영수증 OCR 자동 장부 시스템")
    st.info("여러 장의 영수증을 한 번에 업로드하고 내용을 확인한 뒤 저장하세요.")

    # --- [카테고리 목록을 DB에서 로드] ---
    # categories 테이블에서 전체 목록을 가져와 selectbox에 사용
    if 'categories' not in st.session_state:
        try:
            cat_list = get_all_categories()
            # {카테고리명: PK} 매핑 딕셔너리 생성
            st.session_state['categories'] = {c["name"]: c["id"] for c in cat_list}
        except Exception as e:
            st.warning(f"카테고리 로드 실패: {e}")
            st.session_state['categories'] = {}

    category_names = list(st.session_state['categories'].keys())

    # --- [1. 파일 업로드 섹션] ---
    uploaded_files = st.file_uploader(
        "영수증 사진들을 선택하세요 (JPG, PNG)",
        type=['jpg', 'jpeg', 'png'],
        accept_multiple_files=True
    )

    # --- [OCR 파이프라인 실행 - 업로드된 파일별로 결과를 세션에 캐싱] ---
    if 'ocr_results' not in st.session_state:
        st.session_state['ocr_results'] = {}

    if uploaded_files:
        for file in uploaded_files:
            # 이미 OCR 처리된 파일은 건너뜀 (파일명 기준 캐싱)
            if file.name not in st.session_state['ocr_results']:
                with st.spinner(f"🔍 {file.name} OCR 처리 중..."):
                    try:
                        # 업로드된 파일을 임시 파일로 저장 (파이프라인이 파일 경로를 필요로 함)
                        suffix = Path(file.name).suffix
                        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
                        tmp.write(file.getbuffer())
                        tmp.close()

                        # ocr_pipeline2의 run_pipeline 호출 (DB 자동 저장 없이 OCR/파싱/검증만)
                        result = run_pipeline(tmp.name, verbose=False)
                        st.session_state['ocr_results'][file.name] = result

                        # 임시 파일 삭제
                        os.unlink(tmp.name)
                    except Exception as e:
                        st.session_state['ocr_results'][file.name] = {
                            "validation_status": "error",
                            "error_msg": str(e)
                        }

        st.divider()
        st.subheader(f"🔍 추출 결과 확인 (총 {len(uploaded_files)}건)")

        # 사용자가 수정한 데이터를 임시로 담아둘 리스트 (저장 버튼 클릭 시 DB에 반영)
        temp_data_list = []

        for idx, file in enumerate(uploaded_files):
            ocr_data = st.session_state['ocr_results'].get(file.name, {})

            # OCR 파싱 결과에서 상호명/날짜/금액/카테고리 추출
            parsed_store = ocr_data.get("store_name", "")
            parsed_date = ocr_data.get("transaction_date", "")
            parsed_total = ocr_data.get("total", 0)
            parsed_category = ocr_data.get("category", "기타")
            parsed_payment = ocr_data.get("payment", "")
            validation_status = ocr_data.get("validation_status", "error")

            with st.expander(f"📄 영수증 #{idx+1} : {file.name}", expanded=True):
                col_img, col_form = st.columns([1, 2])

                with col_img:
                    st.image(file, use_column_width=True)
                    # OCR 검증 상태 표시
                    if validation_status == "success":
                        st.success("✅ OCR 인식 성공")
                    elif validation_status == "review_required":
                        st.warning("⚠️ 검토 필요")
                    else:
                        st.error("❌ OCR 인식 실패")

                with col_form:
                    c1, c2 = st.columns(2)
                    store_name = c1.text_input("상호명", value=parsed_store, key=f"store_{idx}")
                    date_val = c2.text_input("날짜", value=parsed_date, key=f"date_{idx}")

                    c3, c4 = st.columns(2)
                    amount = c3.number_input("금액", value=parsed_total, step=100, key=f"amt_{idx}")

                    # DB categories 테이블에서 가져온 카테고리 목록을 selectbox에 표시
                    # OCR이 인식한 카테고리가 목록에 있으면 해당 항목을 기본 선택
                    cat_index = 0
                    if parsed_category in category_names:
                        cat_index = category_names.index(parsed_category)
                    category = c4.selectbox(
                        "카테고리", category_names, index=cat_index, key=f"cat_{idx}"
                    ) if category_names else c4.text_input("카테고리", value=parsed_category, key=f"cat_{idx}")

                    # 선택된 카테고리의 PK값 (UI에는 표시되지 않음)
                    selected_cat_id = st.session_state['categories'].get(category)

                    temp_data_list.append({
                        "store_name": store_name,
                        "date": date_val,
                        "total_amount": amount,
                        "category": category,
                        "category_id": selected_cat_id,
                        "payment": parsed_payment,
                        "payment_method_id": PAYMENT_MAP.get(parsed_payment),
                        "image_path": file.name,
                    })

        # --- [2. 일괄 저장 버튼 - 클릭 시에만 DB에 저장] ---
        st.write("")
        if st.button(
            "💾 위 {0}건의 내역을 모두 장부에 저장".format(len(uploaded_files)),
            use_container_width=True, type="primary"
        ):
            success_count = 0
            fail_count = 0

            for data in temp_data_list:
                try:
                    create_receipt(
                        user_id=st.session_state['user_pk'],
                        category_id=data["category_id"],
                        payment_method_id=data["payment_method_id"],
                        date=data["date"],
                        total_amount=data["total_amount"],
                        store_name=data["store_name"],
                        image_path=data["image_path"],
                    )
                    success_count += 1
                    # 화면 표시용 history에도 추가
                    st.session_state['history'].append({
                        "날짜": data["date"],
                        "상호명": data["store_name"],
                        "금액": data["total_amount"],
                        "카테고리": data["category"],
                    })
                except Exception as e:
                    fail_count += 1
                    st.error(f"❌ {data['store_name']} 저장 실패: {e}")

            if success_count > 0:
                st.balloons()
                st.success(f"✅ {success_count}건 저장 완료!" + (f" ({fail_count}건 실패)" if fail_count else ""))
            # OCR 캐시 초기화 (새로운 업로드를 위해)
            st.session_state['ocr_results'] = {}
            time.sleep(1)
            st.rerun()

    # --- [3. 장부 내역 테이블 표시] ---
    st.divider()
    st.subheader("📅 최근 기록된 장부 내역")

    if st.session_state['history']:
        df = pd.DataFrame(st.session_state['history'])
        # 최신 데이터가 위로 오도록 역순으로 표시
        st.dataframe(df.iloc[::-1], use_container_width=True)

        # 협업 테스트를 위한 내역 초기화 버튼
        if st.sidebar.button("🗑️ 전체 데이터 초기화"):
            st.session_state['history'] = []
            st.rerun()
    else:
        st.write("아직 저장된 내역이 없습니다. 영수증을 업로드해 보세요!")

# --- 5. 실행 로직 (이 부분이 있어야 작동합니다!) ---
if not st.session_state['logged_in']:
    auth_page()
else:
    main_app()
    