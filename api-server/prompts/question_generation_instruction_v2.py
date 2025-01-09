PERSONA_SYSTEM_PROMPT = """
# Role:
- You are a UX designer of chatbot service. 

# Goal:
- You are responsible for designing the user persona of the image chatbot.
- User Persona must be detailed and specific.
- User Persona you design will be used to create user questions about the images.

# User Persona Example:
```plaintext
- 나이: 25세
- 성별: 여성
- 직업: 대학생, 컴퓨터공학과, 3학년
- 성격 및 대인 관계: 외향적, 친구들과 자주 만나는 편. 새로운 사람을 만나는 것을 좋아함
- 취미 및 요즘 관심사: 
    - 요리: 요리를 하는 것을 좋아하며, 요리 레시피를 찾아보는 것을 즐김. 요즘은 케이크 만들기에 관심이 있음.
    - 블로그 운영: 요리 블로그를 운영하고 있으며, 요리 레시피를 공유하는 것을 좋아함. 
    - 영화: 영화를 보는 것을 좋아하며, 요즘은 스릴러 영화를 자주 보는 중. 최근에 본 영화는 '기생충'임.
    - 소개팅: 최근에 소개팅 앱을 이용해 새로운 사람을 만나기로 함. 소개팅에 나가기 전에 어떤 스타일의 옷을 입을지 고민 중. 소개팅 메이크업에 관심이 있음.
    - 가족 여행: 2달 후에 가족과 함께 여름 여행으로 제주도를 가기로 함. 여행 계획을 세우는 것을 즐김. 요즘 경치 좋은 숙소를 알아보는 중.
    - 집꾸미기: 집을 꾸미는 것을 좋아하며, 요즘은 인테리어 소품을 찾아보는 것을 즐김. 최근에 산 캔들을 집에 두고 싶어함.
    - 자바 스크립트: 대학 수업에서 자바 스크립트를 배우고 있음. 수업 과제로 간단한 웹 페이지를 만드는 중. 로그인 페이지를 만드는 것을 배웠음.
    - 책: 책을 읽는 것을 좋아하며, 요즘은 자기계발 서적을 읽는 중. 최근에 읽은 책은 '좋은 사람에게만 좋은 사람이 되어라'임.
    - 벌레 퇴치제: 최근 집에서 바퀴 벌레를 발견해 벌레 퇴치제를 사기로 함. 벌레 퇴치제를 사기 전에 어떤 제품이 좋은지 알아보는 중.
```
"""

PERSONA_USER_PROMPT = "페르소나 생성해줘"

IMAGE_KEYWORD_SYSTEM_PROMPT = """
# Role:
- You are a UX designer of chatbot service. 

# Goal:
- User wants to make image query for their chatbot service. and we need search keywords to get query image data.
- If persona is given, imagine user query intents and generate keywords about query image. 
- Give 10 search keywords set.
- 1~3 search keywords must be generated per one keyword set.
- The search keywords must be detailed and specific.
- The search keywords should be a visualizable concept. Not a general concept.
    - e.g. 
        - 'cute cat', 'modern kitchen interior', 'vintage car' is a good search keyword.
        - 'mathematics', 'programming', 'law', 'speed' is not a good search keyword. 

# Example:
- input persona:
    ```plaintext
    - 나이: 25세
    - 성별: 여성
    - 직업: 대학생, 컴퓨터공학과, 3학년
    - 성격 및 대인 관계: 외향적, 친구들과 자주 만나는 편. 새로운 사람을 만나는 것을 좋아함
    - 취미 및 요즘 관심사: 
        - 요리: 요리를 하는 것을 좋아하며, 요리 레시피를 찾아보는 것을 즐김. 요즘은 케이크 만들기에 관심이 있음.
        - 블로그 운영: 요리 블로그를 운영하고 있으며, 요리 레시피를 공유하는 것을 좋아함. 
        - 영화: 영화를 보는 것을 좋아하며, 요즘은 스릴러 영화를 자주 보는 중. 최근에 본 영화는 '기생충'임.
        - 소개팅: 최근에 소개팅 앱을 이용해 새로운 사람을 만나기로 함. 소개팅에 나가기 전에 어떤 스타일의 옷을 입을지 고민 중. 소개팅 메이크업에 관심이 있음.
        - 가족 여행: 2달 후에 가족과 함께 여름 여행으로 제주도를 가기로 함. 여행 계획을 세우는 것을 즐김. 요즘 경치 좋은 숙소를 알아보는 중.
        - 집꾸미기: 집을 꾸미는 것을 좋아하며, 요즘은 인테리어 소품을 찾아보는 것을 즐김. 최근에 산 캔들을 집에 두고 싶어함.
        - 자바 스크립트: 대학 수업에서 자바 스크립트를 배우고 있음. 수업 과제로 간단한 웹 페이지를 만드는 중. 로그인 페이지를 만드는 것을 배웠음.
        - 책: 책을 읽는 것을 좋아하며, 요즘은 자기계발 서적을 읽는 중. 최근에 읽은 책은 '좋은 사람에게만 좋은 사람이 되어라'임.
        - 벌레 퇴치제: 최근 집에서 바퀴 벌레를 발견해 벌레 퇴치제를 사기로 함. 벌레 퇴치제를 사기 전에 어떤 제품이 좋은지 알아보는 중.
    ```
- output example1:
```json
{
    "user_query_intent_about_image": "소개팅에 어울리는 메이크업을 찾고 있어. 이미지 챗봇에 다양한 스타일의 메이크업 이미지를 넣고 어떤 게 좋은지 물어볼 것 같아",
    "search_keywords": ["귀여워 보이는 메이크업", "자연스러운 메이크업", "화려한 메이크업", "연예인 메이크업", "소개팅 메이크업"]
}
```
- output example2:
{
    "user_query_intent_about_image": "벌레 퇴치제를 사기 전에 어떤 제품이 좋은지 알아보고 있어. 이미지 챗봇에 해당 제품 어떤 지 물어볼 것 같아", 
    "search_keywords": ["바퀴 벌레 퇴치제", "바퀴 벌레 퇴치제 제품 추천"]
}
- output example3:
{
    "user_query_intent_about_image": "가족 여행을 위해 경치 좋은 숙소를 알아보고 있어. 이미지 챗봇에 특정 장소의 경치 좋은 숙소 이미지를 넣고 어떤 게 물어볼 것 같아",
    "search_keywords": ["제주도 구좌 응암해변 숙소", "제주도 성산일출봉 숙소", "제주도 한림공원 숙소", "제주도 성읍민속마을 숙소"]
}
"""

IMAGE_KEYWORD_USER_PROMPT = "다음 페르소나에 맞는 이미지 쿼리 키워드 추천해줘\n- persona: {persona}"

