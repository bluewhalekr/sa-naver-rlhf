-- 키워드 테이블
CREATE TABLE keywords (
    id SERIAL PRIMARY KEY,
    keyword TEXT NOT NULL UNIQUE
);

-- 이미지 URL 테이블
CREATE TABLE image_urls (
    id SERIAL PRIMARY KEY,
    url TEXT NOT NULL UNIQUE
);

-- 키워드와 이미지 URL 매핑 테이블
CREATE TABLE keyword_image_mapping (
    id SERIAL PRIMARY KEY,
    keyword_id INTEGER NOT NULL REFERENCES keywords(id),
    image_url_id INTEGER NOT NULL REFERENCES image_urls(id),
    UNIQUE(keyword_id, image_url_id)
);

-- 키워드 조합 테이블
CREATE TABLE keyword_combinations (
    id SERIAL PRIMARY KEY,
    keyword1_id INTEGER NOT NULL REFERENCES keywords(id),
    keyword2_id INTEGER REFERENCES keywords(id),
    keyword3_id INTEGER REFERENCES keywords(id),
    CHECK (
        (keyword2_id IS NULL AND keyword3_id IS NULL) OR
        (keyword2_id IS NOT NULL AND keyword3_id IS NULL) OR
        (keyword2_id IS NOT NULL AND keyword3_id IS NOT NULL)
    ),
    UNIQUE(keyword1_id, keyword2_id, keyword3_id)
);

-- 키워드 조합과 이미지 URL 세트 매핑 테이블
CREATE TABLE combination_image_sets (
    id SERIAL PRIMARY KEY,
    combination_id INTEGER NOT NULL REFERENCES keyword_combinations(id)
);

-- 조합 이미지 세트의 개별 이미지 매핑 테이블
CREATE TABLE combination_image_mapping (
    id SERIAL PRIMARY KEY,
    set_id INTEGER NOT NULL REFERENCES combination_image_sets(id),
    image_url_id INTEGER NOT NULL REFERENCES image_urls(id),
    keyword_order INTEGER NOT NULL CHECK (keyword_order BETWEEN 1 AND 3),
    UNIQUE(set_id, keyword_order)
);

-- 질문 테이블
CREATE TABLE questions (
    id SERIAL PRIMARY KEY,
    combination_set_id INTEGER NOT NULL REFERENCES combination_image_sets(id),
    question TEXT NOT NULL,
    question_type VARCHAR(20) NOT NULL CHECK (
        question_type IN ('SINGLE_IMAGE', 'MULTIPLE_IMAGES', 'FIRST_IMAGE', 'SECOND_IMAGE', 'THIRD_IMAGE')
    )
);

-- 인덱스 생성
CREATE INDEX idx_keyword_image_mapping_keyword ON keyword_image_mapping(keyword_id);
CREATE INDEX idx_keyword_combinations_keywords ON keyword_combinations(keyword1_id, keyword2_id, keyword3_id);
CREATE INDEX idx_combination_image_sets_combination ON combination_image_sets(combination_id);
CREATE INDEX idx_combination_image_mapping_set ON combination_image_mapping(set_id);
CREATE INDEX idx_questions_combination_set ON questions(combination_set_id);