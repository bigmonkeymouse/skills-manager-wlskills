---
name: markitdown-converter
description: Convert files to Markdown using the locally installed markitdown tool. Use when the user asks to turn PDF, DOCX, PPTX, XLSX, HTML, CSV, JSON, XML, EPUB, YouTube URLs, or similar supported inputs into Markdown, or when the task is to prepare content for LLM pipelines, extraction, or downstream text analysis.
---

# Markitdown Converter

Use the local markitdown installation to convert a source file into Markdown.

## Environment

- Use `$CODEX_HOME/skills/markitdown-converter/scripts/convert_to_markdown.py` by default.
- Default venv target: `F:/ai_proj/markitdown/.venv/Scripts/python.exe`
- Override with env vars when needed:
  - `MARKITDOWN_VENV_PYTHON`
  - `MARKITDOWN_PYTHON_FALLBACK`
- Confirm the target file exists before invoking conversion.
- If the user provides an output path, write Markdown to that path; otherwise print to stdout.
- Prefer the narrowest invocation that satisfies the request.
- If audio workflows are requested, note that ffmpeg may be required.

## Quick start

Run the bundled helper script:

```bash
python "$CODEX_HOME/skills/markitdown-converter/scripts/convert_to_markdown.py" "<input_file>" -o "<output.md>"
```

Common examples:

- PDF to Markdown: convert `report.pdf` to `report.md`
- Office to Markdown: convert `.docx`, `.pptx`, `.xlsx`
- Web or data formats: convert HTML, CSV, JSON, XML
- Media or metadata cases: handle image/audio metadata when supported

## Workflow

1. Identify the input file and desired output destination.
2. Use the helper script for deterministic behavior.
3. If the user asks for quick inspection only, print Markdown to stdout.
4. If the user asks for a saved result, write to an explicit output file.
5. If conversion fails, check environment availability and whether the file type is supported.

## Notes

- Keep outputs clean and token-efficient for downstream use.
- If the user needs selective extraction instead of full conversion, prefer a targeted approach before full Markdown export.