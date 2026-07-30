"""Build ccse.html from questions.json and template.html.

The data is checked before anything is written, so a bad edit fails here instead of
shipping silently. The most important check re-reads the answer key printed at the
back of the official manual and compares it against every answer in questions.json.

Usage: python3 build.py
"""

import hashlib
import json
import pathlib
import re
import subprocess
import sys
import unicodedata

ROOT = pathlib.Path(__file__).parent
QUESTIONS = ROOT / "questions.json"
TEMPLATE = ROOT / "template.html"
OUTPUT = ROOT / "ccse.html"
DATA_MARKER = "/*__DATA__*/"

TAREAS = (1, 2, 3, 4, 5)
LETTERS = "abc"

# The manual is not distributed with this repo. Point CCSE_MANUAL at your own copy,
# or drop it in one of these locations, to enable the answer key check.
MANUAL_ENV = "CCSE_MANUAL"
MANUAL_CANDIDATES = (
    "sources/manual-ccse-2026-def.pdf",
    "manual/manual-ccse-2026.pdf",
    "manual-ccse-2026.pdf",
)


def find_manual():
    from os import environ
    override = environ.get(MANUAL_ENV)
    if override:
        path = pathlib.Path(override).expanduser()
        return path if path.exists() else None
    for candidate in MANUAL_CANDIDATES:
        path = ROOT / candidate
        if path.exists():
            return path
    return None


class AnswerKeyUnavailable(Exception):
    """The manual is present but its answer key could not be read."""


def normalise(text):
    stripped = unicodedata.normalize("NFD", (text or "").lower())
    stripped = "".join(c for c in stripped if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", "", stripped)).strip()


def question_id(question):
    return hashlib.sha1(normalise(question).encode()).hexdigest()[:10]


def read_answer_key(pdf):
    """Parse the Soluciones pages: each line pairs a question number with a, b or c."""
    try:
        text = subprocess.run(
            ["pdftotext", "-layout", str(pdf), "-"],
            capture_output=True, text=True, check=True,
        ).stdout
    except FileNotFoundError:
        raise AnswerKeyUnavailable("pdftotext is not installed (brew install poppler)")
    except subprocess.CalledProcessError as exc:
        raise AnswerKeyUnavailable(f"pdftotext failed: {exc}") from exc
    pairs = re.findall(r"\b([1-5]\d{3})\s+([abc])\b", text)
    return {int(num): LETTERS.index(letter) for num, letter in pairs
            if 1001 <= int(num) <= 5999}


def check(questions):
    problems = []

    ids = [q["id"] for q in questions]
    if len(set(ids)) != len(ids):
        problems.append("duplicate question id")

    for q in questions:
        num = q["num"]
        if q["id"] != question_id(q["question"]):
            problems.append(f"{num}: id does not match its question text")
        if q["tarea"] not in TAREAS:
            problems.append(f"{num}: unknown tarea {q['tarea']}")
        if q["type"] not in ("tf", "mc"):
            problems.append(f"{num}: unknown type {q['type']}")
        if not 0 <= q["answer_index"] < len(q["options"]):
            problems.append(f"{num}: answer_index out of range")
        # a title is highlighted by matching it in the text, so it must occur there
        haystack = q["question"] + " " + " ".join(q["options"])
        for title in q.get("titles") or []:
            if title not in haystack:
                problems.append(f"{num}: title {title!r} does not appear in the question")

    manual = find_manual()
    if manual is None:
        # Not fatal: without the manual the answers simply go unverified.
        print(f"note: manual not found, skipping the answer key check "
              f"(set {MANUAL_ENV} to enable it)")
        return problems

    try:
        key = read_answer_key(manual)
    except AnswerKeyUnavailable as exc:
        problems.append(str(exc))
        return problems

    for q in questions:
        expected = key.get(q["num"])
        if expected is None:
            problems.append(f"{q['num']}: absent from the manual answer key")
        elif expected != q["answer_index"]:
            problems.append(
                f"{q['num']}: answer is {LETTERS[q['answer_index']]} "
                f"but the manual says {LETTERS[expected]}"
            )
    return problems


def main():
    questions = json.loads(QUESTIONS.read_text(encoding="utf8"))
    questions.sort(key=lambda q: q["num"])
    problems = check(questions)

    per_tarea = {t: sum(1 for q in questions if q["tarea"] == t) for t in TAREAS}
    print(f"questions       {len(questions)}  {per_tarea}")
    print(f"explained       {sum(1 for q in questions if q.get('explanation'))}")
    print(f"page reference  {sum(1 for q in questions if q.get('source_page'))}")

    if problems:
        print(f"\n{len(problems)} problem(s), nothing written:")
        for problem in problems[:25]:
            print(f"  {problem}")
        return 1

    template = TEMPLATE.read_text(encoding="utf8")
    if DATA_MARKER not in template:
        print(f"\n{TEMPLATE.name} has no {DATA_MARKER} placeholder")
        return 1

    data = json.dumps(questions, ensure_ascii=False, separators=(",", ":"))
    OUTPUT.write_text(template.replace(DATA_MARKER, data), encoding="utf8")
    print(f"\nwrote {OUTPUT.name} ({OUTPUT.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
