@echo off
rem Build the book: run xelatex twice for TOC and cross references.
cd /d "%~dp0"
xelatex -interaction=nonstopmode main.tex
xelatex -interaction=nonstopmode main.tex
echo.
echo Done. Output: main.pdf
