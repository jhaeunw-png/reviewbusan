CREATE TABLE IF NOT EXISTS sidos (
    sido_cd CHAR(2)     NOT NULL COMMENT '시도 코드',
    sido_nm VARCHAR(50) NOT NULL COMMENT '시도명',

    PRIMARY KEY (sido_cd),
    UNIQUE KEY uq_sido_name (sido_nm)
)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_unicode_ci
COMMENT = '시도 기준정보';


CREATE TABLE IF NOT EXISTS districts (
    sgg_cd  CHAR(5)     NOT NULL COMMENT '시군구 코드',
    sido_cd CHAR(2)     NOT NULL COMMENT '시도 코드',
    sgg_nm  VARCHAR(50) NOT NULL COMMENT '시군구명',

    PRIMARY KEY (sgg_cd),
    UNIQUE KEY uq_district_name (sido_cd, sgg_nm),

    CONSTRAINT fk_district_sido
        FOREIGN KEY (sido_cd) REFERENCES sidos (sido_cd)
        ON UPDATE CASCADE ON DELETE RESTRICT
)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_unicode_ci
COMMENT = '시군구 기준정보';


CREATE TABLE IF NOT EXISTS umds (
    region_cd CHAR(10)     NOT NULL COMMENT '법정동 전체 지역코드',
    umd_cd    CHAR(8)      NOT NULL COMMENT '읍면동 코드',
    sgg_cd    CHAR(5)      NOT NULL COMMENT '시군구 코드',
    umd_nm    VARCHAR(100) NOT NULL COMMENT '읍면동·법정리명',

    PRIMARY KEY (region_cd),
    KEY idx_umd_code (umd_cd),
    KEY idx_umd_district (sgg_cd),

    CONSTRAINT fk_umd_district
        FOREIGN KEY (sgg_cd) REFERENCES districts (sgg_cd)
        ON UPDATE CASCADE ON DELETE RESTRICT
)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_unicode_ci
COMMENT = '읍면동·법정리 기준정보';
