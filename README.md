# 드론 비행 전 체크리스트

서버 없이 정적 페이지 + Supabase만으로 동작하는 드론 비행 전 안전 점검 모바일 웹앱.
GitHub Pages로 호스팅한다.

- **점검 화면**: https://souvenir-hwang.github.io/drone-preflight-checklist/
- **기록 조회**: https://souvenir-hwang.github.io/drone-preflight-checklist/reports.html

## 구성

```
docs/
├─ index.html     # 점검 화면 (드론 선택 · 20개 항목 · GPS 일출/일몰 판정 · 결과 저장)
└─ reports.html   # 점검 기록 조회 화면 (담당자용)

체크리스트.txt                              # 점검 항목 원본 스펙
드론리스트.xlsx                             # 드론 선택 목록 원본
드론 비행 전 안전 점검 리스트 (Checklist).docx  # 최초 요구사항 문서
QR코드.png                                  # 점검 페이지 접속용 QR
```

프런트엔드(모바일 UI · 브라우저 GPS · 일출/일몰 계산)는 `docs/index.html` 안의 JS 에서 전부 동작한다.
서버 코드가 전혀 없다 — 페이지는 GitHub Pages가 정적으로 서빙하고, 데이터는 브라우저가
Supabase REST API를 직접 호출해 저장·조회한다.

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
- 정책상 `INSERT`·`SELECT`만 허용되고 `UPDATE`·`DELETE`는 막혀 있어, 제출된 기록은 이후 수정·삭제될 수 없다.

Supabase 프로젝트의 테이블 스키마·RLS 정책 SQL은 이 저장소에는 포함되어 있지 않다
(별도로 Supabase 대시보드에서 관리).

## 점검 항목

체크리스트는 `docs/index.html` 안 `items` 배열에 하드코딩되어 있으며, 원본 스펙은
[체크리스트.txt](체크리스트.txt)를 참고한다. 항목 추가/수정 시 두 곳을 함께 확인할 것.
