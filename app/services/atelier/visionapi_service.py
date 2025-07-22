from openai import OpenAI
import base64

client = OpenAI(api_key='OPENAI_API_KEY')

def analyze_image(image_path):
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "이 이미지의 내용을 상세히 묘사해줘."},
                    {"type": "image_url", "image_url": f"data:image/jpeg;base64,{encoded_image}"}
                ],
            }
        ],
        max_tokens=300,
    )

    description = response.choices[0].message.content
    return description
