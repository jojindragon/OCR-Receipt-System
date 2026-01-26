"""
OCR Receipt System - Main Application
"""
import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title="OCR Receipt System",
    page_icon="🧾",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    st.title("🧾 OCR Receipt System")
    st.markdown("---")

    st.markdown("""
    ## 프로젝트 초기 설정

    팀원들이 각자 기능을 추가할 수 있는 기본 구조를 준비

    ### 📁 프로젝트 구조
    - `pages/` - Streamlit 멀티페이지 앱을 위한 페이지 디렉토리
    - `utils/` - 공통 유틸리티 함수
    - `data/` - 데이터 파일 저장

    ### 🚀 시작하기
    1. 가상환경 생성: `conda env create -f environment.yml`
    2. 가상환경 활성화: `conda activate ocr-receipt`
    3. 앱 실행: `streamlit run app.py`

    ### 💡 다음 단계
    - 각 팀원은 `pages/` 폴더에 새로운 페이지 추가
    - 공통 함수는 `utils/` 폴더에 추가
    - 필요한 라이브러리는 `requirements.txt`에 추가
    """)

    # 사이드바
    with st.sidebar:
        st.header("📌 개발 가이드")
        st.markdown("""
        **페이지 추가 방법:**
        1. `pages/` 폴더에 `1_페이지명.py` 형식으로 파일 생성
        2. 숫자는 메뉴 순서를 결정
        3. Streamlit이 자동으로 사이드바에 추가

        **예시:**
        - `pages/1_Upload.py`
        - `pages/2_Process.py`
        - `pages/3_Results.py`
        """)

if __name__ == "__main__":
    main()
