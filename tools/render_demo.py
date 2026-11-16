"""Render a captioned, silent demo from live pipeline traces.

Development-only dependencies: Pillow and ffmpeg (not needed by the assistant).
This is an automated replay of actual results, not a screen recording.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from demo import QUESTIONS
from hcmut.iaslab.nlp.app.pipeline import CourseAssistant
from hcmut.iaslab.nlp.app.evaluate import evaluate_cases, load_evaluation_cases

REPO = Path(__file__).resolve().parents[1]


def wrap(text, font, width):
    lines = []
    for paragraph in text.splitlines():
        line = ""
        for word in paragraph.split():
            candidate = f"{line} {word}".strip()
            if line and font.getlength(candidate) > width:
                lines.append(line)
                line = word
            else:
                line = candidate
        lines.append(line)
    return lines


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=REPO / "dist/course-assistant-demo.mp4")
    parser.add_argument("--font", type=Path, default=Path("C:/Windows/Fonts/segoeui.ttf"))
    parser.add_argument("--mono-font", type=Path, default=Path("C:/Windows/Fonts/consola.ttf"))
    args = parser.parse_args()
    if not shutil.which("ffmpeg"):
        parser.error("ffmpeg is required")
    if not args.font.is_file() or not args.mono_font.is_file():
        parser.error("provide font files supporting Vietnamese via --font and --mono-font")
    assistant = CourseAssistant.from_root(REPO / "src")
    results = [assistant.process(question) for question in QUESTIONS]
    scaffolding = REPO / "src/data/scaffolding"
    official = evaluate_cases(assistant, load_evaluation_cases(scaffolding / "sample_queries.txt"))
    challenge = evaluate_cases(assistant, load_evaluation_cases(scaffolding / "challenge_queries.txt"))
    scenes = [(8, "Trợ lý hỏi đáp môn học · Classical NLP",
               "CO3085 | COURSE ASSISTANT\n\n"
               "Input → Tokenizer → CFG / Earley → Tree\n"
               "→ Semantic / Entity → Context → Query / KB → Answer\n\n"
               "Runtime: Python, thư viện chuẩn, chạy offline.\n"
               "Dữ kiện: 6 file KB do giảng viên cung cấp.\n\n"
               "Video phát lại kết quả thực thi bằng code của nhóm.\n"
               "Phụ đề thay lời thuyết minh; thông tin thành viên bổ sung sau.",
               "Phần I: cú pháp · Phần II: hỏi đáp · Phần III: ngữ cảnh · Phần IV: đánh giá")]
    titles = ["01 · Từ câu hỏi tới dữ kiện", "02 · Parser và cây cú pháp", "03 · Giải tham chiếu trong cùng phiên",
              "04 · Tính năng BTL qua nhãn FEAT", "05 · Alias quy định", "06 · Có cây nhưng KB thiếu dữ kiện",
              "07 · Câu ngoài miền"]
    captions = ["Intent và slot tạo query; answer dùng dữ kiện có nguồn.",
                "Parser nhận hết token; node ε vẫn có mặt trong cây.",
                "Câu trước lưu CH03. Resolver dùng chương gần nhất, giữ frame gốc để giải thích.",
                "FEAT_PARSING xác định PART_I; semantic giữ feature=parse tree.",
                "Alias 'thư viện có sẵn' ánh xạ EXTERNAL_LIBRARIES.",
                "Không có thông tin giảng viên trong KB: trả NOT_FOUND, không tự điền tên.",
                "Cây () và UNKNOWN: câu hỏi nằm ngoài văn phạm/miền dữ liệu."]
    durations = [14, 18, 18, 16, 12, 16, 12]
    for index, result in enumerate(results):
        body = f"INPUT: {result.sentence}\n\n"
        if index in (1, 3, 5, 6):
            body += f"PARSE: {result.parse.output()}\n\n"
        if index == 0:
            body += f"TOKENS: {' / '.join(result.parse.tokens)}\n\n"
        body += f"SEMANTIC: {result.raw_semantic.predicate}\n"
        if result.context_used:
            body += f"CONTEXT: {result.context_used}\nRESOLVED: {result.semantic.predicate}\n"
        body += f"\nQUERY: {result.query.query}\n"
        body += f"STATUS: {'FOUND' if result.query.found else 'NOT_FOUND'}\n"
        body += f"SOURCE: {', '.join(result.query.sources) or '-'}\n\nANSWER: {result.answer}"
        scenes.append((durations[index], titles[index], body, captions[index]))
    scenes.append((14, "08 · Đánh giá và sản phẩm",
                   f"Bộ đề: {official.joint_correct}/{official.total} câu đúng end-to-end.\n"
                   f"Challenge: {challenge.joint_correct}/{challenge.total} câu đúng end-to-end.\n\n"
                   "C007: chưa có mẫu hỏi số buổi học mỗi tuần.\n"
                   "C008: chưa nhận 'tuần thứ ba'.\n\n"
                   "python run.py all → 9 file trong output/\n"
                   "Cây / semantic / intent-entity / query / answer\n"
                   "grammar / samples / dialogue / evaluation\n\n"
                   "Các bộ đã dùng trong phát triển; chưa có tập đánh giá độc lập.\n"
                   "README và báo cáo nêu hạn chế, nguồn tham khảo và sử dụng AI.",
                   "Kiểm chứng Docker còn chờ môi trường có Docker. Các số liệu trên lấy từ lần chạy tạo video."))
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    frames = output.parent / "demo-frames"
    frames.mkdir(exist_ok=True)
    heading_font = ImageFont.truetype(str(args.font), 32)
    label_font = ImageFont.truetype(str(args.font), 19)
    caption_font = ImageFont.truetype(str(args.font), 20)
    for index, (duration, title, body, caption) in enumerate(scenes):
        canvas = Image.new("RGB", (1280, 720), "#0b1220")
        draw = ImageDraw.Draw(canvas)
        draw.text((48, 24), "CO3085 / COURSE ASSISTANT", font=label_font, fill="#69d8c7")
        draw.text((48, 61), title, font=heading_font, fill="#f1f5fa")
        draw.rounded_rectangle((40, 120, 1240, 635), radius=18, fill="#142137")
        for size in range(22, 16, -1):
            body_font = ImageFont.truetype(str(args.mono_font), size)
            lines = wrap(body, body_font, 1136)
            line_height = size + 7
            if len(lines) * line_height <= 475:
                break
        else:
            raise RuntimeError(f"Scene {index + 1} text overflows")
        for number, line in enumerate(lines):
            draw.text((70, 141 + number * line_height), line, font=body_font, fill="#e2eaf7")
        for number, line in enumerate(wrap(caption, caption_font, 1150)):
            draw.text((48, 650 + number * 26), line, font=caption_font, fill="#a9bed8")
        draw.rectangle((0, 712, int(1280 * (index + 1) / len(scenes)), 719), fill="#69d8c7")
        canvas.save(frames / f"scene-{index:02d}.png")
    timeline = frames / "timeline.txt"
    # Relative filenames avoid platform-specific escaping in ffmpeg concat files.
    timeline.write_text("".join(f"file 'scene-{index:02d}.png'\nduration {scene[0]}\n"
                                for index, scene in enumerate(scenes)) +
                        f"file 'scene-{len(scenes)-1:02d}.png'\n", encoding="utf-8", newline="\n")
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0",
                    "-i", str(timeline), "-vf", "fps=10,tpad=stop_mode=clone:stop_duration=3",
                    "-t", str(sum(scene[0] for scene in scenes)),
                    "-c:v", "libx264", "-preset", "medium", "-crf", "23", "-pix_fmt", "yuv420p",
                    "-movflags", "+faststart", "-an", str(output)], check=True)
    print(f"Rendered {len(scenes)} scenes, {sum(scene[0] for scene in scenes)} seconds: {output}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
