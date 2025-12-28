import re


class MarkdownTruncator:
    @staticmethod
    def get_smart_preview(content, is_markdown=True, max_lines=3, max_chars=200):
        """
        智能预览生成器
        :param content: 原始字符串 (Text 或 Markdown)
        :param is_markdown: 是否为 markdown 类型
        :param max_lines: 最多保留多少个视觉段落
        :param max_chars: 总字符数上限兜底
        :return: 截断后的安全字符串
        """
        if not content:
            return ""

        # 1. 处理纯文本：直接按字符截断，简单粗暴
        if not is_markdown:
            content = content.strip()
            return content[:max_chars] + ("..." if len(content) > max_chars else "")

        # 2. 处理 Markdown：按段落（双换行）切分
        # 过滤掉开头的空行
        content = content.lstrip()

        # 将文本按连续换行符切分为“块”
        blocks = re.split(r"\n\s*\n", content)

        # 取前 N 段
        preview_blocks = blocks[:max_lines]

        # 拼接回字符串
        preview_text = "\n\n".join(preview_blocks)

        # 3. 长度硬截断兜底 (防止某一个段落特别长)
        if len(preview_text) > max_chars:
            preview_text = preview_text[:max_chars] + "..."

        # 4. 核心：Markdown 语法无损补偿
        # 情况 A: 补全未闭合的代码块 (```)
        if preview_text.count("```") % 2 != 0:
            preview_text += "\n```"

        # 情况 B: 补全未闭合的加粗/斜体 (** 或 *)
        # 这种通常在字符截断时发生，正则匹配最后一行是否有奇数的 * 号
        last_line = preview_text.split("\n")[-1]
        if last_line.count("**") % 2 != 0:
            preview_text += "**"
        elif last_line.count("*") % 2 != 0:
            preview_text += "*"

        return preview_text
