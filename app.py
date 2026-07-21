# -*- coding: utf-8 -*-
"""
드론 비행 전 체크리스트 - Flask 서버

사내 서버 배포용. 외부 휴대폰에서 접속하는 모바일 점검 페이지를 서빙하고,
점검 결과를 로컬 SQLite(reports.db)에 저장한다.
- 프런트엔드(HTML/JS)는 templates/index.html 에 그대로 유지
- 브라우저 GPS·일출/일몰 계산은 클라이언트(JS)에서 처리, 결과만 서버로 전송
- 저장 항목 : 드론 고유번호, 점검 시각, GPS 좌표, 항목별 결과 (조종자 식별정보 없음)
- 조회 화면(/reports)은 별도 인증이 없으므로 사내망 접근으로만 제한한다고 가정한다
"""
import json
import os
import sqlite3
from datetime import datetime

from flask import Flask, g, jsonify, render_template, request

app = Flask(__name__)

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports.db")


def get_db():
    """요청 컨텍스트별 SQLite 연결 (waitress 멀티스레드에서 연결 공유 방지)."""
    db = getattr(g, "_db", None)
    if db is None:
        db = g._db = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_db(_exc):
    db = getattr(g, "_db", None)
    if db is not None:
        db.close()


def init_db():
    """앱 시작 시 1회: 테이블이 없으면 생성."""
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS reports (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at    TEXT NOT NULL,      -- 서버 수신 시각 (UTC ISO)
                client_ts     TEXT,                -- 클라이언트 표시 시각 (로컬 문자열)
                drone         TEXT,                -- 드론 고유번호 (예: DR000007)
                lat           REAL,
                lng           REAL,
                gps_accuracy  REAL,
                sunrise_min   INTEGER,             -- 일출(자정 기준 분), 없으면 NULL
                sunset_min    INTEGER,
                is_daylight   INTEGER,             -- 0/1, 없으면 NULL
                ok_count      INTEGER NOT NULL,
                bad_count     INTEGER NOT NULL,
                verdict       TEXT NOT NULL,        -- '비행가능' / '비행보류'
                items_json    TEXT NOT NULL         -- [{q, state}] 전체 20항목
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


@app.route("/")
def index():
    """체크리스트 메인 페이지."""
    return render_template("index.html")


@app.route("/healthz")
def healthz():
    """로드밸런서/모니터링용 헬스체크."""
    return jsonify(status="ok")


@app.route("/api/reports", methods=["POST"])
def create_report():
    """점검 결과 저장. 조종자 식별정보는 받지 않는다."""
    data = request.get_json(silent=True) or {}

    drone = (data.get("drone") or "").strip()
    items = data.get("items")
    if not drone:
        return jsonify(ok=False, error="드론을 선택해주세요."), 400
    if not isinstance(items, list) or not items:
        return jsonify(ok=False, error="점검 항목 데이터가 없습니다."), 400

    gps = data.get("gps") or {}
    sun = data.get("sunInfo") or {}

    ok_count = sum(1 for it in items if it.get("state") == "ok")
    bad_count = sum(1 for it in items if it.get("state") == "bad")
    verdict = "비행가능" if bad_count == 0 else "비행보류"

    conn = get_db()
    cur = conn.execute(
        """
        INSERT INTO reports
            (created_at, client_ts, drone, lat, lng, gps_accuracy,
             sunrise_min, sunset_min, is_daylight,
             ok_count, bad_count, verdict, items_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            datetime.utcnow().isoformat(timespec="seconds") + "Z",
            data.get("ts"),
            drone,
            gps.get("lat"),
            gps.get("lng"),
            gps.get("acc"),
            sun.get("sunrise"),
            sun.get("sunset"),
            1 if sun.get("isDaylight") else (0 if "isDaylight" in sun else None),
            ok_count,
            bad_count,
            verdict,
            json.dumps(items, ensure_ascii=False),
        ),
    )
    conn.commit()
    return jsonify(ok=True, id=cur.lastrowid, verdict=verdict), 201


@app.route("/api/reports", methods=["GET"])
def list_reports():
    """저장된 점검 기록 목록 (최신순, 최대 200건)."""
    conn = get_db()
    rows = conn.execute(
        """
        SELECT id, created_at, client_ts, drone, lat, lng,
               ok_count, bad_count, verdict
        FROM reports ORDER BY id DESC LIMIT 200
        """
    ).fetchall()
    return jsonify(ok=True, reports=[dict(r) for r in rows])


@app.route("/api/reports/<int:report_id>", methods=["GET"])
def get_report(report_id):
    """저장된 점검 기록 상세(항목별 결과 포함)."""
    conn = get_db()
    row = conn.execute("SELECT * FROM reports WHERE id = ?", (report_id,)).fetchone()
    if row is None:
        return jsonify(ok=False, error="기록을 찾을 수 없습니다."), 404
    result = dict(row)
    result["items"] = json.loads(result.pop("items_json"))
    return jsonify(ok=True, report=result)


@app.route("/reports")
def reports_page():
    """점검 기록 조회 화면 (담당자용)."""
    return render_template("reports.html")


init_db()

if __name__ == "__main__":
    # 개발용 실행. 운영 배포는 run_server.py(waitress) 를 사용한다.
    app.run(host="0.0.0.0", port=8000, debug=True)
