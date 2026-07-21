# -*- coding: utf-8 -*-
"""
운영(Production) 실행 스크립트 - waitress WSGI 서버.

사내 서버에서:
    python run_server.py

리버스 프록시(예: IIS / Nginx / Apache) 뒤에 두고 HTTPS 를 종단하는 것을 권장한다.
※ 모바일 브라우저의 GPS(geolocation)는 보안 컨텍스트(HTTPS) 에서만 동작하므로
   외부 접속용 도메인은 반드시 HTTPS 로 노출해야 한다. (localhost 예외)
"""
from waitress import serve

from app import app

if __name__ == "__main__":
    # threads: 동시 접속자 수에 맞춰 조정
    serve(app, host="0.0.0.0", port=8000, threads=8)
