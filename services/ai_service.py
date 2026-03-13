#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# =============================================================================
# ai_service.py - AI 분석 서비스
# =============================================================================
# 담당: AI
# 설명: OCR 추출 텍스트를 LLM으로 분석하여 구조화
#       - LLM API 호출 (OpenAI / Anthropic 등)
#       - 비정형 텍스트 → 정형 데이터 변환
#       - 카테고리 자동 분류
# =============================================================================


# In[1]:


get_ipython().system('pip install google-generativeai')


# In[2]:


# 분석 데이터 로드
import json

with open("../dummy data/dummy_receipts_full_format.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print(data)


# In[6]:


# Gemini 연결
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-2.5-flash")


# In[7]:


# 프롬프트 생성

prompt = f"""
다음은 사용자의 소비 데이터이다.

{json.dumps(data, ensure_ascii=False, indent=2)}

다음 내용을 분석해라.

1. 전체 소비 패턴
2. 과소비 카테고리
3. 월별 소비 변화
4. 절약을 위한 조언
"""


# In[8]:


# google Geminai 분석 실행

response = model.generate_content(prompt)

print(response.text)


# In[ ]:




