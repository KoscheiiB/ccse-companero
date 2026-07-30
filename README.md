# CCSE Compañero

A study companion for the CCSE, the constitutional and sociocultural knowledge test
you sit as part of applying for Spanish nationality.

## Why this exists

The official practice app is genuinely good, and I used it a lot. My problem was that
it tells you whether you got a question right and stops there. When I picked the wrong
answer I wanted to know *why* that answer was wrong, not just that it was, and when I
picked the right one I wanted to be sure I had picked it for the right reason rather
than by luck. Getting a green tick for a lucky guess teaches you nothing.

So this is the same 300 official questions, with an explanation attached to every one.
Each explanation says why the correct answer is correct, and separately why each of the
other options is wrong, because the wrong options are usually real things and knowing
what they actually are is itself worth learning. Where the fact comes from a specific
page of the official manual, the page number is shown so you can go and check it
instead of taking my word for it.

## What it is

One HTML file. No build step to run it, no dependencies, no server required, nothing to
install. Open `ccse.html` in a browser and it works, including offline.

That is deliberate. I wanted something I could finish in a weekend and actually use,
rather than a project I would still be configuring the week of the exam.

## Using it

On a computer, open `ccse.html` directly.

On a phone, either send yourself the file and open it from Files, or serve the folder
and browse to it over your local network:

```
python3 serve.py
```

Then open `http://<your-machine>:8765/ccse.html`. The server disables caching, because
otherwise a phone browser will keep showing you a stale copy after a rebuild and you
will lose an hour working out why your change did nothing.

Opening the file directly works fine, but browsers restrict storage for local files, so
your history may not survive between sessions. Serving it over HTTP avoids that.

## The four modes

**Examen** mirrors the real thing: 25 questions in 45 minutes, drawn 10/3/2/3/7 across
the five tareas, in that order. That split is not a guess. It matches the published
sample exam, and it also matches the proportions of the question bank itself
(120/36/24/36/84 of 300), which is reassuring. You need 15 of 25 to pass, so the result
screen shows APTO or NO APTO alongside your score. Wrong answers are not penalised.

**Sin fin** runs all 300. It shuffles them but never puts two questions from the same
tarea back to back, so you are not stuck grinding through forty Tarea 1 questions in a
row. It also reports your median time per question, which turned out to be a more
useful number than the total.

**Repasar fallos** serves only the questions you got wrong last time, worst first. Get
one right and it leaves the list, so the list can actually reach zero.

**Buscar** is the one I use most. If you are working through a mock exam in the official
app, type two or three words from the question here, answer it alongside, and read the
explanation. Answers accumulate across lookups into a single session, so twenty
questions looked up one at a time still come out as one result at the end.

Multiple-choice options are shuffled every time a question appears. Without that you
start remembering that the answer is the second one rather than remembering the answer.

## Where the answers come from

Both the questions and the answers come from the *Manual de preparación de la prueba
CCSE* published by the Instituto Cervantes. It prints the full question bank and, near
the back, a `Soluciones` section giving the correct letter for each of the 300 items.

The PDF is not in this repository. Download it from the Instituto Cervantes and either
put it at `sources/manual-ccse-2026-def.pdf` or point an environment variable at it:

```
export CCSE_MANUAL=~/path/to/manual-ccse-2026.pdf
```

With the manual available, `build.py` re-reads that answer key on every build and
compares it against every answer in `questions.json`. If the two ever disagree the build
fails and writes nothing. That check is the reason I trust the data. Without the manual
the build still works, it just tells you the check was skipped.

The explanations are a different matter. I drafted them against the manual with a lot of
help from an LLM, then went back and checked them: every claim had to be supported by
the manual, every page reference had to actually contain the relevant text, and anything
that could not be supported was cut rather than smoothed over. A few explanations
mention a fact that is true but is not in the manual, for instance that 091 is the
Policía Nacional. Treat the page references as the trustworthy part and the prose as
something worth reading sceptically.

## Rebuilding

Edit `questions.json` or `template.html`, then:

```
python3 build.py
```

This validates the data and regenerates `ccse.html`. It refuses to write if anything
looks wrong: an answer that disagrees with the manual, a duplicate id, a malformed
question, or a highlighted work title that does not actually occur in the question text.

The answer key check needs `pdftotext` (`brew install poppler` on macOS) and a copy of
the manual. Both are optional: without them the build says so and carries on.

## Files

| | |
|---|---|
| `ccse.html` | the app, generated, the only file you need to run it |
| `template.html` | markup, styling and logic, with a placeholder where the data goes |
| `questions.json` | the 300 questions, answers, explanations and page references |
| `build.py` | validates the data and builds `ccse.html` |
| `serve.py` | static file server with caching turned off |

Your answer history lives in the browser's local storage, not in a file. There is an
export button if you want a copy.

## Where I would take this next

This is a weekend tool that I kept using, which is usually the point at which something
deserves a rewrite. If I come back to it I would like to move the logic to TypeScript
and give it real tests, or use it as an excuse to finally learn Swift and make it a
proper iOS app. Spaced repetition would suit the material far better than my current
"wrong last time" rule. Per-question statistics would help too: knowing I keep failing
the same six questions is more actionable than a per-tarea percentage.

For now it does the job, and the exam is the deadline that matters.

## A note on the material

The questions and answers are the Instituto Cervantes'. The explanations, the app and
the code are mine.
