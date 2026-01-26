# OCR Receipt System

AI+ 팀 프로젝트 협업 공간

## 📋 프로젝트 개요
영수증 이미지에서 텍스트를 추출하고 분석하는 OCR 기반 시스템

## 🚀 환경 설정

### 1. Anaconda 가상환경 생성
```bash
conda env create -f environment.yml
```

### 2. 가상환경 활성화
```bash
conda activate ocr-receipt
```

### 3. 애플리케이션 실행
```bash
streamlit run app.py
```

## 📁 프로젝트 구조
```
OCR-Receipt-System/
├── app.py              # 메인 애플리케이션
├── pages/              # 멀티페이지 폴더 (팀원들이 페이지 추가)
│   └── .gitkeep
├── utils/              # 공통 유틸리티 함수
│   └── .gitkeep
├── data/               # 데이터 파일 저장
│   └── .gitkeep
├── requirements.txt    # Python 패키지 목록
├── environment.yml     # Conda 환경 설정
└── README.md
```

## 👥 팀원 작업 가이드

### 새 페이지 추가하기
1. `pages/` 폴더에 `숫자_페이지명.py` 형식으로 파일 생성
   - 예: `1_Upload.py`, `2_Process.py`, `3_Results.py`
2. 숫자는 메뉴에 표시되는 순서를 결정
3. Streamlit이 자동으로 사이드바에 메뉴 추가

**페이지 파일 예시:**
```python
import streamlit as st

st.title("페이지 제목")
st.write("내용 작성")
```

### 유틸리티 함수 추가하기
1. `utils/` 폴더에 기능별 파일 생성
   - 예: `image_utils.py`, `ocr_utils.py`, `file_utils.py`
2. 다른 파일에서 import하여 사용

### 라이브러리 추가하기
1. `requirements.txt` 파일에 필요한 패키지 추가
2. 환경 업데이트:
```bash
pip install -r requirements.txt
```

## 🔧 기술 스택
- **Python**: 3.10.19
- **Framework**: Streamlit
- **환경관리**: Anaconda

## 📝 개발 규칙
1. 각자 담당한 기능을 독립적으로 개발
2. 공통으로 사용할 함수는 `utils/`에 작성
3. 새로운 라이브러리가 필요하면 `requirements.txt`에 추가
4. 커밋 전에 `streamlit run app.py`로 정상 작동 확인

## 🎯 다음 단계
- [ ] OCR 엔진 선택 및 통합
- [ ] 이미지 업로드 기능 구현
- [ ] 텍스트 추출 기능 구현
- [ ] 결과 시각화 및 내보내기
- [ ] 데이터 구조화 및 분석
.
