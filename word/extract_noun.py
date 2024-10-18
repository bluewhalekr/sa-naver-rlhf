from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv
import time
import json
import re
import pandas as pd
import os

# Load environment variables
load_dotenv()

# Load the CSV file
file_path = 'cleaned_unique_words.csv'
output_dir = '/ext/Dataset/naver/word2'
df = pd.read_csv(file_path)

# Azure OpenAI settings
llm = AzureChatOpenAI(
    openai_api_version="2024-07-01-preview",
    deployment_name="gpt-4o-mini",
)

# 모든 행 반복
for index, row in df.iterrows():
    word = row['Word']
    category = row['Category']
    
    # Generate a prompt for the current word
    text = f"""
    한글 단어 '{word}'와 관련성을 단계별로 나열해 주세요. 각 단계는 다음과 같이 정의됩니다:

    1단계: 가장 관련이 많은 단어 리스트
    2단계: 의미적으로 중간정도 관련이 있는 단어 리스트
    3단계: 의미적으로 관련이 없는 단어 리스트
    
    단어가 의미적으로 관련이 있어야 합니다.

    정치적인 단어나 삶과 죽음 등과 같은 추상적인 단어는 제외해주세요. 대신 일상생활에서 자주 사용되는 단어들을 고려해주세요.

    각 단계에 해당하는 단어를 dictionary 형식으로 반환해주세요. 예: {{ 'query': '배', 1: ['과일', '사과', '바나나'], 2: ['바다', '자동차', '신체'], 3: ['컴퓨터', '노트북', '부모님'] }}
    """
    
    print(f"Processing word: {word} from category: {category}")
    
    # Invoke the model
    start = time.time()
    response = llm.invoke(text)
    elapsed_time = time.time() - start
    print(f"Generated in %.2fs" % elapsed_time)
    
    # Process the response
    result = response.content
    
    # Extract the JSON content using regex
    match = re.search(r'\{.*\}', result, re.DOTALL)
    if match:
        json_string = match.group()
        
        # Replace single quotes with double quotes and handle numeric keys
        json_string = json_string.replace("'", '"')
        json_string = re.sub(r'(\d+):', r'"\1":', json_string)
        
        try:
            # Convert the JSON string to a dictionary
            result_dict = json.loads(json_string)
            
            # Save the result to a JSON file named after the index
            file_name = os.path.join(output_dir, f"{index}.json")  # Use index as the filename
            with open(file_name, 'w', encoding='utf-8') as f:
                json.dump(result_dict, f, ensure_ascii=False, indent=4)
            print(f"Results saved for index {index} in {file_name}")
        
        except json.JSONDecodeError as e:
            print(f"JSON parsing error for {word}: {e}")
    else:
        print(f"No valid JSON found for {word}")