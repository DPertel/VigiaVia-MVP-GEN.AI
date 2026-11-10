import re
from dataclasses import dataclass

from .config import SOURCES_DIR


@dataclass
class Chunk:
    chunk_id: str
    source_id: str
    source_name: str
    text: str


def load_chunks():
    chunks = []

    for path in sorted(SOURCES_DIR.glob("*.md")):
        if path.name.lower() == "leia_antes.md":
            continue

        source_id = path.stem
        content = path.read_text(encoding="utf-8")

        current_heading = ""
        paragraphs = []
        current_paragraph = []

        def save_paragraph():
            if not current_paragraph:
                return

            paragraph = " ".join(current_paragraph).strip()

            if paragraph:
                if current_heading:
                    paragraphs.append(
                        f"Seção: {current_heading}\n{paragraph}"
                    )
                else:
                    paragraphs.append(paragraph)

            current_paragraph.clear()

        for line in content.splitlines():
            heading_match = re.match(
                r"^\s*#{1,6}\s+(.+?)\s*#*\s*$",
                line
            )

            if heading_match:
                save_paragraph()
                current_heading = heading_match.group(1).strip()
                continue

            if not line.strip():
                save_paragraph()
                continue

            current_paragraph.append(line.strip())

        save_paragraph()

        for i, paragraph in enumerate(paragraphs, 1):
            chunks.append(
                Chunk(
                    chunk_id=f"{source_id}-{i:03d}",
                    source_id=source_id,
                    source_name=path.name,
                    text=paragraph
                )
            )

    return chunks
