import csv
import json
import sys
from pathlib import Path

max_int = sys.maxsize
while True:
    try:
        csv.field_size_limit(max_int)
        break
    except OverflowError:
        max_int = int(max_int / 10)

RAW_DIR = Path("raw_data")
OUTPUT_DIR = Path("data")
OUTPUT_FILE = OUTPUT_DIR / "corpus.jsonl"

CONTENT_FIELDS = ("content", "text", "article", "body", "article_content")
TITLE_FIELDS = ("title", "headline", "news_title")
URL_FIELDS = ("link", "url", "article_url")

def extract_field(row: dict, candidates: tuple) -> str:
    for field in candidates:
        val = row.get(field)
        if val and isinstance(val, str) and val.strip():
            return val.strip()
    return ""

def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    doc_id = 0
    total_bytes = 0
    seen_urls = set()

    csv_files = sorted(RAW_DIR.glob("*.csv"))
    if not csv_files:
        print(f"Помилка: у {RAW_DIR} не знайдено жодного .csv файлу!")
        return

    with OUTPUT_FILE.open("w", encoding="utf-8") as out_f:
        for csv_path in csv_files:
            print(f"Обробка: {csv_path.name}...")
            with csv_path.open("r", encoding="utf-8", errors="replace") as in_f:
                reader = csv.DictReader(in_f)
                for row in reader:
                    content = extract_field(row, CONTENT_FIELDS)
                    if not content or len(content) < 50:
                        continue

                    url = extract_field(row, URL_FIELDS)
                    if url:
                        if url in seen_urls:
                            continue
                        seen_urls.add(url)

                    title = extract_field(row, TITLE_FIELDS)
                    doc_path = url or f"{csv_path.stem}_{doc_id}"

                    full_text = f"{title}\n\n{content}" if title else content

                    doc = {
                        "doc_id": doc_id,
                        "path": doc_path,
                        "text": full_text
                    }

                    line = json.dumps(doc, ensure_ascii=False) + "\n"
                    out_f.write(line)
                    total_bytes += len(line.encode("utf-8"))
                    doc_id += 1

    mb_size = total_bytes / (1024 * 1024)
    print("--- Успішно завершено ---")
    print(f"Створено документів : {doc_id}")
    print(f"Підсумковий розмір : {mb_size:.2f} MB")
    print(f"Файл збережено в   : {OUTPUT_FILE}")

if __name__ == "__main__":
    main()