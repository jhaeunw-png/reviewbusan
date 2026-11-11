/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19-11.7.2-MariaDB, for Win64 (AMD64)
--
-- Host: localhost    Database: rise_db
-- ------------------------------------------------------
-- Server version	13.0.2-MariaDB-ubu2604

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*M!100616 SET @OLD_NOTE_VERBOSITY=@@NOTE_VERBOSITY, NOTE_VERBOSITY=0 */;

--
-- Table structure for table `age_gender_visitor_counts`
--

DROP TABLE IF EXISTS `age_gender_visitor_counts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `age_gender_visitor_counts` (
  `base_ym` char(7) NOT NULL COMMENT '기준 연월(YYYY-MM)',
  `sgg_cd` char(5) NOT NULL COMMENT '방문 시군구 코드',
  `age_group` varchar(20) NOT NULL COMMENT '연령대',
  `gender` enum('남성','여성') NOT NULL COMMENT '성별',
  `visitor_counts` bigint(20) unsigned NOT NULL COMMENT '방문자 수',
  PRIMARY KEY (`base_ym`,`sgg_cd`,`age_group`,`gender`),
  KEY `idx_demographics_group` (`age_group`,`gender`),
  KEY `fk_demographics_region_code` (`sgg_cd`),
  CONSTRAINT `fk_demographics_region_code` FOREIGN KEY (`sgg_cd`) REFERENCES `sigungu` (`sgg_cd`) ON UPDATE CASCADE,
  CONSTRAINT `chk_demographics_base_ym` CHECK (`base_ym` regexp '^[0-9]{4}-(0[1-9]|1[0-2])$')
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='월별 성별·연령대별 방문자 수';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `country_holidays`
--

DROP TABLE IF EXISTS `country_holidays`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `country_holidays` (
  `country_code` char(2) NOT NULL COMMENT 'ISO 3166-1 alpha-2 국가·지역 코드',
  `holiday_date` date NOT NULL COMMENT '공휴일 날짜',
  `country_name` varchar(30) NOT NULL COMMENT '국가·지역명',
  `holiday_name` varchar(150) NOT NULL COMMENT '공휴일명',
  PRIMARY KEY (`country_code`,`holiday_date`),
  KEY `idx_country_holidays_date` (`holiday_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='국가·지역별 날짜 단위 공휴일';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `foreign_epay_amounts`
--

