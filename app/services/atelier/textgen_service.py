import os
from openai import OpenAI
from app.schemas.atelier_schema import TextGenerationRequest, TextResultDto
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_text_from_gpt(request: TextGenerationRequest) -> TextResultDto:
    prompt = f"다음 입력을 {request.style} 스타일로 감성적인 글로 만들어줘:\n\n{request.inputText}"

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024,
        temperature=0.9
    )

    generated = response.choices[0].message.content.strip()

    return TextResultDto(
        title=generated[:30].replace("\n", ""),
        content=generated,
        style=request.style,
        memoryType=request.memoryType,
        collectionId=request.collectionId,
        memoryOrder=request.memoryOrder
    )