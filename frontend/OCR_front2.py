import streamlit as st
import pandas as pd
import json
import os
import time

# --- 1. 회원 정보 저장용 파일 설정 ---
USER_DB_FILE = "users.json"

def load_users():
    if os.path.exists(USER_DB_FILE):
        with open(USER_DB_FILE, "r") as f:
            return json.load(f)
    return {"admin": "1234"}

def save_user(username, password):
    users = load_users()
    if username in users:
        return False
    users[username] = password
    with open(USER_DB_FILE, "w") as f:
        json.dump(users, f)
    return True

# --- 2. 페이지 설정 및 세션 상태 초기화 ---
st.set_page_config(page_title="영수증 OCR 장부", layout="wide")

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = None
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
            users = load_users()
            if login_id in users and users[login_id] == login_pw:
                st.session_state['logged_in'] = True
                st.session_state['user_id'] = login_id
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
                if save_user(new_id, new_pw):
                    st.success("회원가입 성공! 로그인 탭에서 로그인해주세요.")
                else:
                    st.error("이미 존재하는 아이디입니다.")

def main_app():
    # --- [사용자 정보 및 로그아웃] ---
    st.sidebar.write(f"👤 **{st.session_state['user_id']}**님 접속 중")
    if st.sidebar.button("로그아웃"):
        st.session_state['logged_in'] = False
        st.session_state['user_id'] = None
        st.rerun()

    st.title("🧾 영수증 OCR 자동 장부 시스템")
    st.info("여러 장의 영수증을 한 번에 업로드하고 내용을 확인한 뒤 저장하세요.")

    # --- [1. 파일 업로드 섹션] ---
    # accept_multiple_files=True: 드래그 앤 드롭이나 파일 선택 시 여러 개를 동시에 받을 수 있게 함
    uploaded_files = st.file_uploader(
        "영수증 사진들을 선택하세요 (JPG, PNG)", 
        type=['jpg', 'jpeg', 'png'], 
        accept_multiple_files=True
    )

    # 파일이 하나라도 업로드 되었을 때만 아래 로직 실행
    if uploaded_files:
        st.divider()
        st.subheader(f"🔍 추출 결과 확인 (총 {len(uploaded_files)}건)")
        
        # 사용자가 수정한 데이터를 임시로 담아둘 리스트 (저장 버튼 클릭 시 세션에 반영)
        temp_data_list = []

        # 각 업로드된 파일에 대해 루프를 돌며 UI 생성
        for idx, file in enumerate(uploaded_files):
            # st.expander: 여러 장일 경우 화면이 길어지므로 영수증별로 접을 수 있게 구성
            with st.expander(f"📄 영수증 #{idx+1} : {file.name}", expanded=True):
                col_img, col_form = st.columns([1, 2])
                
                with col_img:
                    # 업로드된 이미지 미리보기
                    st.image(file, use_container_width=True)
                
                with col_form:
                    # [주의] 실제 서비스 시 이 부분에 OCR API 호출 로직(ex: Clova, Google Vision)이 들어가야 함
                    # 현재는 파일명을 활용한 데모용 더미 데이터 생성
                    mock_data = {
                        "상호명": f"매장_{file.name[:5]}", 
                        "날짜": "2026-03-04", 
                        "금액": 12000 + (idx * 1000), 
                        "카테고리": "식비"
                    }
                    
                    # [중요] Streamlit은 위젯의 key값이 중복되면 에러가 발생함
                    # idx(인덱스)를 활용해 각 입력창에 고유한 key를 부여 (ex: store_0, store_1...)
                    c1, c2 = st.columns(2)
                    store_name = c1.text_input("상호명", value=mock_data["상호명"], key=f"store_{idx}")
                    date_val = c2.text_input("날짜", value=mock_data["날짜"], key=f"date_{idx}")
                    
                    c3, c4 = st.columns(2)
                    amount = c3.number_input("금액", value=mock_data["금액"], step=100, key=f"amt_{idx}")
                    category = c4.selectbox("카테고리", ["식비", "교통비", "생활용품", "기타"], index=0, key=f"cat_{idx}")
                    
                    # 현재 입력창에 있는 값들을 딕셔너리로 묶어 임시 리스트에 추가
                    temp_data_list.append({
                        "날짜": date_val, 
                        "상호명": store_name, 
                        "금액": amount, 
                        "카테고리": category
                    })

        # --- [2. 일괄 저장 버튼] ---
        st.write("") # 간격 조절
        if st.button("💾 위 {0}건의 내역을 모두 장부에 저장".format(len(uploaded_files)), use_container_width=True, type="primary"):
            # 임시 리스트에 담긴 모든 데이터를 세션 상태(history)에 추가
            for data in temp_data_list:
                st.session_state['history'].append(data)
            
            st.balloons() # 성공 축하 효과
            st.success("장부 저장이 완료되었습니다!")
            time.sleep(1) # 사용자에게 메시지를 보여주기 위한 잠깐의 대기
            st.rerun() # 화면을 새로고침하여 아래쪽 테이블에 반영

    # --- [3. 장부 내역 테이블 표시] ---
    st.divider()
    st.subheader("📅 최근 기록된 장부 내역")
    
    if st.session_state['history']:
        # 리스트 데이터를 판다스 데이터프레임으로 변환하여 표 형식으로 출력
        df = pd.DataFrame(st.session_state['history'])
        # 최신 데이터가 위로 오도록 역순(iloc[::-1])으로 표시
        st.dataframe(df.iloc[::-1], use_container_width=True)
        
        # 협업 테스트를 위한 내역 초기화 버튼
        if st.sidebar.button("🗑️ 전체 데이터 초기화"):
            st.session_state['history'] = []
            st.rerun()
    else:
        st.write("아직 저장된 내역이 없습니다. 영수증을 업로드해 보세요!")


# --- 5. 프로그램 실행부 (중요: 가장 아래에 위치) ---
if __name__ == "__main__":
    if not st.session_state['logged_in']:
        auth_page()
    else:
        main_app()