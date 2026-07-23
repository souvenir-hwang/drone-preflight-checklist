# 드론 비행 전 체크리스트

서버 없이 정적 페이지 + Supabase만으로 동작하는 드론 비행 전 안전 점검 모바일 웹앱.
GitHub Pages로 호스팅한다.

- **점검 화면**: https://souvenir-hwang.github.io/drone-preflight-checklist/
- **관리 화면**: https://souvenir-hwang.github.io/drone-preflight-checklist/admin.html (PIN 필요)

## 구성

```
docs/
├─ index.html          # 점검 화면 (드론 선택 · 체크리스트 · GPS 일출/일몰 판정 · 결과 저장)
├─ reports.html        # 점검 기록 현황 (조회·선택 삭제·엑셀 다운로드) — 로그인 없이 공개
├─ admin.html           # 관리 허브 (PIN 게이트, 하위 관리 화면 링크)
├─ admin-drones.html    # 드론 목록 관리 (추가·수정·삭제)
├─ admin-items.html     # 체크리스트 항목 관리 (추가·수정·삭제·순서변경)
└─ admin-common.js      # 관리 화면 공통: PIN 게이트 + Supabase 접속정보

체크리스트.txt                              # 점검 항목 최초 원본 스펙 (참고용, 현재는 DB가 정본)
드론리스트.xlsx                             # 드론 선택 목록 최초 원본 (참고용, 현재는 DB가 정본)
드론 비행 전 안전 점검 리스트 (Checklist).docx  # 최초 요구사항 문서
```

프런트엔드(모바일 UI · 브라우저 GPS · 일출/일몰 계산)는 `docs/index.html` 안의 JS 에서 전부 동작한다.
서버 코드가 전혀 없다 — 페이지는 GitHub Pages가 정적으로 서빙하고, 데이터는 브라우저가
Supabase REST API를 직접 호출해 저장·조회한다.

드론 목록과 체크리스트 항목은 더 이상 하드코딩되어 있지 않고 Supabase `drones`·`checklist_items`
테이블에서 매번 불러온다 — `admin.html`에서 PIN(코드 내 `ADMIN_PIN`, `admin-common.js`)을 입력하면
드론 목록·체크리스트 항목을 화면에서 직접 추가·수정·삭제할 수 있다. 이 PIN은 UI 진입을 막는
정도이며, 실제 접근 제어는 Supabase Row Level Security로 anon 역할에 전체 권한을 허용해 둔
상태라는 점에 유의한다(사내 도구 성격상 감수한 트레이드오프).

## 배포 (GitHub Pages)

1. 이 저장소를 GitHub에 push
2. **Settings → Pages → Build and deployment → Source: Deploy from a branch**
3. **Branch: `main` / Folder: `/docs`** 선택 후 저장
4. 몇 분 뒤 `https://<계정>.github.io/<저장소명>/` 에서 접속 가능 (HTTPS 자동 적용)

GitHub Pages는 HTTPS를 기본 제공하므로, 별도 리버스 프록시나 인증서 설정이 필요 없다.
(모바일 브라우저의 GPS는 HTTPS 환경에서만 동작하는데, 이 조건이 자동으로 충족된다.)

## 점검 결과 저장 · 조회 (Supabase)

- 저장: `docs/index.html`의 제출 버튼이 Supabase `reports` 테이블에 `INSERT` 요청을 직접 보낸다.
- 조회: `docs/reports.html`에서 최근 200건 목록과 항목별 상세를 조회할 수 있다(로그인 없음).
- 저장 항목: **드론 고유번호 · 점검 시각 · GPS 좌표 · 항목별 결과**뿐이며, 조종자를 식별하는 값은 저장하지 않는다.
- GPS 좌표와 드론 번호는 의도적으로 공개(Row Level Security: 누구나 조회 가능) — 특정 지점에서
  드론이 발견되었을 때 교차검증하기 위함이다.
- 삭제는 `reports.html`에서 체크박스로 선택 후 PIN을 입력해야 진행된다(UI 단 게이팅, `UPDATE`는 여전히 막혀 있음).

Supabase 프로젝트의 테이블 스키마·RLS 정책 SQL은 이 저장소에는 포함되어 있지 않다
(별도로 Supabase 대시보드에서 관리).

## 드론 목록 · 체크리스트 항목

`admin-drones.html`·`admin-items.html`에서 관리한다. 체크리스트 항목의 `key` 컬럼은
코드에서 특수 로직(3번 항목의 GPS 일출/일몰 자동판정 = `sun_check`, 12번 항목의 방재센터
전화번호 자동 링크 = `fire_center`)을 항목 순서가 아니라 이 값으로 찾는 안정적 식별자다.
기존 항목의 `key`를 바꾸거나 `sun_check`/`fire_center` 항목을 삭제하면 해당 특수 동작이
빠지므로 주의한다. 새 항목을 추가할 때는 임의의 고유한 `key`를 지정하면 된다.
