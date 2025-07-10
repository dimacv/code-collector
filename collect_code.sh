#!/usr/bin/env bash
set -euo pipefail

# ─────────────────────────────────────────────────────────────
#  Collected_Code_Script.sh
#  Сохраняет структуру проекта + содержимое файлов
#  в формате, идентичном Collected_Code_Script.py
# ─────────────────────────────────────────────────────────────

# Итоговый файл
output_file="collected_code(sh).txt"

# ──────────────────────────── правила фильтрации ──────────────────────
# 1. Файлы, которые надо пропустить (glob-шаблоны, регистр игнорируется
#    для паттернов с «*» в начале ─ *.pyc, *.jpg …)
ignore_file_patterns=(
  "TEST.py" "*_old*.py"
  "*.pyc" "*.pyo" "*.txt" "*.md" "*.log" "*.ini"
  "*.png" "*.jpg" "*.jpeg" "*.gif" "*.svg" "*.pdf"
  "*.zip" "*.rar" "*.tar" "*.gz" "*.bz2" "*.7z"
  "*.exe" "*.js" "*.min.js" "*.bin" "*.ipynb" "*.csv"
  "*.xls" "*.xlsx" "*.ppt" "*.pptx"
  "build_image.sh"
  "Collected_Code_Script.py" "Collected_Code_Script-v2.py" "Collected_Code_Script.sh"
  "docker-compose.override.yml" "langgraph_rag_demo.py" "service.yaml"
)

# 2. Директории, которые не должны попадать в дерево / поиск
ignore_dir_patterns=(
  "__pycache__" "venv" "env" ".venv" "build" "dist" ".pytest_cache"
  ".git" ".idea" "docs" "docs_"
  "time-bot" "ПРЕЗЕНТАЦИЯ" "tmp"
  "*утилита-парсит проект со структуро*кодом*"
)

# 3. Точные (относительные) пути к файлам, которые пропускаем
ignore_path_patterns=(
  "backend/app/categories_config.yaml"
  "backend_fallback/categories_config.yaml"
)

# 4. Файлы, которые мы **хотим** видеть в выводе
include_file_patterns=(
  "*.py" "*.go" "*.yml" "*.yaml" "Dockerfile"
)

# ────────────────────────── полезные вспомогалки ─────────────────────
script_path="$(cd "$(dirname "$0")" && pwd)/$(basename "$0")"

should_ignore_file() {
  # $1 = base-name, $2 = rel-path
  local name="$1" rel="$2"

  # скрытые файлы
  [[ "$name" == .* ]] && return 0

  # точные относительные пути
  for pat in "${ignore_path_patterns[@]}"; do
    [[ "$rel" == "$pat" ]] && return 0
  done

  # шаблоны «что игнорировать»
  shopt -s nocasematch
  for pat in "${ignore_file_patterns[@]}"; do
    [[ "$name" == $pat ]] && { shopt -u nocasematch; return 0; }
  done
  shopt -u nocasematch

  # если **совпало** с include → НЕ игнорируем
  for pat in "${include_file_patterns[@]}"; do
    [[ "$name" == $pat ]] && return 1
  done
  # иначе игнор
  return 0
}

print_tree() {
  # $1 = dir, $2 = prefix
  local dir="$1" prefix="$2"

  local entries=()
  for itm in "$dir"/*; do entries+=("$(basename "$itm")"); done
  IFS=$'\n' entries=($(printf "%s\n" "${entries[@]}" | sort)); unset IFS
  local count=${#entries[@]}

  for idx in "${!entries[@]}"; do
    local name="${entries[idx]}"
    local path="$dir/$name" rel="${path#./}"

    # пропуск скрытых / игнор-директорий / игнор-файлов
    [[ "$name" == .* ]] && continue
    for pat in "${ignore_dir_patterns[@]}"; do
        shopt -s nocasematch
        [[ $name == $pat ]] && { shopt -u nocasematch; continue 2; }
        shopt -u nocasematch
    done

    [[ -f "$path" ]] && should_ignore_file "$name" "$rel" && continue

    local connector="├─"; [[ $idx -eq $((count-1)) ]] && connector="└─"
    if [[ -d "$path" ]]; then
      printf "%s%s %s/\n" "$prefix" "$connector" "$name"
      local new_prefix="$prefix"; [[ $idx -eq $((count-1)) ]] && new_prefix+="   " || new_prefix+="│  "
      print_tree "$path" "$new_prefix"
    else
      printf "%s%s %s\n" "$prefix" "$connector" "$name"
    fi
  done
}

# ───────────────────────────── запись файла ───────────────────────────
: > "$output_file"
{
  echo -e "Структура проекта:\n"

  # root-обход: выводим каждый элемент с «├─ / └─» у корня
  print_tree "." ""
  echo -e "\n-----------------------------------------------------------\n"
} >> "$output_file"

# ────────────────── обход файлов через find + prune ───────────────────
prune_args=()
for pat in "${ignore_dir_patterns[@]}";  do
    prune_args+=( -iname "$pat" -o )
done
for pat in "${ignore_path_patterns[@]}"; do prune_args+=( -path "./$pat" -o ); done
unset 'prune_args[${#prune_args[@]}-1]'        # убираем последний «-o»

while IFS= read -r -d '' file; do
  rel="${file#./}"; base="$(basename "$file")"

  # пропускаем сам скрипт + скрытые + игнор-файлы
  [[ "$file" = "$script_path" ]] && continue
  [[ "$base" == .* ]] && continue
  should_ignore_file "$base" "$rel" && continue

  # содержимое
  {
    echo -e "--- Мой файл $rel имеет такое содержание:\n"
    cat "$file"
    echo -e "\n\n-----------------------------------------------------------\n"
  } >> "$output_file"
done < <(find . \( "${prune_args[@]}" \) -prune -o -type f -print0)

echo "Сбор кода завершён. Результаты в файле $output_file"