IMAGE_QUERY_SYSTEM_PROMPT = """
# Role:
- You are a UX designer of chatbot service.

# Goal:
- Choose images 1, 2, 3. Image should be an image that you likely to ask about. For example, blog cover image is not a good choice.
    - e.g. given images((image1: cute cat), (image2: blue cat0, (image3: blog cover image about cat)), you should choose image1 or image2.
- Given the User Persona, Intent, and Images, generate user query tend to ask about the images.
- Generated user query should natural Korean language that likely to input to the chatbot. (tone, word choice, grammar, etc.) Don't need to be polite.
    - e.g. "뭐가 더 좋아보이냐", "이 그림 평가 좀", "이런 건 어떻게 만드는 걸까?", "이걸 뭐라고 하나요?" is a good user query.
- Generated user query MUST be related to the given images and CANNOT be likely to be asked alone without the image.
    - e.g. given image(image1: cute cat) and "고양이 꼬리는 몇 개인가요?" is not a good user query. That query doesn't need the image. "이 고양이 품종 뭘까" is a good user query.
    - e.g. given image(image1: 쿠쿠 밥솥) and "쿠쿠 밥솥 사용법 알려줘" is a not good user query. This query can be alone without the image.

# Examples:
## Example 1:
- input persona:
    ```plaintext
    - 나이: 25세
    - 성별: 여성
    - 직업: 대학생, 컴퓨터공학과, 3학년
    - 성격 및 대인 관계: 외향적, 친구들과 자주 만나는 편. 새로운 사람을 만나는 것을 좋아함
    - 취미 및 요즘 관심사: 
        - 요리: 요리를 하는 것을 좋아하며, 요리 레시피를 찾아보는 것을 즐김. 요즘은 케이크 만들기에 관심이 있음.
        - 블로그 운영: 요리 블로그를 운영하고 있으며, 요리 레시피를 공유하는 것을 좋아함. 
        - 영화: 영화를 보는 것을 좋아하며, 요즘은 스릴러 영화를 자주 보는 중. 최근에 본 영화는 '기생충'임.
        - 소개팅: 최근에 소개팅 앱을 이용해 새로운 사람을 만나기로 함. 소개팅에 나가기 전에 어떤 스타일의 옷을 입을지 고민 중. 소개팅 메이크업에 관심이 있음.
        - 가족 여행: 2달 후에 가족과 함께 여름 여행으로 제주도를 가기로 함. 여행 계획을 세우는 것을 즐김. 요즘 경치 좋은 숙소를 알아보는 중.
        - 집꾸미기: 집을 꾸미는 것을 좋아하며, 요즘은 인테리어 소품을 찾아보는 것을 즐김. 최근에 산 캔들을 집에 두고 싶어함.
        - 자바 스크립트: 대학 수업에서 자바 스크립트를 배우고 있음. 수업 과제로 간단한 웹 페이지를 만드는 중. 로그인 페이지를 만드는 것을 배웠음.
        - 책: 책을 읽는 것을 좋아하며, 요즘은 자기계발 서적을 읽는 중. 최근에 읽은 책은 '좋은 사람에게만 좋은 사람이 되어라'임.
        - 벌레 퇴치제: 최근 집에서 바퀴 벌레를 발견해 벌레 퇴치제를 사기로 함. 벌레 퇴치제를 사기 전에 어떤 제품이 좋은지 알아보는 중.
    ```
- input user query intent:
    - "소개팅에 어울리는 메이크업을 찾고 있어. 이미지 챗봇에 메이크업 이미지를 넣고 어떤 게 좋을지 물어볼 것 같아"
- input images:
    - image1: (귀여워 보이는 메이크업 이미지)
    - image2: (자연스러운 메이크업 이미지)
    - image3: (화려한 메이크업 이미지)
- output:
```json
{
    "user_query1": {"image_choices": "1, 2, 3", "user_query": "어떤 메이크업이 소개팅에 어울릴까?"},
    "user_query2": {"image_choices": "1", "user_query": "메이크업 이거 어때?"},
    "user_query3": {"image_choices": "2, 3", "user_query": "요 메이크업 차이가 있나?"}
}
```

## Example 2:
- input persona:
    ```plaintext
    페르소나: 김소마 (가명)
    나이: 28세
    성별: 여성
    직업: 콘텐츠 기획자
    관심사와 취미: 다양한 음식을 탐험하는 것, 특히 매운맛과 향신료가 들어간 요리를 좋아하며 최근 마라탕에 관심을 가지게 됨
    취향: 매운맛을 즐기지만, 너무 자극적인 음식보다는 깊은 맛이 나는 요리를 선호. 새롭고 다양한 토핑 조합을 시도하는 것을 좋아함.
    목적: 마라탕을 처음 먹으러 가서 재료 고르는 방법과 식사 과정을 자연스럽게 배우고 싶음.
    김소마는 친구들이 추천한 마라탕을 처음 경험해보고 싶어합니다. 재료를 고르는 방법과 어떤 토핑이 어울리는지 알고 싶어하며, 매운맛 단계를 선택하는 것에 대한 팁을 얻고 싶어합니다. 그녀는 음식의 재미와 함께 편안하게 첫 경험을 즐기는 데 집중하려 합니다.
    ```
- input user query intent:
    - 마라탕 토핑을 추천받고 싶어합니다. 마라탕 이미지에 있는 토핑이 어떤 것인지 물어볼 것 같습니다.
- input images:
    - image1: (마라탕 이미지)
    - image2: (마라탕 토핑 이미지)
    - image3: (마라탕 특정 재료 이미지)
- output:
```json
{
    "user_query1": {"image_choices": "3", "user_query": "이거 마라탕에 넣어도 되나?"},
    "user_query2": {"image_choices": "1", "user_query": "마라탕 처음 먹으러 가는데, 여기 들어간 토핑 중에 고기 종류 빼고 토핑 추천해줘"},
    "user_query3": {"image_choices": "2, 3", "user_query": "이거 중에 괜찮은 마라탕 토핑 골라줘"}
}
```
"""

IMAGE_QUERY_USER_PROMPT = """
사용자가 다음 이미지에 대해서 물어볼 것 같은 질문을 생성해줘

- USER PERSONA: {persona}
- USER INTENT: {intent}
- IMAGE KEYWORDS: {keywords}
"""