#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт для сбора содержимого файлов в репозитории.
Результат сохраняется в файле collected_code.txt.

В начале файла можно задать:
- glob-шаблоны имён файлов для игнорирования (ignore_file_patterns)
- glob-шаблоны директорий для игнорирования (ignore_dir_patterns)
- glob-шаблоны относительных путей для игнорирования (ignore_path_patterns)
- glob-шаблоны имён файлов для включения (include_file_patterns)
"""

import os
import fnmatch
import unicodedata

def _norm(s: str) -> str:
    """NFC-нормализация: буквы вроде 'й' сравниваются корректно
    при разных внутренних кодировках."""
    return unicodedata.normalize("NFC", s)


# Имя итогового файла
output_filename = "collected_code.txt"

# Определяем путь и имя скрипта, чтобы всегда игнорировать его сам
script_path = os.path.abspath(__file__)
script_name = os.path.basename(script_path)

# Шаблоны имён файлов для игнорирования (с учётом регистра для имён)
ignore_file_patterns = {
    script_name,          # сам этот скрипт (строгое соответствие)
    "TEST.py",           # строгое соответствие
    "*_old*.py",         # строчное соответствие
    "*.pyc",             # расширения игнорировать без учёта регистра
    "*.pyo","*.txt","*.md","*.pyc","*.pyo","*.log","*.ini","*.png","*.jpg","*.gif",
    "*.svg","*.pdf","*.zip","*.rar","*.tar","*.gz","*.bz2", "*.7z", "*.exe",
    "*.jpeg","*.js","*.min.js",
    "*.bin", "*.ipynb", "*.csv", "*.xls",
    "*.xlsx",
    "*.ppt",
    "*.pptx",
    "build_image.sh",
    "Collected_Code_Script.py",
    "docker-compose.override.yml",
    "langgraph_rag_demo.py",
    "service.yaml",
}


# Шаблоны имён файлов для игнорирования (с учётом регистра для имён)
ignore_file_patterns = { script_name,
    "*.pyc", "*.pyo", "*.txt", "*.md", "*.log", "*.ini", "*.png", "*.jpg", "*.gif", "*.svg", "*.pdf", "*.zip",
    "*.rar", "*.tar", "*.gz", "*.bz2", "*.7z", "*.exe", "*.jpeg", "*.js", "*.min.js", "*.bin", "*.ipynb",
    "*.csv", "*.xls", "*.xlsx", "*.ppt", "*.pptx",
    "TEST.py", "*_old*.py", "build_image.sh", "Collected_Code_Script.py","Collected_Code_Script-v2.py","Collected_Code_Script.sh",
    "docker-compose.override.yml", "langgraph_rag_demo.py", "service.yaml",}

# Шаблоны имён директорий для игнорирования
ignore_dir_patterns = {"__pycache__", "venv", "env", ".venv", "build", "dist", ".pytest_cache",
                       ".git", ".idea", "docs", "docs_",
                       "time-bot", "ПРЕЗЕНТАЦИЯ",
                       "tmp",
                       "утилита-парсит проект со структурой и кодом",
                       "backend_fallback",
                       "frontend"}

# Шаблоны относительных путей для игнорирования (glob по rel_path)
ignore_path_patterns = {"backend/app/categories_config.yaml",
                        "backend_fallback/categories_config.yaml",}

# Шаблоны имён файлов для включения
include_file_patterns = {"*.py", "*.go", "*.yml", "Dockerfile"
    # можно добавить другие относительные пути, например 'frontend/Dockerfile'
}


# Разделяем шаблоны на чувствительные и нечувствительные к регистру расширения
case_sensitive_file_patterns = {pat for pat in ignore_file_patterns if not pat.startswith("*.")}
case_insensitive_file_patterns = {pat for pat in ignore_file_patterns if pat.startswith("*.")}


def should_ignore_file(filename):
    # проверяем точные (чувствительные) шаблоны
    for pat in case_sensitive_file_patterns:
        if fnmatch.fnmatch(filename, pat):
            return True
    # расширения без учёта регистра
    lower = filename.lower()
    for pat in case_insensitive_file_patterns:
        if fnmatch.fnmatch(lower, pat.lower()):
            return True
    return False


def should_ignore_path(rel_path):
    # относительные пути
    for pat in ignore_path_patterns:
        if fnmatch.fnmatch(rel_path, pat):
            return True
    return False


def build_project_tree():
    """Генерирует строковую схему проекта, исключая игнорируемые файлы и папки."""
    lines = ["Структура проекта:", ""]

    def walk(dir_path, prefix):
        entries = sorted(os.listdir(dir_path))
        for e in entries:
            path = os.path.join(dir_path, e)
            rel = os.path.relpath(path, '.')
            is_dir = os.path.isdir(path)
            # пропуски: скрытые, директории, файлы, скрипт, пути
            if e.startswith('.'):
                continue
            if is_dir and any(fnmatch.fnmatch(_norm(e), _norm(pat)) for pat in ignore_dir_patterns):
                continue
            if not is_dir and (should_ignore_file(e) or should_ignore_path(rel)):
                continue
            if os.path.abspath(path) == script_path:
                continue
            # вывод
            is_last = e == entries[-1]
            connector = "└─" if is_last else "├─"
            display = e + ("/" if is_dir else "")
            lines.append(f"{prefix}{connector} {display}")
            if is_dir:
                extension = "   " if is_last else "│  "
                walk(path, prefix + extension)

    # обход корня — с коннекторами на самом корне
    entries = sorted(os.listdir('.'))
    for idx, e in enumerate(entries):
        path = os.path.join('.', e)
        rel = os.path.relpath(path, '.')
        is_dir = os.path.isdir(path)
        # пропуски: скрытые, игнорируемые
        if e.startswith('.'):
            continue
        if is_dir and any(
                fnmatch.fnmatch(_norm(e), _norm(pat)) for pat in
                ignore_dir_patterns):
            continue
        if not is_dir and (should_ignore_file(e) or should_ignore_path(rel)):
            continue
        # выбираем коннектор
        connector = "└─" if idx == len(entries) - 1 else "├─"
        display = e + ('/' if is_dir else '')
        lines.append(f"{connector} {display}")
        if is_dir:
            ext = "   " if idx == len(entries) - 1 else "│  "
            walk(path, prefix=ext)
    return lines


# основная запись
with open(output_filename, "w", encoding="utf-8") as out_file:
    # схема проекта
    for line in build_project_tree():
        out_file.write(line + "\n")
    out_file.write("\n-----------------------------------------------------------\n\n")

    # обход файлов
    for root, dirs, files in os.walk('.'):
        dirs[:] = [
            d for d in dirs
            if not d.startswith('.')
               and not any(fnmatch.fnmatch(_norm(d), _norm(pat)) for pat in
                           ignore_dir_patterns)
        ]

        for filename in files:
            file_path = os.path.join(root, filename)
            rel = os.path.relpath(file_path, '.')
            # пропуски: скрипт, скрытые, шаблоны файлов, пути, включение
            if os.path.abspath(file_path) == script_path:
                continue
            if filename.startswith('.'):
                continue
            if should_ignore_file(filename) or should_ignore_path(rel):
                continue
            if not any(fnmatch.fnmatch(filename, pat) for pat in include_file_patterns):
                continue
            # запись
            out_file.write(f"--- Мой файл {rel} имеет такое содержание: \n\n")
            with open(file_path, 'r', encoding='utf-8') as f:
                out_file.write(f.read())
            out_file.write("\n\n-----------------------------------------------------------\n\n")

print(f"Сбор кода завершён. Результаты в файле {output_filename}")
