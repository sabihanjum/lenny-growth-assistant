"""Artifact Generation & Extraction Skill: Formats and parses Claude-style artifacts."""

import re
from typing import List, Dict, Any, Tuple

ARTIFACT_SYSTEM_PROMPT = """When creating standalone documents, comprehensive frameworks, or interactive visual tools (such as calculators, dashboards, or simulation widgets), generate them as self-contained ARTIFACTS.

Artifact Format Specification:
Wrap the generated code or document inside `<artifact>` tags with strict attributes:
<artifact identifier="kebab-case-slug" type="html|markdown" title="Human-Readable Title">
...complete, self-contained document or code snippet...
</artifact>

Guidelines for HTML/CSS/JS Artifacts:
1. Always produce complete, valid HTML5 documents including `<!DOCTYPE html><html><head>...<body>...</html>`.
2. Include modern, beautiful inline CSS or load Tailwind CSS via CDN (`https://cdn.tailwindcss.com`).
3. If interactive JavaScript is needed (e.g. for calculators or sliders), include clean vanilla JavaScript inside `<script>` tags.
4. The artifact must be completely self-contained and run cleanly inside a sandboxed iframe without requiring external server endpoints.

Guidelines for Markdown Artifacts:
1. Use rich GFM (GitHub Flavored Markdown) with clear hierarchies, tables, and task checklists.
"""

ARTIFACT_REGEX = re.compile(
    r'<artifact\s+identifier="(?P<identifier>[^"]+)"\s+type="(?P<type>html|markdown)"\s+title="(?P<title>[^"]+)">\s*(?P<content>.*?)\s*</artifact>',
    re.DOTALL | re.IGNORECASE
)


def extract_artifacts(raw_text: str) -> Tuple[str, List[Dict[str, str]]]:
    """Parse out artifact tags from LLM response text.
    Returns:
        (clean_text, list_of_artifacts)
    """
    artifacts = []
    
    def replacer(match):
        identifier = match.group("identifier").strip()
        art_type = match.group("type").strip().lower()
        title = match.group("title").strip()
        content = match.group("content").strip()

        artifacts.append({
            "identifier": identifier,
            "artifact_type": art_type,
            "title": title,
            "content": content
        })

        return f"\n\n> 📦 **Generated Artifact:** [{title}]({identifier})\n*View the rendered artifact in the side-by-side viewer panel.*"

    clean_text = ARTIFACT_REGEX.sub(replacer, raw_text)
    return clean_text.strip(), artifacts
