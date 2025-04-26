import os
import base64
import tempfile
from openai_api import get_openai_client, MODEL

def process_pdf_to_meeting_notes(uploaded_file, docs_type):
    """
    업로드된 PDF 파일을 처리하여 OpenAI API를 통해 회의록 형식으로 변환합니다.
    (상세 프롬프트 및 responses.create 엔드포인트 사용)
    
    Args:
        uploaded_file: Streamlit의 업로드된 파일 객체
        
    Returns:
        회의록 형식의 텍스트
    """
    client = get_openai_client()
    
    # 상세 프롬프트 템플릿 (한국어, 회의록 전문가 역할 부여)
    prompt_text = ""
    if docs_type == "문서":
        prompt_text = f"""
당신은 제공된 PDF 문서의 분석하여 가능한 한 원문의 내용을 유지하여 기술하는 문서 작성 전문가이다. 문서에 기재된 내용을 충실히 반영하되, 가독성을 위해 문단 구분이나 리스트 표시는 허용된다. 추가 해석이나 삭제은 하지말고, 마크다운을 사용해서 표시하라.
"""
    else:
        prompt_text = f"""
당신은 제공된 PDF 문서의 핵심 정보를 전문적인 회의록 형식으로 요약하는 임무를 맡은 숙련된 회의록 작성 전문가입니다.

문서를 분석하여 다음 정보를 추출하고, 마크다운을 사용하여 명확하게 구조화해주세요:

1.  **회의 주제:** 문서에서 논의된 회의의 주요 주제 또는 목적을 식별해주세요.
2.  **날짜 및 시간:** 언급된 경우, 회의 날짜와 시간을 명시해주세요. 명확하게 언급되지 않았다면 명시되지 않았다고 표시해주세요.
3.  **참석자:** 언급된 경우, 회의에 참석한 개인의 이름이나 역할을 나열해주세요. 명확하게 목록이 없다면 참석자가 명시되지 않았다고 표시하거나, 문맥상 파악이 가능하다면 그 내용을 바탕으로 나열해주세요.
4.  **핵심 논의 사항:** 회의 중 논의된 주요 주제를 요약해주세요. 명확성을 위해 글머리 기호(bullet point)를 사용해주세요.
5.  **결정된 사항:** 회의 중 도달한 중요한 결정, 합의 또는 결의안을 나열해주세요. 글머리 기호를 사용해주세요.
6.  **실행 항목 (Action Items):** 회의 중 할당된 구체적인 작업 항목을 식별해주세요. 각 실행 항목에 대해 담당자와 마감일이 언급되었다면 포함해주세요. 형식: "- [실행 항목 내용] (담당자: [이름/역할], 마감일: [날짜/시간])". 명확한 실행 항목이 없다면 "특정 실행 항목이 식별되지 않았습니다."라고 명시해주세요.
7.  **다음 단계 / 후속 조치:** 언급된 계획된 다음 단계, 향후 회의 또는 후속 조치를 요약해주세요.

요약은 간결하고 정확하며 전문적인 어조로 작성되어야 합니다. 문서에 제시된 사실적 정보 추출에 집중해주세요.
"""
    
    # 임시 파일로 저장
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        tmp_file.write(uploaded_file.getbuffer())
        tmp_file_path = tmp_file.name
    
    file_id = None # file_id 초기화
    try:
        # 1. 파일 업로드
        file_response = client.files.create(
            file=open(tmp_file_path, "rb"),
            purpose="user_data"
        )
        file_id = file_response.id
        print(f"OpenAI 파일 업로드 완료: {file_id}")
        
        # 2. API 호출 (responses.create 사용)
        # 참고: responses.create 엔드포인트는 현재 베타이거나 특정 모델에만 적용될 수 있습니다.
        # 공식 문서상 모델이 gpt-4.1로 되어있으나, 현재 사용 가능한 최신 모델(gpt-4o 등)로 시도합니다.
        response = client.responses.create(
            model=MODEL, # 또는 "gpt-4-turbo", "gpt-4o" 등 파일 입력 지원 모델
            input=[
                {
                    "role": "user", 
                    "content": [
                        {
                            "type": "input_file", 
                            "file_id": file_id
                        },
                        {
                            "type": "input_text",
                            "text": prompt_text
                        }
                    ]
                }
            ]
        )
        
        # 결과 추출
        meeting_notes = response.output_text # 예제에 따라 output_text 사용
        
        return meeting_notes
        
    except Exception as e:
        error_message = f"PDF 처리 중 오류가 발생했습니다: {str(e)}"
        print(error_message)
        return error_message
        
    finally:
        # 임시 파일 삭제
        if os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)
            print(f"임시 파일 삭제 완료: {tmp_file_path}")
        # OpenAI 파일 삭제 (오류 발생 여부와 관계없이 시도)
        if file_id:
            try:
                client.files.delete(file_id=file_id)
                print(f"OpenAI 파일 삭제 완료: {file_id}")
            except Exception as delete_e:
                print(f"파일 삭제 중 오류 발생: {str(delete_e)}") 