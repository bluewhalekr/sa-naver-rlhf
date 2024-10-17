import fasttext
import pandas as pd
import numpy as np

# FastText 모델 다운로드 및 로드
model_path = '/ext/model.bin'
model = fasttext.load_model(model_path)

# CSV 파일 로드
file_path = '/ext/Dataset/naver/unique_words_.csv'
unique_words_df = pd.read_csv(file_path)

# 카테고리별 단어 목록 생성
categories = unique_words_df['Category'].unique()

# 유사도 계산 함수
def cosine_similarity(vec1, vec2):
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm_a = sum(a ** 2 for a in vec1) ** 0.5
    norm_b = sum(b ** 2 for b in vec2) ** 0.5
    return dot_product / (norm_a * norm_b)

# 각 단어의 가장 유사한 단어와 가장 비유사한 단어 찾기
for category in categories:
    words = unique_words_df[unique_words_df['Category'] == category]['Word'].tolist()
    print(f"\n카테고리: {category}")
    
    for word in words:
        try:
            vec1 = model[word]
            
            # 벡터가 유효한지 체크
            if np.all(vec1 == 0):
                print(f"'{word}'의 벡터가 유효하지 않습니다.")
                continue

            similarities = []

            for other_word in words:
                if word != other_word:
                    vec2 = model[other_word]
                    
                    # 유효한 벡터만 사용
                    if np.all(vec2 == 0):
                        print(f"'{other_word}'의 벡터가 유효하지 않아 건너뜁니다.")
                        continue
                    
                    # NaN 발생 시 벡터 상태 출력
                    similarity = cosine_similarity(vec1, vec2)
                    if np.isnan(similarity):
                        print(f"NaN 발생: '{word}'과 '{other_word}'의 유사도")
                        print(f"'{word}' 벡터: {vec1}")
                        print(f"'{other_word}' 벡터: {vec2}")
                    else:
                        similarities.append((other_word, similarity))

            if similarities:
                similarities.sort(key=lambda x: x[1])
                most_similar = similarities[-1]
                least_similar = similarities[0]

                print(f"'{word}'과 가장 유사한 단어: '{most_similar[0]}', 유사도: {most_similar[1]}")
                print(f"'{word}'과 가장 비유사한 단어: '{least_similar[0]}', 유사도: {least_similar[1]}")
            else:
                print(f"'{word}'에 대해 유효한 유사 단어가 없습니다.")

        except Exception as e:
            print(f"'{word}'을 처리하는 중 오류 발생: {e}")