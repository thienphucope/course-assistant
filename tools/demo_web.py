"""Serve the live Course Assistant demo on localhost using Python alone."""

import argparse
from collections import OrderedDict
from dataclasses import asdict, replace
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sys
from threading import Lock, Timer
from uuid import uuid4
import webbrowser

from demo import SCENES
from hcmut.iaslab.nlp.app.dialogue import DialogueContext
from hcmut.iaslab.nlp.app.paths import PATHS
from hcmut.iaslab.nlp.app.pipeline import CourseAssistant


DEMO_DIR = Path(__file__).resolve().with_name("demo_web")
STATIC_ASSETS = {
    "/": ("index.html", "text/html"),
    "/style.css": ("style.css", "text/css"),
    "/app.js": ("app.js", "text/javascript"),
}
EXAMPLES = (
    ("Số tín chỉ", SCENES["credits"][0]),
    ("Lịch học tuần 3", SCENES["dialogue"][0]),
    ("Hỏi tiếp về parsing", SCENES["dialogue"][1]),
    ("Thiếu dữ kiện trong KB", SCENES["missing-kb"][0]),
    ("Câu hỏi ngoài miền", SCENES["out-of-scope"][0]),
    ("Cách diễn đạt văn phạm chưa phủ", SCENES["grammar-gap"][0]),
)


class DemoServer(ThreadingHTTPServer):
    def __init__(self, port: int):
        assistant = CourseAssistant.from_paths(PATHS)
        self.components = assistant.components
        self.sessions: OrderedDict[str, DialogueContext] = OrderedDict()
        self.lock = Lock()
        super().__init__(("127.0.0.1", port), DemoHandler)

    def analyze(self, question: str, session: str | None) -> dict | None:
        with self.lock:
            if session is None:
                session = uuid4().hex
                if len(self.sessions) >= 32:
                    self.sessions.popitem(last=False)
                self.sessions[session] = DialogueContext()
            context = self.sessions.get(session)
            if context is None:
                return None
            self.sessions.move_to_end(session)
            assistant = CourseAssistant(replace(self.components, context=context))
            before = asdict(context)
            result = assistant.process(question)
            after = asdict(context)

        query = asdict(result.query)
        status = "FOUND" if result.query.found else "NOT_FOUND"
        if result.query.query == "NO_QUERY":
            status = "SKIPPED"
        return {
            "session": session,
            "question": result.sentence,
            "tokens": result.parse.tokens,
            "parse": {
                "accepted": result.parse.accepted,
                "tree": asdict(result.parse.tree) if result.parse.tree else None,
                "bracketed": result.parse.output(),
            },
            "semantic": {**asdict(result.raw_semantic), "predicate": result.raw_semantic.predicate},
            "context": {
                "used": result.context_used,
                "before": before,
                "after": after,
                "resolved": {**asdict(result.semantic), "predicate": result.semantic.predicate},
            },
            "query": {**query, "status": status},
            "answer": result.answer,
        }


class DemoHandler(BaseHTTPRequestHandler):
    server: DemoServer

    def do_GET(self):
        if self.path == "/api/examples":
            self.send_json([
                {"label": label, "question": question} for label, question in EXAMPLES
            ])
        elif self.path in STATIC_ASSETS:
            filename, content_type = STATIC_ASSETS[self.path]
            self.send_content(HTTPStatus.OK, content_type, (DEMO_DIR / filename).read_bytes())
        else:
            self.send_json({"error": "Không tìm thấy trang này."}, HTTPStatus.NOT_FOUND)

    def do_POST(self):
        if self.path != "/api/analyze":
            self.send_json({"error": "Không tìm thấy trang này."}, HTTPStatus.NOT_FOUND)
            return
        if self.headers.get_content_type() != "application/json":
            self.send_json({"error": "Yêu cầu dữ liệu JSON."}, HTTPStatus.UNSUPPORTED_MEDIA_TYPE)
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 8192:
                raise ValueError
            data = json.loads(self.rfile.read(size))
            if not isinstance(data, dict):
                raise ValueError
            question = data.get("question")
            session = data.get("session")
            if not isinstance(question, str) or not question.strip():
                raise ValueError
            if session is not None and not isinstance(session, str):
                raise ValueError
        except ValueError:
            self.send_json({"error": "Hãy nhập một câu hỏi hợp lệ."}, HTTPStatus.BAD_REQUEST)
            return
        result = self.server.analyze(question.strip(), session)
        if result is None:
            self.send_json({"error": "Phiên đã hết. Chọn Phiên mới rồi gửi lại câu hỏi."},
                           HTTPStatus.CONFLICT)
            return
        self.send_json(result)

    def send_json(self, payload, status=HTTPStatus.OK):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_content(status, "application/json", body)

    def send_content(self, status, content_type, body):
        self.send_response(status)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765, help="localhost port (default: 8765)")
    parser.add_argument("--open", action="store_true", help="open the demo in your browser")
    args = parser.parse_args()
    try:
        server = DemoServer(args.port)
    except (OSError, OverflowError) as error:
        parser.exit(1, f"Không mở được cổng {args.port}: {error}\n")

    with server:
        url = f"http://127.0.0.1:{server.server_port}/"
        print(f"Course Assistant Demo: {url}", flush=True)
        if args.open:
            Timer(0.1, webbrowser.open, args=(url,)).start()
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            sys.stdout.write("\nĐã dừng demo.\n")


if __name__ == "__main__":
    main()
