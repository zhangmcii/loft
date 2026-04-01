import re
from dataclasses import dataclass

from .markdown_images import replace_markdown_image_refs


@dataclass(frozen=True)
class SummaryPreview:
    summary: str
    is_truncated: bool


class MarkdownTruncator:
    DEFAULT_MAX_BLOCKS = 3
    DEFAULT_MAX_VISIBLE_CHARS = 200
    DEFAULT_MAX_OUTPUT_CHARS = 260

    @staticmethod
    def build_preview(
        content,
        *,
        is_markdown=True,
        image_refs=None,
        max_blocks=DEFAULT_MAX_BLOCKS,
        max_visible_chars=DEFAULT_MAX_VISIBLE_CHARS,
        max_output_chars=DEFAULT_MAX_OUTPUT_CHARS,
    ) -> SummaryPreview:
        if not content:
            return SummaryPreview(summary="", is_truncated=False)

        if not is_markdown:
            content = content.strip()
            is_truncated = len(content) > max_visible_chars
            summary = content[:max_visible_chars] + ("..." if is_truncated else "")
            return SummaryPreview(summary=summary, is_truncated=is_truncated)

        normalized = MarkdownTruncator._prepare_markdown_content(
            content, image_refs=image_refs
        )
        blocks = re.split(r"\n\s*\n", normalized)

        preview_blocks = []
        used_visible = 0
        used_output = 0
        is_truncated = False
        block_count = 0

        for block in blocks:
            stripped_block = block.strip()
            if not stripped_block:
                continue

            if block_count >= max_blocks:
                is_truncated = True
                break

            joiner = "\n\n" if preview_blocks else ""
            next_output_len = used_output + len(joiner) + len(stripped_block)
            next_visible_len = (
                used_visible
                + MarkdownTruncator._estimate_visible_length(stripped_block)
            )

            if (
                next_visible_len <= max_visible_chars
                and next_output_len <= max_output_chars
            ):
                preview_blocks.append(stripped_block)
                used_visible = next_visible_len
                used_output = next_output_len
                block_count += 1
                continue

            remaining_visible = max(max_visible_chars - used_visible, 0)
            remaining_output = max(
                max_output_chars - used_output - len(joiner),
                0,
            )
            truncated_block = MarkdownTruncator._truncate_block(
                stripped_block,
                remaining_visible=remaining_visible,
                remaining_output=remaining_output,
            )
            if truncated_block:
                preview_blocks.append(truncated_block)
            is_truncated = True
            break

        preview_text = "\n\n".join(preview_blocks).strip()
        preview_text = MarkdownTruncator._finalize_preview(preview_text, is_truncated)
        return SummaryPreview(summary=preview_text, is_truncated=is_truncated)

    @staticmethod
    def _prepare_markdown_content(content, *, image_refs=None):
        normalized = (content or "").lstrip()
        if not normalized:
            return ""

        if image_refs:
            positions = [item.get("pos", "") for item in image_refs]
            urls = [item.get("url", "") for item in image_refs]
            normalized = replace_markdown_image_refs(normalized, positions, urls)

        return normalized

    @staticmethod
    def _truncate_block(block, *, remaining_visible, remaining_output):
        if remaining_visible <= 0 or remaining_output <= 0:
            return ""

        if block.lstrip().startswith("```"):
            return MarkdownTruncator._truncate_code_block(
                block,
                remaining_visible=remaining_visible,
                remaining_output=remaining_output,
            )

        tokens = re.findall(
            r"!\[[^\]]*\]\([^)]+\)|\[[^\]]+\]\([^)]+\)|\s+|[^\s]+",
            block,
        )

        selected = []
        used_visible = 0
        used_output = 0

        for token in tokens:
            token_output = len(token)
            token_visible = MarkdownTruncator._estimate_visible_length(token)

            if used_output + token_output > remaining_output:
                break
            if used_visible + token_visible > remaining_visible and selected:
                break
            if token_visible > remaining_visible and not selected:
                partial = MarkdownTruncator._truncate_plain_token(
                    token,
                    remaining_visible=remaining_visible,
                    remaining_output=remaining_output,
                )
                if partial:
                    selected.append(partial)
                break

            selected.append(token)
            used_visible += token_visible
            used_output += token_output

        return "".join(selected).rstrip()

    @staticmethod
    def _truncate_code_block(block, *, remaining_visible, remaining_output):
        lines = block.splitlines()
        if not lines:
            return ""

        selected = []
        used_visible = 0
        used_output = 0

        for line in lines:
            line_with_break = line if not selected else f"\n{line}"
            line_output = len(line_with_break)
            line_visible = MarkdownTruncator._estimate_visible_length(line)
            if selected and (
                used_output + line_output > remaining_output
                or used_visible + line_visible > remaining_visible
            ):
                break
            if not selected and line_output > remaining_output:
                return ""
            selected.append(line)
            used_output += line_output
            used_visible += line_visible

        if not selected:
            return ""

        preview = "\n".join(selected).rstrip()
        if preview.count("```") % 2 != 0:
            if len(preview) + 4 <= remaining_output:
                preview += "\n```"
        return preview

    @staticmethod
    def _truncate_plain_token(token, *, remaining_visible, remaining_output):
        if token.isspace():
            return token[:remaining_output]

        if MarkdownTruncator._looks_like_markdown_atom(token):
            return ""

        selected = []
        used_visible = 0
        used_output = 0
        for char in token:
            if used_output + 1 > remaining_output:
                break
            if used_visible + 1 > remaining_visible:
                break
            selected.append(char)
            used_output += 1
            used_visible += 1
        return "".join(selected).rstrip()

    @staticmethod
    def _looks_like_markdown_atom(token):
        return bool(re.fullmatch(r"!\[[^\]]*\]\([^)]+\)|\[[^\]]+\]\([^)]+\)", token))

    @staticmethod
    def _estimate_visible_length(text):
        visible = text
        visible = re.sub(
            r"!\[([^\]]*)\]\([^)]+\)",
            lambda match: match.group(1).strip() or "[图片]",
            visible,
        )
        visible = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", visible)
        visible = re.sub(r"`([^`]*)`", r"\1", visible)
        visible = re.sub(r"(\*\*|__)(.*?)\1", r"\2", visible)
        visible = re.sub(r"(\*|_)(.*?)\1", r"\2", visible)
        visible = re.sub(r"^\s{0,3}(#{1,6}|>|[-+*]|\d+\.)\s+", "", visible)
        visible = re.sub(r"<[^>]+>", "", visible)
        visible = re.sub(r"\s+", " ", visible).strip()
        return len(visible)

    @staticmethod
    def _finalize_preview(preview_text, is_truncated):
        preview = preview_text.rstrip()
        if preview.count("```") % 2 != 0:
            preview += "\n```"

        last_line = preview.split("\n")[-1] if preview else ""
        if last_line.count("**") % 2 != 0:
            preview += "**"
        elif last_line.count("*") % 2 != 0:
            preview += "*"

        if is_truncated and preview:
            preview += "..."

        return preview
