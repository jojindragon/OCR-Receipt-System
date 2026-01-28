# OCR Receipt System

AI+ 팀 프로젝트 협업 공간

## 프로젝트 개요
영수증 이미지에서 텍스트를 추출하고 분석하는 OCR 기반 시스템

## 환경 설정

```bash
# 1. Anaconda 가상환경 생성
conda env create -f environment.yml

# 2. 가상환경 활성화
conda activate ocr-receipt

# 3. Streamlit 실행
streamlit run frontend/app.py
```

## 프로젝트 구조
```
OCR-Receipt-System/
├── frontend/               # [프론트엔드] Streamlit UI
│   ├── app.py              # 메인 앱 진입점
│   └── pages/              # 페이지 추가 시 여기에
│
├── backend/                # [백엔드] API 서버 + DB
│   ├── api.py              # API 라우트
│   ├── database.py         # DB 연결
│   └── models.py           # 데이터 모델
│
├── services/               # [OCR / AI] 핵심 서비스
│   ├── ocr_service.py      # OCR 처리
│   └── ai_service.py       # LLM 분석
│
├── utils/                  # [공통] 유틸리티
│   ├── config.py           # 설정 관리
│   └── helpers.py          # 공통 함수
│
├── data/                   # 데이터 저장소
│   └── receipts/           # 영수증 이미지
│
├── tests/                  # 테스트 (나중에 추가)
│
├── .env.example            # 환경변수 템플릿
├── .gitignore
├── environment.yml         # Conda 환경
├── requirements.txt        # 패키지 목록
└── README.md
```

## 팀원별 작업 영역

| 역할 | 작업 디렉토리 | 설명 |
|------|---------------|------|
| 프론트엔드 | `frontend/` | Streamlit UI, 페이지, 컴포넌트 |
| 백엔드 | `backend/` | API, DB, 데이터 모델 |
| OCR | `services/ocr_service.py` | OCR API 연동 및 처리 |
| AI | `services/ai_service.py` | LLM 텍스트 분석 |
| 공통 | `utils/` | 설정, 헬퍼 함수 (수정 시 협의) |

## 기술 스택
- **Python**: 3.10.19
- **UI**: Streamlit
- **환경관리**: Anaconda
