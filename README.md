# 드론 비행 전 체크리스트 (Flask)

사내 서버에 배포하여, 외부에서 휴대폰으로 접속하는 모바일 점검 페이지.

## 구성

```
260617/
├─ app.py              # Flask 앱 (페이지 서빙 + /healthz + /api/reports 저장 API)
├─ run_server.py       # 운영 실행 (waitress WSGI)
├─ requirements.txt
├─ reports.db           # 점검 결과 SQLite (최초 실행 시 자동 생성, git 미포함)
├─ templates/
│  ├─ index.html       # 점검 화면 (기존 drone_checklist.html 그대로)
│  └─ reports.html     # 점검 기록 조회 화면 (/reports)
└─ static/             # (선택) 정적 리소스
```

프런트엔드(모바일 UI · 브라우저 GPS · 일출/일몰 계산)는 모두 `index.html` 안의 JS 에서 동작한다.
점검 완료 시 결과는 `mailto` 대신 `POST /api/reports` 로 서버에 전송되어 `reports.db`(SQLite)에 저장된다.
저장 항목은 **드론 고유번호·점검 시각·GPS 좌표·항목별 결과**뿐이며, 조종자를 식별하는 값은 저장하지 않는다.
담당자는 `/reports` 화면에서 최근 200건을 조회할 수 있다(별도 로그인 없음 — 사내망 접근으로만 제한된다는 전제).

## 설치

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

## 실행

개발(자동 리로드):
```bash
python app.py
```

운영(사내 서버):
```bash
python run_server.py
```

기본 포트 `8000`. 브라우저에서 `http://<서버IP>:8000` 접속.

## ⚠️ HTTPS 필수 (중요)

모바일 브라우저의 **GPS(위치정보)** 는 보안 컨텍스트(HTTPS)에서만 동작한다.
외부 접속 도메인은 반드시 **HTTPS** 로 노출해야 GPS·일출/일몰 자동판정이 작동한다.

권장 배포: 리버스 프록시(IIS / Nginx / Apache)가 HTTPS 를 종단하고
내부적으로 `127.0.0.1:8000` 의 waitress 로 전달.

Nginx 예시:
```nginx
server {
    listen 443 ssl;
    server_name drone.example.co.kr;
    ssl_certificate     /path/cert.pem;
    ssl_certificate_key /path/key.pem;
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $remote_addr;
    }
}
```

## 점검 결과 저장 · 조회

- 저장: 클라이언트가 `POST /api/reports` 로 JSON 전송 → `reports.db`(SQLite)에 적재.
- 조회: `GET /reports` 웹 화면(최근 200건, 클릭 시 항목별 상세) 또는
  `GET /api/reports`(목록) / `GET /api/reports/<id>`(상세) API 직접 호출.
- `reports.db`는 운영 데이터이므로 `.gitignore`에 포함되어 저장소에 커밋되지 않는다.
  서버 이전/백업 시 이 파일만 별도로 옮기면 된다.