DROP TABLE IF EXISTS `foreign_epay_amounts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `foreign_epay_amounts` (
  `base_ym` char(7) NOT NULL COMMENT '기준 연월(YYYY-MM)',
  `sgg_cd` char(5) NOT NULL COMMENT '소비 발생 시군구 코드',
  `nationality_id` smallint(5) unsigned NOT NULL COMMENT '국가 ID',
  `detail_industry_id` smallint(5) unsigned NOT NULL COMMENT '관광 세부업종 ID',
  `spend_amt` bigint(20) unsigned NOT NULL COMMENT '간편결제 관광소비 금액(천원)',
  PRIMARY KEY (`base_ym`,`sgg_cd`,`nationality_id`,`detail_industry_id`),
  KEY `idx_epay_spending_nationality` (`nationality_id`),
  KEY `idx_epay_spending_detail_industry` (`detail_industry_id`),
  KEY `fk_epay_spending_region_code` (`sgg_cd`),
  CONSTRAINT `fk_epay_spending_detail_industry` FOREIGN KEY (`detail_industry_id`) REFERENCES `tourism_detail_categories` (`detail_industry_id`) ON UPDATE CASCADE,
  CONSTRAINT `fk_epay_spending_nationality` FOREIGN KEY (`nationality_id`) REFERENCES `nationalities` (`nationality_id`) ON UPDATE CASCADE,
  CONSTRAINT `fk_epay_spending_region_code` FOREIGN KEY (`sgg_cd`) REFERENCES `sigungu` (`sgg_cd`) ON UPDATE CASCADE,
  CONSTRAINT `chk_epay_spending_base_ym` CHECK (`base_ym` regexp '^[0-9]{4}-(0[1-9]|1[0-2])$')
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='월별 시군구·외국인 국가·세부업종별 간편결제 관광소비 금액';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `kto_large_categories`
--

DROP TABLE IF EXISTS `kto_large_categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `kto_large_categories` (
  `large_cat_cd` char(3) NOT NULL COMMENT 'KTO 대분류 코드',
  `large_cat_nm` varchar(50) NOT NULL COMMENT 'KTO 대분류명',
  PRIMARY KEY (`large_cat_cd`),
  KEY `idx_kto_large_category_nm` (`large_cat_nm`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='한국관광공사 관광 콘텐츠 대분류';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `kto_mid_categories`
--

DROP TABLE IF EXISTS `kto_mid_categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `kto_mid_categories` (
  `mid_cat_cd` char(5) NOT NULL COMMENT 'KTO 중분류 코드',
  `mid_cat_nm` varchar(50) NOT NULL COMMENT 'KTO 중분류명',
  `large_cat_cd` char(3) NOT NULL COMMENT 'KTO 대분류 코드',
  PRIMARY KEY (`mid_cat_cd`),
  UNIQUE KEY `uq_kto_mid_category_name` (`large_cat_cd`,`mid_cat_nm`),
  KEY `idx_kto_mid_large` (`large_cat_cd`),
  CONSTRAINT `fk_kto_mid_large` FOREIGN KEY (`large_cat_cd`) REFERENCES `kto_large_categories` (`large_cat_cd`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='한국관광공사 관광 콘텐츠 중분류';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `kto_small_categories`
--

DROP TABLE IF EXISTS `kto_small_categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `kto_small_categories` (
  `small_cat_cd` char(9) NOT NULL COMMENT 'KTO 소분류 코드',
  `small_cat_nm` varchar(50) NOT NULL COMMENT 'KTO 소분류명',
  `mid_cat_cd` char(5) NOT NULL COMMENT 'KTO 중분류 코드',
  PRIMARY KEY (`small_cat_cd`),
  UNIQUE KEY `uq_kto_small_category_name` (`mid_cat_cd`,`small_cat_nm`),
  KEY `idx_kto_small_mid` (`mid_cat_cd`),
  CONSTRAINT `fk_kto_small_mid` FOREIGN KEY (`mid_cat_cd`) REFERENCES `kto_mid_categories` (`mid_cat_cd`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='한국관광공사 관광 콘텐츠 소분류';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `mice_events`
--

DROP TABLE IF EXISTS `mice_events`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `mice_events` (
  `event_id` int(10) unsigned NOT NULL COMMENT '행사 ID',
  `base_ym` char(7) NOT NULL COMMENT '조회 기준 연월(YYYY-MM)',
  `event_type_cd` tinyint(3) unsigned NOT NULL COMMENT '행사 유형 코드',
  `event_type_nm` varchar(20) NOT NULL COMMENT '행사 유형명',
  `event_nm` varchar(200) NOT NULL COMMENT '행사명',
  `place_nm` varchar(500) DEFAULT NULL COMMENT '행사 장소',
  `start_date` date NOT NULL COMMENT '행사 시작일',
  `end_date` date NOT NULL COMMENT '행사 종료일',
  `event_time` varchar(255) DEFAULT NULL COMMENT '행사 시간 설명',
  `attachment_id` char(64) CHARACTER SET ascii COLLATE ascii_bin DEFAULT NULL COMMENT '첨부파일 ID',
  `file_sn` char(32) CHARACTER SET ascii COLLATE ascii_bin DEFAULT NULL COMMENT '파일 번호',
  PRIMARY KEY (`event_id`,`base_ym`),
  KEY `idx_mice_period` (`start_date`,`end_date`),
  KEY `idx_mice_type` (`event_type_cd`),
  CONSTRAINT `chk_mice_base_ym` CHECK (`base_ym` regexp '^[0-9]{4}-(0[1-9]|1[0-2])$'),
  CONSTRAINT `chk_mice_event_type` CHECK (`event_type_cd` between 1 and 4),
  CONSTRAINT `chk_mice_period` CHECK (`start_date` <= `end_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='부산 MICE 행사 정보';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `nationalities`
--

DROP TABLE IF EXISTS `nationalities`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `nationalities` (
  `nationality_id` smallint(5) unsigned NOT NULL AUTO_INCREMENT COMMENT '국가 ID',
  `nationality_cd` char(3) DEFAULT NULL COMMENT '외국인 국가 코드',
  `nationality_nm` varchar(50) NOT NULL COMMENT '국가명',
  PRIMARY KEY (`nationality_id`),
  UNIQUE KEY `uq_nationality_name` (`nationality_nm`),
  UNIQUE KEY `uq_nationality_code` (`nationality_cd`),
  CONSTRAINT `chk_nationality_cd` CHECK (`nationality_cd` is null or `nationality_cd` regexp '^[0-9]{3}$')
) ENGINE=InnoDB AUTO_INCREMENT=101 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='국가 기준정보';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `nationality_amounts`
--

DROP TABLE IF EXISTS `nationality_amounts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `nationality_amounts` (
  `base_ym` char(7) NOT NULL COMMENT '기준 연월(YYYY-MM)',
  `sgg_cd` char(5) NOT NULL COMMENT '소비 발생 시군구 코드',
  `nationality_id` smallint(5) unsigned NOT NULL COMMENT '국가 ID',
  `spend_amt` bigint(20) unsigned NOT NULL COMMENT '관광소비 금액',
  PRIMARY KEY (`base_ym`,`sgg_cd`,`nationality_id`),
  KEY `idx_nationality_spending_nationality` (`nationality_id`),
  KEY `fk_nationality_spending_region_code` (`sgg_cd`),
  CONSTRAINT `fk_nationality_spending_nationality` FOREIGN KEY (`nationality_id`) REFERENCES `nationalities` (`nationality_id`) ON UPDATE CASCADE,
  CONSTRAINT `fk_nationality_spending_region_code` FOREIGN KEY (`sgg_cd`) REFERENCES `sigungu` (`sgg_cd`) ON UPDATE CASCADE,
  CONSTRAINT `chk_nationality_spending_base_ym` CHECK (`base_ym` regexp '^[0-9]{4}-(0[1-9]|1[0-2])$')
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='월별 시군구·국가별 관광소비 금액';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `nationality_visitor_counts`
--

DROP TABLE IF EXISTS `nationality_visitor_counts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `nationality_visitor_counts` (
  `base_ym` char(7) NOT NULL COMMENT '기준 연월(YYYY-MM)',
  `sgg_cd` char(5) NOT NULL COMMENT '방문 시군구 코드',
  `nationality_id` smallint(5) unsigned NOT NULL COMMENT '국가 ID',
  `visitor_counts` bigint(20) unsigned NOT NULL COMMENT '관광객 수',
  PRIMARY KEY (`base_ym`,`sgg_cd`,`nationality_id`),
  KEY `idx_tourist_nationality` (`nationality_id`),
  KEY `fk_tourist_region_code` (`sgg_cd`),
  CONSTRAINT `fk_tourist_nationality` FOREIGN KEY (`nationality_id`) REFERENCES `nationalities` (`nationality_id`) ON UPDATE CASCADE,
  CONSTRAINT `fk_tourist_region_code` FOREIGN KEY (`sgg_cd`) REFERENCES `sigungu` (`sgg_cd`) ON UPDATE CASCADE,
  CONSTRAINT `chk_tourist_base_ym` CHECK (`base_ym` regexp '^[0-9]{4}-(0[1-9]|1[0-2])$')
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='월별 시군구·국가별 외국인 관광객 수';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `navigation_search_counts`
--

DROP TABLE IF EXISTS `navigation_search_counts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `navigation_search_counts` (
  `base_ym` char(7) NOT NULL COMMENT '기준 연월(YYYY-MM)',
  `sgg_cd` char(5) NOT NULL COMMENT '검색 대상 소재 시군구 코드',
  `poi_id` char(32) CHARACTER SET ascii COLLATE ascii_bin NOT NULL COMMENT '관광지·맛집 POI ID',
  `audience_type` enum('전체','외지인','현지인') NOT NULL COMMENT '방문자 구분',
  `ranking` tinyint(3) unsigned NOT NULL COMMENT '검색 순위',
  `search_cnt` bigint(20) unsigned NOT NULL COMMENT '검색 건수',
  PRIMARY KEY (`base_ym`,`sgg_cd`,`poi_id`,`audience_type`),
  KEY `idx_navigation_rank` (`base_ym`,`sgg_cd`,`audience_type`,`ranking`),
  KEY `fk_navigation_place` (`poi_id`),
  KEY `fk_navigation_region_code` (`sgg_cd`),
  CONSTRAINT `fk_navigation_place` FOREIGN KEY (`poi_id`) REFERENCES `tourism_places` (`poi_id`) ON UPDATE CASCADE,
  CONSTRAINT `fk_navigation_region_code` FOREIGN KEY (`sgg_cd`) REFERENCES `sigungu` (`sgg_cd`) ON UPDATE CASCADE,
  CONSTRAINT `chk_navigation_base_ym` CHECK (`base_ym` regexp '^[0-9]{4}-(0[1-9]|1[0-2])$'),
  CONSTRAINT `chk_navigation_rank` CHECK (`ranking` between 1 and 100)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='월별 관광지·맛집 내비게이션 검색 순위와 검색 건수';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `paid_attraction_counts`
--

DROP TABLE IF EXISTS `paid_attraction_counts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `paid_attraction_counts` (
  `base_ym` char(7) NOT NULL COMMENT '기준 연월(YYYY-MM)',
  `sgg_cd` char(5) NOT NULL COMMENT '시군구 코드',
  `attraction_id` smallint(5) unsigned NOT NULL COMMENT '유료 관광지 대체키',
  `ranking` tinyint(3) unsigned NOT NULL COMMENT '월별 순위',
  `domestic_cnt` bigint(20) unsigned NOT NULL COMMENT '내국인 입장객 수',
  `total_cnt` bigint(20) unsigned NOT NULL COMMENT '전체 입장객 수',
  PRIMARY KEY (`base_ym`,`sgg_cd`,`attraction_id`),
  KEY `idx_paid_attraction_rank` (`base_ym`,`sgg_cd`,`ranking`),
  KEY `fk_paid_count_attraction` (`sgg_cd`,`attraction_id`),
  CONSTRAINT `fk_paid_count_attraction` FOREIGN KEY (`sgg_cd`, `attraction_id`) REFERENCES `paid_attractions` (`sgg_cd`, `attraction_id`) ON UPDATE CASCADE,
  CONSTRAINT `chk_paid_attraction_base_ym` CHECK (`base_ym` regexp '^[0-9]{4}-(0[1-9]|1[0-2])$'),
  CONSTRAINT `chk_paid_attraction_rank` CHECK (`ranking` between 1 and 100),
  CONSTRAINT `chk_paid_attraction_count` CHECK (`domestic_cnt` <= `total_cnt`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='월별 유료 관광지 입장객 수';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `paid_attractions`
--

DROP TABLE IF EXISTS `paid_attractions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `paid_attractions` (
  `attraction_id` smallint(5) unsigned NOT NULL AUTO_INCREMENT COMMENT '유료 관광지 대체키',
  `sgg_cd` char(5) NOT NULL COMMENT '소재 시군구 코드',
  `attraction_nm` varchar(100) NOT NULL COMMENT '유료 관광지명',
  PRIMARY KEY (`attraction_id`),
  UNIQUE KEY `uq_paid_attraction_name` (`sgg_cd`,`attraction_nm`),
  UNIQUE KEY `uq_paid_attraction_district` (`sgg_cd`,`attraction_id`),
  KEY `idx_paid_attraction_name` (`attraction_nm`),
  CONSTRAINT `fk_paid_attraction_region_code` FOREIGN KEY (`sgg_cd`) REFERENCES `sigungu` (`sgg_cd`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=76 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='유료 관광지 기준정보';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `public_transport_counts`
--

DROP TABLE IF EXISTS `public_transport_counts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `public_transport_counts` (
  `base_ym` char(7) NOT NULL COMMENT '기준 연월(YYYY-MM)',
  `sgg_cd` char(5) NOT NULL COMMENT '이용 시군구 코드',
  `user_type_cd` char(2) NOT NULL COMMENT 'STCIS 이용자 유형 코드',
  `user_type_nm` varchar(20) NOT NULL COMMENT '이용자 유형명',
  `use_cnt` bigint(20) unsigned NOT NULL COMMENT '대중교통 이용 인원',
  PRIMARY KEY (`base_ym`,`sgg_cd`,`user_type_cd`),
  KEY `idx_transport_user_type` (`user_type_cd`),
  KEY `fk_transport_region_code` (`sgg_cd`),
  CONSTRAINT `fk_transport_region_code` FOREIGN KEY (`sgg_cd`) REFERENCES `sigungu` (`sgg_cd`) ON UPDATE CASCADE,
  CONSTRAINT `chk_transport_base_ym` CHECK (`base_ym` regexp '^[0-9]{4}-(0[1-9]|1[0-2])$')
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='월별 시군구·이용자 유형별 대중교통 이용 인원';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `residence_visitor_counts`
--

DROP TABLE IF EXISTS `residence_visitor_counts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `residence_visitor_counts` (
  `base_ym` char(7) NOT NULL COMMENT '기준 연월(YYYY-MM)',
  `sgg_cd` char(5) NOT NULL COMMENT '방문 시군구 코드',
  `origin_region_nm` varchar(30) NOT NULL COMMENT '출발 시도명',
  `origin_detail_nm` varchar(30) NOT NULL COMMENT '출발 상세지역명',
  `visitor_counts` bigint(20) unsigned NOT NULL COMMENT '방문자 수',
  PRIMARY KEY (`base_ym`,`sgg_cd`,`origin_region_nm`,`origin_detail_nm`),
  KEY `idx_residence_origin` (`origin_region_nm`,`origin_detail_nm`),
  KEY `fk_residence_region_code` (`sgg_cd`),
  CONSTRAINT `fk_residence_region_code` FOREIGN KEY (`sgg_cd`) REFERENCES `sigungu` (`sgg_cd`) ON UPDATE CASCADE,
  CONSTRAINT `chk_residence_base_ym` CHECK (`base_ym` regexp '^[0-9]{4}-(0[1-9]|1[0-2])$')
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='월별 방문자의 출발 거주지별 방문자 수';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `restaurants`
--

DROP TABLE IF EXISTS `restaurants`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `restaurants` (
  `restaurant_id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT '내부 음식점 행 ID',
  `source_row_no` int(10) unsigned NOT NULL COMMENT '원본 CSV의 데이터 행 번호(헤더 제외)',
  `license_no` varchar(50) NOT NULL COMMENT '원본 관리번호',
  `business_nm` varchar(255) NOT NULL COMMENT '사업장명',
  `business_subtype` varchar(100) DEFAULT NULL COMMENT '업태구분명',
  `facility_area_sqm` decimal(15,2) DEFAULT NULL COMMENT '시설총규모(제곱미터)',
  `status_nm` varchar(50) DEFAULT NULL COMMENT '영업상태명',
  `license_date` date DEFAULT NULL COMMENT '인허가일자',
  `closure_date` date DEFAULT NULL COMMENT '폐업일자',
  `road_address` varchar(500) DEFAULT NULL COMMENT '도로명주소',
  `lot_address` varchar(500) DEFAULT NULL COMMENT '지번주소',
  `sgg_cd` char(5) DEFAULT NULL COMMENT '주소에서 매핑한 시군구 코드',
  `source_x` decimal(18,8) DEFAULT NULL COMMENT '원본 좌표정보(X)',
  `source_y` decimal(18,8) DEFAULT NULL COMMENT '원본 좌표정보(Y)',
  `source_modified_at` datetime DEFAULT NULL COMMENT '원본 최종수정시점',
  `source_data` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '원본 CSV 전체 컬럼' CHECK (json_valid(`source_data`)),
  PRIMARY KEY (`restaurant_id`),
  UNIQUE KEY `uq_restaurant_source_row` (`source_row_no`),
  KEY `idx_restaurant_license` (`license_no`),
  KEY `idx_restaurant_region_status` (`sgg_cd`,`status_nm`),
  CONSTRAINT `fk_restaurant_region_code` FOREIGN KEY (`sgg_cd`) REFERENCES `sigungu` (`sgg_cd`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=132152 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='부산 일반음식점 사업장 정보';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sidos`
--

DROP TABLE IF EXISTS `sidos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `sidos` (
  `sido_cd` char(2) NOT NULL COMMENT '시도 코드',
  `sido_nm` varchar(50) NOT NULL COMMENT '시도명',
  PRIMARY KEY (`sido_cd`),
  UNIQUE KEY `uq_sido_name` (`sido_nm`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='시도 기준정보';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sigungu`
--

DROP TABLE IF EXISTS `sigungu`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `sigungu` (
  `sgg_cd` char(5) NOT NULL COMMENT '시군구 코드',
  `sido_cd` char(2) NOT NULL COMMENT '시도 코드',
  `sgg_nm` varchar(50) NOT NULL COMMENT '시군구명',
  PRIMARY KEY (`sgg_cd`),
  UNIQUE KEY `uq_district_name` (`sido_cd`,`sgg_nm`),
  CONSTRAINT `fk_district_sido` FOREIGN KEY (`sido_cd`) REFERENCES `sidos` (`sido_cd`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='시군구 기준정보';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `stay_visitor_ratios`
--

DROP TABLE IF EXISTS `stay_visitor_ratios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `stay_visitor_ratios` (
  `base_ym` char(7) NOT NULL COMMENT '기준 연월(YYYY-MM)',
  `sgg_cd` char(5) NOT NULL COMMENT '방문 시군구 코드',
  `stay_ratio_pct` decimal(5,2) NOT NULL COMMENT '외지인 숙박방문자 비율(%)',
  PRIMARY KEY (`base_ym`,`sgg_cd`),
  KEY `fk_stay_visitor_ratios_region_code` (`sgg_cd`),
  CONSTRAINT `fk_stay_visitor_ratios_region_code` FOREIGN KEY (`sgg_cd`) REFERENCES `sigungu` (`sgg_cd`) ON UPDATE CASCADE,
  CONSTRAINT `chk_stay_visitor_ratios_base_ym` CHECK (`base_ym` regexp '^[0-9]{4}-(0[1-9]|1[0-2])$'),
  CONSTRAINT `chk_stay_visitor_ratios_pct` CHECK (`stay_ratio_pct` between 0 and 100)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='월별 시군구 외지인 숙박방문자 비율';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `stays`
--

DROP TABLE IF EXISTS `stays`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `stays` (
  `stay_id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT '내부 숙박시설 행 ID',
  `source_type` enum('tourist_lodging','lodging') NOT NULL COMMENT '관광숙박업 또는 숙박업 원본 구분',
  `source_row_no` int(10) unsigned NOT NULL COMMENT '원본 CSV의 데이터 행 번호(헤더 제외)',
  `license_no` varchar(50) NOT NULL COMMENT '원본 관리번호(중복 가능)',
  `business_nm` varchar(255) NOT NULL COMMENT '사업장명',
  `business_subtype` varchar(100) DEFAULT NULL COMMENT '관광숙박업상세명 또는 업태구분명',
  `room_cnt` int(10) unsigned DEFAULT NULL COMMENT '객실 수(원본 객실수 또는 양실수와 한실수의 합)',
  `status_nm` varchar(50) DEFAULT NULL COMMENT '영업상태명',
  `license_date` date DEFAULT NULL COMMENT '인허가일자',
  `closure_date` date DEFAULT NULL COMMENT '폐업일자',
  `road_address` varchar(500) DEFAULT NULL COMMENT '도로명주소',
  `lot_address` varchar(500) DEFAULT NULL COMMENT '지번주소',
  `sgg_cd` char(5) DEFAULT NULL COMMENT '주소에서 매핑한 시군구 코드',
  `source_x` decimal(18,8) DEFAULT NULL COMMENT '원본 좌표정보(X)',
  `source_y` decimal(18,8) DEFAULT NULL COMMENT '원본 좌표정보(Y)',
  `source_modified_at` datetime DEFAULT NULL COMMENT '원본 최종수정시점',
  `source_data` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '원본 CSV 전체 컬럼' CHECK (json_valid(`source_data`)),
  PRIMARY KEY (`stay_id`),
  UNIQUE KEY `uq_stay_source_row` (`source_type`,`source_row_no`),
  KEY `idx_stay_license` (`license_no`),
  KEY `idx_stay_region_status` (`sgg_cd`,`source_type`,`status_nm`),
  CONSTRAINT `fk_stay_region_code` FOREIGN KEY (`sgg_cd`) REFERENCES `sigungu` (`sgg_cd`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5351 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='부산 관광숙박업·숙박업 시설 정보';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tourism_categories`
--

DROP TABLE IF EXISTS `tourism_categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tourism_categories` (
  `industry_id` tinyint(3) unsigned NOT NULL AUTO_INCREMENT COMMENT '관광 대업종 ID',
  `industry_nm` varchar(50) NOT NULL COMMENT '관광 대업종명',
  PRIMARY KEY (`industry_id`),
  UNIQUE KEY `uq_tourism_industry_name` (`industry_nm`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='관광 대업종 기준정보';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tourism_category_amounts`
--

DROP TABLE IF EXISTS `tourism_category_amounts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tourism_category_amounts` (
  `base_ym` char(7) NOT NULL COMMENT '기준 연월(YYYY-MM)',
  `sgg_cd` char(5) NOT NULL COMMENT '소비 발생 시군구 코드',
  `industry_id` tinyint(3) unsigned NOT NULL COMMENT '관광 대업종 ID',
  `spend_amt` bigint(20) unsigned NOT NULL COMMENT '관광소비 금액',
  PRIMARY KEY (`base_ym`,`sgg_cd`,`industry_id`),
  KEY `idx_industry_spending_industry` (`industry_id`),
  KEY `fk_industry_spending_region_code` (`sgg_cd`),
  CONSTRAINT `fk_industry_spending_industry` FOREIGN KEY (`industry_id`) REFERENCES `tourism_categories` (`industry_id`) ON UPDATE CASCADE,
  CONSTRAINT `fk_industry_spending_region_code` FOREIGN KEY (`sgg_cd`) REFERENCES `sigungu` (`sgg_cd`) ON UPDATE CASCADE,
  CONSTRAINT `chk_industry_spending_base_ym` CHECK (`base_ym` regexp '^[0-9]{4}-(0[1-9]|1[0-2])$')
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='월별 시군구·업종별 관광소비 금액';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tourism_content_localizations`
--

DROP TABLE IF EXISTS `tourism_content_localizations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tourism_content_localizations` (
  `content_id` int(10) unsigned NOT NULL COMMENT '관광 콘텐츠 ID',
  `language` enum('내국인','영어권','일본어','중간체','중번체') NOT NULL COMMENT '언어권',
  `content_nm` varchar(200) NOT NULL COMMENT '해당 언어권의 최신 콘텐츠명',
  `content_url` varchar(255) NOT NULL COMMENT '해당 언어권의 최신 콘텐츠 URL',
  PRIMARY KEY (`content_id`,`language`),
  CONSTRAINT `fk_content_localization_content` FOREIGN KEY (`content_id`) REFERENCES `tourism_contents` (`content_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='관광 콘텐츠 언어권별 최신 명칭과 URL';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tourism_contents`
--

DROP TABLE IF EXISTS `tourism_contents`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tourism_contents` (
  `content_id` int(10) unsigned NOT NULL COMMENT '관광 콘텐츠 ID',
  `content_nm` varchar(200) NOT NULL COMMENT '좌표 검색용 대표 한글 콘텐츠명',
  `latitude` decimal(10,7) DEFAULT NULL COMMENT '위도',
  `longitude` decimal(10,7) DEFAULT NULL COMMENT '경도',
  PRIMARY KEY (`content_id`),
  KEY `idx_tourism_content_name` (`content_nm`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='관광 콘텐츠 대표 정보 및 위치 정보';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tourism_detail_categories`
--

DROP TABLE IF EXISTS `tourism_detail_categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tourism_detail_categories` (
  `detail_industry_id` smallint(5) unsigned NOT NULL AUTO_INCREMENT COMMENT '관광 세부업종 ID',
  `industry_id` tinyint(3) unsigned NOT NULL COMMENT '관광 대업종 ID',
  `detail_industry_nm` varchar(50) NOT NULL COMMENT '관광 세부업종명',
  PRIMARY KEY (`detail_industry_id`),
  UNIQUE KEY `uq_tourism_detail_industry` (`industry_id`,`detail_industry_nm`),
  CONSTRAINT `fk_detail_industry_parent` FOREIGN KEY (`industry_id`) REFERENCES `tourism_categories` (`industry_id`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=67 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='관광 세부업종 기준정보';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tourism_interest_counts`
--

DROP TABLE IF EXISTS `tourism_interest_counts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tourism_interest_counts` (
  `base_ym` char(7) NOT NULL COMMENT '기준 연월(YYYY-MM)',
  `sgg_cd` char(5) NOT NULL COMMENT '시군구 코드',
  `content_id` int(10) unsigned NOT NULL COMMENT '관광 콘텐츠 ID',
  `language` enum('내국인','영어권','일본어','중간체','중번체') NOT NULL COMMENT '언어권',
  `small_cat_cd` char(9) NOT NULL COMMENT 'KTO 소분류 코드',
  `visitor_counts` bigint(20) unsigned NOT NULL COMMENT '콘텐츠 방문자 수',
  PRIMARY KEY (`base_ym`,`sgg_cd`,`content_id`,`language`),
  KEY `idx_interest_content` (`content_id`,`language`),
  KEY `idx_interest_category` (`small_cat_cd`),
  KEY `fk_interest_region_code` (`sgg_cd`),
  CONSTRAINT `fk_interest_category` FOREIGN KEY (`small_cat_cd`) REFERENCES `kto_small_categories` (`small_cat_cd`) ON UPDATE CASCADE,
  CONSTRAINT `fk_interest_content_localization` FOREIGN KEY (`content_id`, `language`) REFERENCES `tourism_content_localizations` (`content_id`, `language`) ON UPDATE CASCADE,
  CONSTRAINT `fk_interest_region_code` FOREIGN KEY (`sgg_cd`) REFERENCES `sigungu` (`sgg_cd`) ON UPDATE CASCADE,
  CONSTRAINT `chk_interest_base_ym` CHECK (`base_ym` regexp '^[0-9]{4}-(0[1-9]|1[0-2])$')
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='월별 언어권별 관심 관광 콘텐츠 방문자 수';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tourism_places`
--

DROP TABLE IF EXISTS `tourism_places`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tourism_places` (
  `poi_id` char(32) CHARACTER SET ascii COLLATE ascii_bin NOT NULL COMMENT 'MD5 POI ID',
  `source_poi_id` char(32) CHARACTER SET ascii COLLATE ascii_bin NOT NULL COMMENT '원천 POI ID',
  `sgg_cd` char(5) NOT NULL COMMENT '소재 시군구 코드',
  `place_type` enum('관광지','맛집') NOT NULL COMMENT '장소 구분',
  `place_nm` varchar(100) NOT NULL COMMENT '장소명',
  `category_nm` varchar(50) NOT NULL COMMENT 'POI 카테고리명',
  `latitude` decimal(10,7) DEFAULT NULL COMMENT '위도(WGS84)',
  `longitude` decimal(10,7) DEFAULT NULL COMMENT '경도(WGS84)',
  PRIMARY KEY (`poi_id`),
  UNIQUE KEY `uq_tourism_place_source` (`source_poi_id`),
  KEY `idx_tourism_place_district` (`sgg_cd`,`place_type`),
  KEY `idx_tourism_place_name` (`place_nm`),
  CONSTRAINT `fk_tourism_place_region_code` FOREIGN KEY (`sgg_cd`) REFERENCES `sigungu` (`sgg_cd`) ON UPDATE CASCADE,
  CONSTRAINT `chk_tourism_place_poi_id` CHECK (`poi_id` regexp '^[0-9A-Fa-f]{32}$'),
  CONSTRAINT `chk_tourism_place_source_poi_id` CHECK (`source_poi_id` regexp '^[0-9A-Fa-f]{32}$'),
  CONSTRAINT `chk_tourism_place_latitude` CHECK (`latitude` is null or `latitude` between -90 and 90),
  CONSTRAINT `chk_tourism_place_longitude` CHECK (`longitude` is null or `longitude` between -180 and 180),
  CONSTRAINT `chk_tourism_place_coordinates` CHECK (`latitude` is null and `longitude` is null or `latitude` is not null and `longitude` is not null)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='관광지·맛집 POI 기준정보와 위치 좌표';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `umds`
--

DROP TABLE IF EXISTS `umds`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `umds` (
  `region_cd` char(10) NOT NULL COMMENT '법정동 전체 지역코드',
  `umd_cd` char(8) NOT NULL COMMENT '읍면동 코드',
  `sgg_cd` char(5) NOT NULL COMMENT '시군구 코드',
  `umd_nm` varchar(100) NOT NULL COMMENT '읍면동·법정리명',
  PRIMARY KEY (`region_cd`),
  KEY `idx_umd_code` (`umd_cd`),
  KEY `idx_umd_district` (`sgg_cd`),
  CONSTRAINT `fk_umd_district` FOREIGN KEY (`sgg_cd`) REFERENCES `sigungu` (`sgg_cd`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='읍면동·법정리 기준정보';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `visitor_stay_times`
--

DROP TABLE IF EXISTS `visitor_stay_times`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `visitor_stay_times` (
  `base_ym` char(7) NOT NULL COMMENT '기준 연월(YYYY-MM)',
  `sgg_cd` char(5) NOT NULL COMMENT '방문 시군구 코드',
  `avg_stay_minutes` decimal(10,1) NOT NULL COMMENT '외지인 평균 체류시간(분)',
  PRIMARY KEY (`base_ym`,`sgg_cd`),
  KEY `fk_visitor_stay_times_region_code` (`sgg_cd`),
  CONSTRAINT `fk_visitor_stay_times_region_code` FOREIGN KEY (`sgg_cd`) REFERENCES `sigungu` (`sgg_cd`) ON UPDATE CASCADE,
  CONSTRAINT `chk_visitor_stay_times_base_ym` CHECK (`base_ym` regexp '^[0-9]{4}-(0[1-9]|1[0-2])$'),
  CONSTRAINT `chk_visitor_stay_times_minutes` CHECK (`avg_stay_minutes` >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='월별 시군구 외지인 평균 체류시간';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `visitor_type_counts`
--

DROP TABLE IF EXISTS `visitor_type_counts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `visitor_type_counts` (
  `base_ym` char(7) NOT NULL COMMENT '기준 연월(YYYY-MM)',
  `sgg_cd` char(5) NOT NULL COMMENT '방문 시군구 코드',
  `visitor_type` enum('현지인','외지인','외국인') NOT NULL COMMENT '방문자 유형',
  `visitor_counts` bigint(20) unsigned DEFAULT NULL COMMENT '방문자 수(NULL은 자료 미수집)',
  PRIMARY KEY (`base_ym`,`sgg_cd`,`visitor_type`),
  KEY `fk_visitor_type_region_code` (`sgg_cd`),
  CONSTRAINT `fk_visitor_type_region_code` FOREIGN KEY (`sgg_cd`) REFERENCES `sigungu` (`sgg_cd`) ON UPDATE CASCADE,
  CONSTRAINT `chk_visitor_type_base_ym` CHECK (`base_ym` regexp '^[0-9]{4}-(0[1-9]|1[0-2])$')
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='월별 시군구·방문자 유형별 방문자 수';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping routines for database 'rise_db'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*M!100616 SET NOTE_VERBOSITY=@OLD_NOTE_VERBOSITY */;

-- Dump completed on 2026-11-11  9:49:22
