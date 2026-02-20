# =============================================================================
# config.py - 설정 관리
# =============================================================================
# 담당: 공통 (전체 팀)
# 설명: 환경변수 및 설정값 로딩
#       - .env 파일에서 Supabase URL, Key 등 로드
#       - 경로, 상수 등 공통 설정
# =============================================================================

import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# =============================================================================
# Supabase 설정
# =============================================================================
# .env 파일에 다음 값들을 설정해야 합니다:
# SUPABASE_URL=https://your-project.supabase.co
# SUPABASE_KEY=your-anon-key
# =============================================================================

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "OcrReceipts")


def check_env():
    """
    환경변수가 제대로 설정되었는지 확인

    Returns:
        bool: 설정 완료 여부
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("⚠️  .env 파일에 SUPABASE_URL, SUPABASE_KEY를 설정하세요.")
        return False
    return True