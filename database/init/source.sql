-- data/results CSV 통합 스키마
--
-- 기존 초기화 파일에서 생성되는 지역 차원 테이블
--   sidos, districts, umds: region_code.csv
--
-- 적재 전 정리 사항
--   1. 기준 연월은 YYYY-MM 형식으로 통일한다.
--   2. 관심_관광지_내국인.csv에는 완전 중복 행이 있으므로 제거 후 적재한다.
--   3. 인기관광지_네비.csv는 인기관광지_네비_전체.csv의 초기 3개월과
--      중복되므로 둘 중 하나만 적재한다.
--   4. 내비게이션 CSV 파일명에 따라 place_type, audience_type 값을 지정한다.


-- 국가 차원
CREATE TABLE IF NOT EXISTS nationalities (
    nationality_id SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '국가 ID',
    nationality_cd CHAR(3)     NULL COMMENT '외국인 국가 코드',
    nationality_nm VARCHAR(50) NOT NULL COMMENT '국가명',

    PRIMARY KEY (nationality_id),
    UNIQUE KEY uq_nationality_code (nationality_cd),
    UNIQUE KEY uq_nationality_name (nationality_nm),

    CONSTRAINT chk_nationality_cd
        CHECK (
            nationality_cd IS NULL
            OR nationality_cd REGEXP '^[0-9]{3}$'
        )
)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_unicode_ci
COMMENT = '국가 기준정보';


