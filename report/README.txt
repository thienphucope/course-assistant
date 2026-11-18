CO3085 Course Assistant — báo cáo LaTeX
=======================================

Build (pdflatex, chạy 2 lần để có mục lục, tham chiếu và "Trang x/y"):

    pdflatex report.tex
    pdflatex report.tex

Không cần -shell-escape hay Pygments (minted đã được thay bằng fvextra).
Trên máy nhóm: MiKTeX portable tại D:\Documents\261\4041\.miktex
(texmfs\install\miktex\bin\x64\pdflatex.exe). Overleaf: upload cả thư mục, compiler pdfLaTeX.

Cấu trúc
- report.tex          preamble, thông tin bìa (môn, GV, lớp, \addmember), danh sách chương
- chapters/*.tex      nội dung, một file mỗi mục
- hcmut-report.cls    class: bìa, header/footer theo tham số
- codespace.sty       khối trace/grammar (fvextra), \code{} cho định danh ASCII
- graphics/hcmut.png  logo

Số liệu trong báo cáo lấy từ src/output/ (evaluation.txt, dialogue.txt, ...) và
docs/validation/grammar-check.json; chạy lại `python src/run.py all` nếu code/grammar đổi.

Template gốc
Repository: https://github.com/hoang-himself/hcmut-report
Commit: 350906b86be7adae1c953217029cbe12ad4f6ac5 refactor: update `listings` styles
License: LPPL 1.3c (LICENSE.txt). Đã chỉnh class/sty cho môn CO3085.
