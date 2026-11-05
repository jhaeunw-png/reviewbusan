
# 부산 관광 데이터 분석

부산 관광 관련 데이터를 수집해 CSV와 MariaDB에 저장하고, 방문객·관광 소비·관광지 정보를 그래프로 시각화하는 프로젝트입니다.

## 프로젝트 구성

| 경로 | 설명 |
| --- | --- |
| `src/data_collection/` | 관광 데이터를 수집하고 지역 코드·관광지 위치를 정리하는 스크립트 |
| `src/data_storage/` | `data/results/`의 수집 결과를 읽어 통합 데이터베이스에 적재하는 스크립트 |
| `src/visualization/` | CSV 또는 DB 데이터로 차트와 지도를 만드는 스크립트 |
| `data/` | 원본 데이터, 지적도, 수집 결과를 보관하는 폴더 |
| `data/results/` | 수집·가공된 CSV와 시각화 결과가 저장되는 폴더 |
| `database/` | MariaDB용 Docker Compose 설정, 환경 변수 예시, 초기화 SQL 및 [DB 사용 안내](database/README.md) |
| `docs/` | 요구사항 문서, 발표 자료 등 프로젝트 문서 |
| `backend/`, `frontend/` | 현재 별도 구현 파일이 없는 폴더 |
| `environment.yml` | Python Conda 환경의 패키지 목록 |

## 시작하기

아래 명령은 **저장소 루트에서** 실행하세요. 스크립트가 `data/`와 `database/.env`를 상대경로로 참조합니다.

### 1. Python 환경 만들기

Conda가 설치되어 있어야 합니다.

```bash
conda env create -f environment.yml
conda activate rise_team_1
```

이미 환경을 만든 뒤 `environment.yml`이 바뀌었다면 다음 명령으로 갱신할 수 있습니다.

```bash
conda env update -f environment.yml --prune
```

### 2. 환경 변수 설정하기

루트의 `.env.sample`을 `.env`로 복사한 뒤 공공데이터포털 API 키와 카카오 REST API 키를 입력하세요. DB를 사용할 경우 `database/.env.sample`도 `database/.env`로 복사하고 포트, DB 이름, 사용자명 및 비밀번호를 설정하세요. 실제 `.env` 파일에는 비밀키가 들어갈 수 있으므로 공유하지 마세요.

### 3. 데이터베이스 실행하기 (DB 사용 시)

Docker Compose가 설치되어 있고 `database/.env`를 작성했다면:

```bash
docker compose -f database/docker-compose.yml --env-file database/.env up -d
```

DB 설정과 접속 방법은 [database/README.md](database/README.md)를 참고하세요. DB를 읽거나 쓰는 스크립트는 `database/.env`의 접속 정보를 사용합니다.

## 데이터 작업 흐름

1. `src/data_collection/`에서 필요한 수집 스크립트를 실행해 `data/results/`에 CSV를 생성합니다. 일부 수집 스크립트는 DB 연결도 사용합니다.
2. `src/data_storage/`의 통합 적재 스크립트로 준비된 CSV를 DB에 넣습니다.
3. `src/visualization/`에서 필요한 시각화 스크립트를 실행합니다. 생성된 이미지의 주요 저장 위치는 `data/results/visualization/`입니다.

예를 들어 지역 코드 CSV는 다음과 같이 생성할 수 있습니다.

```bash
python src/data_collection/00_지역코드_시도_시군구_읍면동.py
```

스크립트마다 필요한 입력 CSV, API 키, DB 연결이 다릅니다. 실행 전 해당 파일 상단의 입력 경로와 환경 변수 설정을 확인하세요. 관광지 위치 수집과 일부 지도 시각화에는 `data/지적도/sig.shp`가 필요합니다.

## 데이터 출처

- [지적도 자료 안내](http://www.gisdeveloper.co.kr/?p=2332)