-- 국가별외국인방문객현황.csv
CREATE TABLE IF NOT EXISTS tourist_counts (
    base_ym       CHAR(7)      NOT NULL COMMENT '기준 연월(YYYY-MM)',
    sgg_cd        CHAR(5)      NOT NULL COMMENT '방문 시군구 코드',
    nationality_id SMALLINT UNSIGNED NOT NULL COMMENT '국가 ID',
    tourist_cnt   BIGINT UNSIGNED NOT NULL COMMENT '관광객 수',

    PRIMARY KEY (base_ym, sgg_cd, nationality_id),
    KEY idx_tourist_nationality (nationality_id),

    CONSTRAINT fk_tourist_nationality
        FOREIGN KEY (nationality_id) REFERENCES nationalities (nationality_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT chk_tourist_base_ym
        CHECK (base_ym REGEXP '^[0-9]{4}-(0[1-9]|1[0-2])$')
)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_unicode_ci
COMMENT = '월별 시군구·국가별 외국인 관광객 수';


-- 방문자_거주지.csv
CREATE TABLE IF NOT EXISTS visitor_residence_counts (
    base_ym          CHAR(7)     NOT NULL COMMENT '기준 연월(YYYY-MM)',
    sgg_cd           CHAR(5)     NOT NULL COMMENT '방문 시군구 코드',
    origin_region_nm VARCHAR(30) NOT NULL COMMENT '출발 시도명',
    origin_detail_nm VARCHAR(30) NOT NULL COMMENT '출발 상세지역명',
    visitor_cnt      BIGINT UNSIGNED NOT NULL COMMENT '방문자 수',

    PRIMARY KEY (
        base_ym,
        sgg_cd,
        origin_region_nm,
        origin_detail_nm
    ),
    KEY idx_residence_origin (origin_region_nm, origin_detail_nm),

    CONSTRAINT chk_residence_base_ym
        CHECK (base_ym REGEXP '^[0-9]{4}-(0[1-9]|1[0-2])$')
)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_unicode_ci
COMMENT = '월별 방문자의 출발 거주지별 방문자 수';


-- 방문자_성_연령.csv
CREATE TABLE IF NOT EXISTS visitor_demographics (
    base_ym     CHAR(7)     NOT NULL COMMENT '기준 연월(YYYY-MM)',
    sgg_cd      CHAR(5)     NOT NULL COMMENT '방문 시군구 코드',
    age_group   VARCHAR(20) NOT NULL COMMENT '연령대',
    gender      ENUM('남성', '여성') NOT NULL COMMENT '성별',
    visitor_cnt BIGINT UNSIGNED NOT NULL COMMENT '방문자 수',

    PRIMARY KEY (base_ym, sgg_cd, age_group, gender),
    KEY idx_demographics_group (age_group, gender),

    CONSTRAINT chk_demographics_base_ym
        CHECK (base_ym REGEXP '^[0-9]{4}-(0[1-9]|1[0-2])$')
)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_unicode_ci
COMMENT = '월별 성별·연령대별 방문자 수';


-- 국가별관광소비.csv
CREATE TABLE IF NOT EXISTS nationality_tourism_spending (
    base_ym       CHAR(7)     NOT NULL COMMENT '기준 연월(YYYY-MM)',
    sgg_cd        CHAR(5)     NOT NULL COMMENT '소비 발생 시군구 코드',
    nationality_id SMALLINT UNSIGNED NOT NULL COMMENT '국가 ID',
    spend_amt     BIGINT UNSIGNED NOT NULL COMMENT '관광소비 금액',

    PRIMARY KEY (base_ym, sgg_cd, nationality_id),
    KEY idx_nationality_spending_nationality (nationality_id),

    CONSTRAINT fk_nationality_spending_nationality
        FOREIGN KEY (nationality_id) REFERENCES nationalities (nationality_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT chk_nationality_spending_base_ym
        CHECK (base_ym REGEXP '^[0-9]{4}-(0[1-9]|1[0-2])$')
)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_unicode_ci
COMMENT = '월별 시군구·국가별 관광소비 금액';


-- 관광 대업종 차원
CREATE TABLE IF NOT EXISTS tourism_industries (
    industry_id TINYINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '관광 대업종 ID',
    industry_nm VARCHAR(50) NOT NULL COMMENT '관광 대업종명',

    PRIMARY KEY (industry_id),
    UNIQUE KEY uq_tourism_industry_name (industry_nm)
)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_unicode_ci
COMMENT = '관광 대업종 기준정보';


-- 업종별관광소비.csv
CREATE TABLE IF NOT EXISTS industry_tourism_spending (
    base_ym    CHAR(7)     NOT NULL COMMENT '기준 연월(YYYY-MM)',
    sgg_cd     CHAR(5)     NOT NULL COMMENT '소비 발생 시군구 코드',
    industry_id TINYINT UNSIGNED NOT NULL COMMENT '관광 대업종 ID',
    spend_amt  BIGINT UNSIGNED NOT NULL COMMENT '관광소비 금액',

    PRIMARY KEY (base_ym, sgg_cd, industry_id),
    KEY idx_industry_spending_industry (industry_id),

    CONSTRAINT fk_industry_spending_industry
        FOREIGN KEY (industry_id) REFERENCES tourism_industries (industry_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT chk_industry_spending_base_ym
        CHECK (base_ym REGEXP '^[0-9]{4}-(0[1-9]|1[0-2])$')
)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_unicode_ci
COMMENT = '월별 시군구·업종별 관광소비 금액';


-- 관광 세부업종 차원
CREATE TABLE IF NOT EXISTS tourism_detail_industries (
    detail_industry_id SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '관광 세부업종 ID',
    industry_id        TINYINT UNSIGNED NOT NULL COMMENT '관광 대업종 ID',
    detail_industry_nm VARCHAR(50) NOT NULL COMMENT '관광 세부업종명',

    PRIMARY KEY (detail_industry_id),
    UNIQUE KEY uq_tourism_detail_industry (industry_id, detail_industry_nm),

    CONSTRAINT fk_detail_industry_parent
        FOREIGN KEY (industry_id) REFERENCES tourism_industries (industry_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_unicode_ci
COMMENT = '관광 세부업종 기준정보';


-- 외국인_업종_국적별_관광소비_및_방문.csv 사실 테이블
CREATE TABLE IF NOT EXISTS foreign_epay_spending (
    base_ym            CHAR(7)     NOT NULL COMMENT '기준 연월(YYYY-MM)',
    sgg_cd             CHAR(5)     NOT NULL COMMENT '소비 발생 시군구 코드',
    nationality_id     SMALLINT UNSIGNED NOT NULL COMMENT '국가 ID',
    detail_industry_id SMALLINT UNSIGNED NOT NULL COMMENT '관광 세부업종 ID',
    spend_amt          BIGINT UNSIGNED NOT NULL COMMENT '간편결제 관광소비 금액(천원)',

    PRIMARY KEY (base_ym, sgg_cd, nationality_id, detail_industry_id),
    KEY idx_epay_spending_nationality (nationality_id),
    KEY idx_epay_spending_detail_industry (detail_industry_id),

    CONSTRAINT fk_epay_spending_nationality
        FOREIGN KEY (nationality_id) REFERENCES nationalities (nationality_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_epay_spending_detail_industry
        FOREIGN KEY (detail_industry_id)
        REFERENCES tourism_detail_industries (detail_industry_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT chk_epay_spending_base_ym
        CHECK (base_ym REGEXP '^[0-9]{4}-(0[1-9]|1[0-2])$')
)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_unicode_ci
COMMENT = '월별 시군구·외국인 국가·세부업종별 간편결제 관광소비 금액';


-- 유료_관광지_내국인_입장객수.csv
-- BASE_YM은 YEAR_MONTH와 같은 정보이므로 base_ym 하나만 저장한다.
CREATE TABLE IF NOT EXISTS paid_attractions (
    attraction_id SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '유료 관광지 대체키',
    sgg_cd        CHAR(5)      NOT NULL COMMENT '소재 시군구 코드',
    attraction_nm VARCHAR(100) NOT NULL COMMENT '유료 관광지명',

    PRIMARY KEY (attraction_id),
    UNIQUE KEY uq_paid_attraction_name (sgg_cd, attraction_nm),
    UNIQUE KEY uq_paid_attraction_district (sgg_cd, attraction_id),
    KEY idx_paid_attraction_name (attraction_nm)
)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_unicode_ci
COMMENT = '유료 관광지 기준정보';


CREATE TABLE IF NOT EXISTS paid_attraction_counts (
    base_ym       CHAR(7)      NOT NULL COMMENT '기준 연월(YYYY-MM)',
    sgg_cd        CHAR(5)      NOT NULL COMMENT '시군구 코드',
    attraction_id SMALLINT UNSIGNED NOT NULL COMMENT '유료 관광지 대체키',
    ranking       TINYINT UNSIGNED NOT NULL COMMENT '월별 순위',
    domestic_cnt  BIGINT UNSIGNED NOT NULL COMMENT '내국인 입장객 수',
    total_cnt     BIGINT UNSIGNED NOT NULL COMMENT '전체 입장객 수',

    PRIMARY KEY (base_ym, sgg_cd, attraction_id),
    KEY idx_paid_attraction_rank (base_ym, sgg_cd, ranking),

    CONSTRAINT fk_paid_count_attraction
        FOREIGN KEY (sgg_cd, attraction_id)
        REFERENCES paid_attractions (sgg_cd, attraction_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT chk_paid_attraction_base_ym
        CHECK (base_ym REGEXP '^[0-9]{4}-(0[1-9]|1[0-2])$'),
    CONSTRAINT chk_paid_attraction_rank
        CHECK (ranking BETWEEN 1 AND 100),
    CONSTRAINT chk_paid_attraction_count
        CHECK (domestic_cnt <= total_cnt)
)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_unicode_ci
COMMENT = '월별 유료 관광지 입장객 수';


-- 인기관광지_네비*.csv와 지역맛집_*.csv의 장소 기준정보
-- POI ID당 한 행을 저장하고, 명칭·카테고리·소재지는 최신 값을 사용한다.
-- 월별 소재 시군구 이력은 navigation_search_counts에 보존한다.
CREATE TABLE IF NOT EXISTS tourism_places (
    poi_id        CHAR(32) CHARACTER SET ascii COLLATE ascii_bin
                                NOT NULL COMMENT 'MD5 POI ID',
    source_poi_id CHAR(32) CHARACTER SET ascii COLLATE ascii_bin
                                NOT NULL COMMENT '원천 POI ID',
    sgg_cd        CHAR(5)      NOT NULL COMMENT '소재 시군구 코드',
    place_type    ENUM('관광지', '맛집') NOT NULL COMMENT '장소 구분',
    place_nm      VARCHAR(100) NOT NULL COMMENT '장소명',
    category_nm   VARCHAR(50)  NOT NULL COMMENT 'POI 카테고리명',
    latitude      DECIMAL(10, 7) NULL COMMENT '위도(WGS84)',
    longitude     DECIMAL(10, 7) NULL COMMENT '경도(WGS84)',

    PRIMARY KEY (poi_id),
    UNIQUE KEY uq_tourism_place_source (source_poi_id),
    KEY idx_tourism_place_district (sgg_cd, place_type),
    KEY idx_tourism_place_name (place_nm),

    CONSTRAINT chk_tourism_place_poi_id
        CHECK (poi_id REGEXP '^[0-9A-Fa-f]{32}$'),
    CONSTRAINT chk_tourism_place_source_poi_id
        CHECK (source_poi_id REGEXP '^[0-9A-Fa-f]{32}$'),
    CONSTRAINT chk_tourism_place_latitude
        CHECK (latitude IS NULL OR latitude BETWEEN -90 AND 90),
    CONSTRAINT chk_tourism_place_longitude
        CHECK (longitude IS NULL OR longitude BETWEEN -180 AND 180),
    CONSTRAINT chk_tourism_place_coordinates
        CHECK (
            (latitude IS NULL AND longitude IS NULL)
            OR (latitude IS NOT NULL AND longitude IS NOT NULL)
        )
)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_unicode_ci
COMMENT = '관광지·맛집 POI 기준정보와 위치 좌표';


-- 인기관광지_네비*.csv와 지역맛집_*.csv의 월별 검색 집계
-- audience_type: '전체', '외지인', '현지인'
CREATE TABLE IF NOT EXISTS navigation_search_counts (
    base_ym       CHAR(7)      NOT NULL COMMENT '기준 연월(YYYY-MM)',
    sgg_cd        CHAR(5)      NOT NULL COMMENT '검색 대상 소재 시군구 코드',
    poi_id        CHAR(32) CHARACTER SET ascii COLLATE ascii_bin
                                NOT NULL COMMENT '관광지·맛집 POI ID',
    audience_type ENUM('전체', '외지인', '현지인') NOT NULL COMMENT '방문자 구분',
    ranking       TINYINT UNSIGNED NOT NULL COMMENT '검색 순위',
    search_cnt    BIGINT UNSIGNED NOT NULL COMMENT '검색 건수',

    PRIMARY KEY (base_ym, sgg_cd, poi_id, audience_type),
    KEY idx_navigation_rank (base_ym, sgg_cd, audience_type, ranking),

    CONSTRAINT fk_navigation_place
        FOREIGN KEY (poi_id) REFERENCES tourism_places (poi_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT chk_navigation_base_ym
        CHECK (base_ym REGEXP '^[0-9]{4}-(0[1-9]|1[0-2])$'),
    CONSTRAINT chk_navigation_rank
        CHECK (ranking BETWEEN 1 AND 100)
)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_unicode_ci
COMMENT = '월별 관광지·맛집 내비게이션 검색 순위와 검색 건수';


-- 관심 관광지 CSV의 KTO 대·중·소분류 계층
CREATE TABLE IF NOT EXISTS kto_large_categories (
    large_cat_cd CHAR(3)     NOT NULL COMMENT 'KTO 대분류 코드',
    large_cat_nm VARCHAR(50) NOT NULL COMMENT 'KTO 대분류명',

    PRIMARY KEY (large_cat_cd),
    KEY idx_kto_large_category_nm (large_cat_nm)
)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_unicode_ci
COMMENT = '한국관광공사 관광 콘텐츠 대분류';


CREATE TABLE IF NOT EXISTS kto_mid_categories (
    mid_cat_cd   CHAR(5)     NOT NULL COMMENT 'KTO 중분류 코드',
    mid_cat_nm   VARCHAR(50) NOT NULL COMMENT 'KTO 중분류명',
    large_cat_cd CHAR(3)     NOT NULL COMMENT 'KTO 대분류 코드',

    PRIMARY KEY (mid_cat_cd),
    UNIQUE KEY uq_kto_mid_category_name (large_cat_cd, mid_cat_nm),
    KEY idx_kto_mid_large (large_cat_cd),

    CONSTRAINT fk_kto_mid_large
        FOREIGN KEY (large_cat_cd)
        REFERENCES kto_large_categories (large_cat_cd)
        ON UPDATE CASCADE ON DELETE RESTRICT
)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_unicode_ci
COMMENT = '한국관광공사 관광 콘텐츠 중분류';


CREATE TABLE IF NOT EXISTS kto_small_categories (
    small_cat_cd CHAR(9)     NOT NULL COMMENT 'KTO 소분류 코드',
    small_cat_nm VARCHAR(50)  NOT NULL COMMENT 'KTO 소분류명',
    mid_cat_cd   CHAR(5)     NOT NULL COMMENT 'KTO 중분류 코드',

    PRIMARY KEY (small_cat_cd),
    UNIQUE KEY uq_kto_small_category_name (mid_cat_cd, small_cat_nm),
    KEY idx_kto_small_mid (mid_cat_cd),

    CONSTRAINT fk_kto_small_mid
        FOREIGN KEY (mid_cat_cd)
        REFERENCES kto_mid_categories (mid_cat_cd)
        ON UPDATE CASCADE ON DELETE RESTRICT
)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_unicode_ci
COMMENT = '한국관광공사 관광 콘텐츠 소분류';


-- 관광 콘텐츠 대표 정보
-- content_nm은 내국인 최신 명칭을 우선 사용하며 위경도 검색 기준명으로 사용한다.
CREATE TABLE IF NOT EXISTS tourism_contents (
    content_id INT UNSIGNED NOT NULL COMMENT '관광 콘텐츠 ID',
    content_nm VARCHAR(200) NOT NULL COMMENT '좌표 검색용 대표 한글 콘텐츠명',
    latitude   DECIMAL(10, 7) NULL COMMENT '위도',
    longitude  DECIMAL(10, 7) NULL COMMENT '경도',

    PRIMARY KEY (content_id),
    KEY idx_tourism_content_name (content_nm)
)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_unicode_ci
COMMENT = '관광 콘텐츠 대표 정보 및 위치 정보';


-- 콘텐츠 언어권별 최신 명칭과 URL
CREATE TABLE IF NOT EXISTS tourism_content_localizations (
    content_id  INT UNSIGNED NOT NULL COMMENT '관광 콘텐츠 ID',
    language    ENUM('내국인', '영어권', '일본어', '중간체', '중번체')
                                NOT NULL COMMENT '언어권',
    content_nm  VARCHAR(200) NOT NULL COMMENT '해당 언어권의 최신 콘텐츠명',
    content_url VARCHAR(255) NOT NULL COMMENT '해당 언어권의 최신 콘텐츠 URL',

    PRIMARY KEY (content_id, language),

    CONSTRAINT fk_content_localization_content
        FOREIGN KEY (content_id) REFERENCES tourism_contents (content_id)
        ON UPDATE CASCADE ON DELETE CASCADE
)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_unicode_ci
COMMENT = '관광 콘텐츠 언어권별 최신 명칭과 URL';


-- 관심_관광지_내국인/영어권/일어권/중간체/중번체.csv 통합 사실 테이블
-- 구군과 소분류는 기간 중 변경 사례가 있으므로 월별 사실 값으로 보존한다.
CREATE TABLE IF NOT EXISTS tourism_interest_counts (
    base_ym      CHAR(7)      NOT NULL COMMENT '기준 연월(YYYY-MM)',
    sgg_cd       CHAR(5)      NOT NULL COMMENT '시군구 코드',
    content_id   INT UNSIGNED NOT NULL COMMENT '관광 콘텐츠 ID',
    language     ENUM('내국인', '영어권', '일본어', '중간체', '중번체')
                                 NOT NULL COMMENT '언어권',
    small_cat_cd CHAR(9)      NOT NULL COMMENT 'KTO 소분류 코드',
    visitor_cnt  BIGINT UNSIGNED NOT NULL COMMENT '콘텐츠 방문자 수',

    PRIMARY KEY (base_ym, sgg_cd, content_id, language),
    KEY idx_interest_content (content_id, language),
    KEY idx_interest_category (small_cat_cd),

    CONSTRAINT fk_interest_content_localization
        FOREIGN KEY (content_id, language)
        REFERENCES tourism_content_localizations (content_id, language)
        ON UPDATE CASCADE ON DELETE RESTRICT,

    CONSTRAINT fk_interest_category
        FOREIGN KEY (small_cat_cd) REFERENCES kto_small_categories (small_cat_cd)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT chk_interest_base_ym
        CHECK (base_ym REGEXP '^[0-9]{4}-(0[1-9]|1[0-2])$')
)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_unicode_ci
COMMENT = '월별 언어권별 관심 관광 콘텐츠 방문자 수';


-- MICE관련행사정보.csv
-- 같은 event_id가 여러 조회 월에 나타나므로 event_id와 base_ym을 복합키로 사용한다.
CREATE TABLE IF NOT EXISTS mice_events (
    event_id       INT UNSIGNED NOT NULL COMMENT '행사 ID',
    base_ym        CHAR(7)      NOT NULL COMMENT '조회 기준 연월(YYYY-MM)',
    event_type_cd  TINYINT UNSIGNED NOT NULL COMMENT '행사 유형 코드',
    event_type_nm  VARCHAR(20)  NOT NULL COMMENT '행사 유형명',
    event_nm       VARCHAR(200) NOT NULL COMMENT '행사명',
    place_nm       VARCHAR(500) NULL COMMENT '행사 장소',
    start_date     DATE         NOT NULL COMMENT '행사 시작일',
    end_date       DATE         NOT NULL COMMENT '행사 종료일',
    event_time     VARCHAR(255) NULL COMMENT '행사 시간 설명',
    attachment_id  CHAR(64) CHARACTER SET ascii COLLATE ascii_bin
                                 NULL COMMENT '첨부파일 ID',
    file_sn        CHAR(32) CHARACTER SET ascii COLLATE ascii_bin
                                 NULL COMMENT '파일 번호',

    PRIMARY KEY (event_id, base_ym),
    KEY idx_mice_period (start_date, end_date),
    KEY idx_mice_type (event_type_cd),

    CONSTRAINT chk_mice_base_ym
        CHECK (base_ym REGEXP '^[0-9]{4}-(0[1-9]|1[0-2])$'),
    CONSTRAINT chk_mice_event_type
        CHECK (event_type_cd BETWEEN 1 AND 4),
    CONSTRAINT chk_mice_period
        CHECK (start_date <= end_date)
)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_unicode_ci
COMMENT = '부산 MICE 행사 정보';


ALTER TABLE tourist_counts
    ADD CONSTRAINT fk_tourist_region_code
    FOREIGN KEY (sgg_cd) REFERENCES districts (sgg_cd)
    ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE visitor_residence_counts
    ADD CONSTRAINT fk_residence_region_code
    FOREIGN KEY (sgg_cd) REFERENCES districts (sgg_cd)
    ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE visitor_demographics
    ADD CONSTRAINT fk_demographics_region_code
    FOREIGN KEY (sgg_cd) REFERENCES districts (sgg_cd)
    ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE nationality_tourism_spending
    ADD CONSTRAINT fk_nationality_spending_region_code
    FOREIGN KEY (sgg_cd) REFERENCES districts (sgg_cd)
    ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE industry_tourism_spending
    ADD CONSTRAINT fk_industry_spending_region_code
    FOREIGN KEY (sgg_cd) REFERENCES districts (sgg_cd)
    ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE foreign_epay_spending
    ADD CONSTRAINT fk_epay_spending_region_code
    FOREIGN KEY (sgg_cd) REFERENCES districts (sgg_cd)
    ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE paid_attractions
    ADD CONSTRAINT fk_paid_attraction_region_code
    FOREIGN KEY (sgg_cd) REFERENCES districts (sgg_cd)
    ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE tourism_places
    ADD CONSTRAINT fk_tourism_place_region_code
    FOREIGN KEY (sgg_cd) REFERENCES districts (sgg_cd)
    ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE navigation_search_counts
    ADD CONSTRAINT fk_navigation_region_code
    FOREIGN KEY (sgg_cd) REFERENCES districts (sgg_cd)
    ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE tourism_interest_counts
    ADD CONSTRAINT fk_interest_region_code
    FOREIGN KEY (sgg_cd) REFERENCES districts (sgg_cd)
    ON UPDATE CASCADE ON DELETE RESTRICT;
