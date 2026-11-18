% hcmut-report.cls — HCMUT report class
% Based on https://github.com/hoang-himself/hcmut-report (LPPL 1.3c, see LICENSE.txt),
% adapted from a CO3037 (IoT) report for CO3085 Natural Language Processing:
% cover page, header and footer are now driven by the configuration macros below
% instead of hard-coded course text.
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{hcmut-report}[2026/11/18 HCMUT report, CO3085 edition]

\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions\relax
\LoadClass[12pt,a4paper]{article}

\RequirePackage[utf8]{vntex,inputenc}
\RequirePackage{anyfontsize,amsmath,amssymb}
\RequirePackage[T5]{fontenc}

\RequirePackage{array,lastpage}
\RequirePackage{geometry,graphicx,indentfirst,setspace}
\RequirePackage{booktabs}
\RequirePackage[center]{caption}
\RequirePackage{xcolor}

% url (loaded by hyperref) keeps spaces in \code{...} and may break lines there
\PassOptionsToPackage{obeyspaces,spaces}{url}
\RequirePackage{fancyhdr,hyperref}
\RequirePackage[square,numbers,sort]{natbib}

\RequirePackage[vietnamese]{babel}
\addto\captionsvietnamese{\renewcommand{\refname}{Tài liệu tham khảo}}

% ---------------------------------------------------------------- configuration
\newcommand{\@upperuniname}{Đại học Quốc gia Thành phố Hồ Chí Minh}
\newcommand{\@uniname}{Trường Đại học Bách Khoa}

\newcommand{\@deptname}{Khoa Khoa học và Kỹ thuật Máy tính}
\newcommand{\deptname}[1]{\renewcommand{\@deptname}{#1}}

\newcommand{\@coursename}{Course name}
\newcommand{\coursename}[1]{\renewcommand{\@coursename}{#1}}

\newcommand{\@coursecode}{COxxxx}
\newcommand{\coursecode}[1]{\renewcommand{\@coursecode}{#1}}

\newcommand{\@semester}{HKxxx}
\newcommand{\semester}[1]{\renewcommand{\@semester}{#1}}

\newcommand{\@reporttype}{Báo cáo bài tập lớn}
\newcommand{\reporttype}[1]{\renewcommand{\@reporttype}{#1}}

\renewcommand{\@title}{Report title}
\newcommand{\@subtitle}{}
\newcommand{\subtitle}[1]{\renewcommand{\@subtitle}{#1}}

\newcommand{\@advisor}{Advisor}
\newcommand{\advisor}[1]{\renewcommand{\@advisor}{#1}}

\newcommand{\@class}{L01}
\newcommand{\class}[1]{\renewcommand{\@class}{#1}}

\newcommand{\@reportplace}{TP. Hồ Chí Minh}
\newcommand{\reportplace}[1]{\renewcommand{\@reportplace}{#1}}

\newcommand{\@reporttime}{Tháng 11/2026}
\newcommand{\reporttime}[1]{\renewcommand{\@reporttime}{#1}}

% \addmember{Full name}{Student ID}: one row of the cover-page member table.
\newcounter{memberrowno}
\newcommand{\@members}{}
\newcommand{\addmember}[2]{%
  \g@addto@macro\@members{\stepcounter{memberrowno}\arabic{memberrowno} & #1 & #2 & \@class \\ \hline}}

% ---------------------------------------------------------------- page layout
\geometry{
  paper=a4paper,
  left=3cm,
  right=2cm,
  vmargin=2cm,
  includeheadfoot=true,
  headheight=35.45059pt
}

\onehalfspacing
\raggedbottom
\renewcommand{\arraystretch}{1.2}

\setcounter{secnumdepth}{3}
\setcounter{tocdepth}{2}

% Floats: allow larger floats in text pages; float-only pages start at the top
\renewcommand{\topfraction}{0.85}
\renewcommand{\bottomfraction}{0.6}
\renewcommand{\textfraction}{0.12}
\renewcommand{\floatpagefraction}{0.7}
\setlength{\@fptop}{0pt}
\setlength{\@fpsep}{14pt plus 4pt}
\setlength{\@fpbot}{0pt plus 1fil}

\AtBeginDocument{\counterwithin{equation}{section}}
\AtBeginDocument{\counterwithin{table}{section}}
\AtBeginDocument{\counterwithin{figure}{section}}

\hypersetup{
  colorlinks=true,
  linkcolor=black,
  citecolor=blue!60!black,
  urlcolor=blue
}

\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0.3pt}
\renewcommand{\footrulewidth}{0.3pt}

\fancyhead[L]{%
  \bfseries
  \begin{tabular}{rl}
    \begin{picture}(25pt,15pt)
      \put(0,-8pt){\includegraphics[width=20pt]{graphics/hcmut.png}}
    \end{picture}
    \begin{tabular}{l}
      \ttfamily\MakeUppercase{\@uniname} \\
      \ttfamily\MakeUppercase{\@deptname} \\
    \end{tabular}
  \end{tabular}%
}
\fancyfoot[L]{\scriptsize\ttfamily \@coursename\ (\@coursecode) -- \@semester}
\fancyfoot[R]{\scriptsize\ttfamily Trang {\thepage}/\pageref{LastPage}}

% ---------------------------------------------------------------- cover page
\newcommand{\coverpage}{%
  \thispagestyle{empty}
  \vspace*{-3\baselineskip}
  \begin{center}
    \MakeUppercase{\@upperuniname}

    \MakeUppercase{\@uniname}

    \textbf{\MakeUppercase{\@deptname}}
    \vfill
    \includegraphics[scale=0.4]{graphics/hcmut.png}
    \vfill
    \bfseries
    \begin{tabular}{c}
      \Large \MakeUppercase{\@coursename} \\
      \Large (\@coursecode) \\
      {} \\
      \midrule \\
      \Large \MakeUppercase{\@reporttype} \\[4pt]
      \LARGE \@title \\[2pt]
      \large\mdseries \@subtitle \\
      {} \\
      \bottomrule
    \end{tabular}
    \vfill
    \mdseries
    \textbf{Giảng viên hướng dẫn: \@advisor} \\
    \textbf{Lớp: \@class\ -- \@semester} \\
    \vfill
    \begin{minipage}{\linewidth}
      \centering
      \renewcommand{\arraystretch}{1.6}
      \setcounter{memberrowno}{0}
      \begin{tabular}{|>{\centering\arraybackslash}m{1.4cm}|>{\centering\arraybackslash}m{6cm}|>{\centering\arraybackslash}m{3cm}|>{\centering\arraybackslash}m{2cm}|}
        \hline
        \textbf{STT} & \textbf{Họ và tên} & \textbf{MSSV} & \textbf{Lớp} \\ \hline
        \@members
      \end{tabular}
    \end{minipage}
    \vfill
    \MakeUppercase{\@reportplace, \@reporttime}
  \end{center}
  \clearpage
}
