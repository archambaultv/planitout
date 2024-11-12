def beamer_template():
    tex = r'''
% Compile document with LuaLaTeX
\documentclass[aspectratio=169]{beamer}

\usepackage{fontspec}
\usepackage{unicode-math}
\setromanfont{Source Serif 4}
\setsansfont{Source Sans 3}
\setmonofont{Source Code Pro}
\setmathfont{Latin Modern Math}
\setmainfont{Source Sans 3}

\usepackage[french]{babel}
\usepackage[autostyle=true]{csquotes}
\usepackage{amsmath}
\usepackage{fontawesome5}
\usepackage{booktabs}
\usepackage{tikz}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
\usepackage{hyperref}
\usepackage[
    type={CC},
    modifier={by},
    version={4.0},
]{doclicense}

\usetheme{moloch}
\definecolor{bluegreen}{RGB}{3, 166, 155}
\setbeamercolor{frametitle}{bg=bluegreen}
\setbeamertemplate{section in toc}[sections numbered]

\title{Titre de la présentation}
\author{Vincent Archambault}
\date{}

\begin{document}

\maketitle

\begin{frame}
    \frametitle{Droit d'auteur}
    {\doclicenseThis}
\end{frame}

\begin{frame}
    \frametitle{Titre de la diapositive}
    \begin{itemize}
    \item Item 1
    \item Item 2
    \end{itemize}
\end{frame}

\end{document}
'''
    return tex.strip()
