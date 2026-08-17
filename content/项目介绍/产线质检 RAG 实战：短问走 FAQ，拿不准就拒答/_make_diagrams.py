"""Generate two Chinese flowchart images for the QC KB blog."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent
FONT = r"C:\Windows\Fonts\msyh.ttc"
FONT_BD = r"C:\Windows\Fonts\msyhbd.ttc"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = FONT_BD if bold else FONT
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.truetype(FONT, size)


def rounded_rect(draw, xy, radius, fill, outline=None, width=2):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def center_text(draw, xy, text, fnt, fill):
    x1, y1, x2, y2 = xy
    bbox = draw.textbbox((0, 0), text, font=fnt)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(
        ((x1 + x2 - tw) / 2, (y1 + y2 - th) / 2 - 2),
        text,
        font=fnt,
        fill=fill,
    )


def multiline_center(draw, xy, lines, fnt, fill, gap=6):
    x1, y1, x2, y2 = xy
    heights = []
    widths = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=fnt)
        widths.append(bbox[2] - bbox[0])
        heights.append(bbox[3] - bbox[1])
    total_h = sum(heights) + gap * (len(lines) - 1)
    y = (y1 + y2 - total_h) / 2
    cx = (x1 + x2) / 2
    for line, w, h in zip(lines, widths, heights):
        draw.text((cx - w / 2, y - 2), line, font=fnt, fill=fill)
        y += h + gap


def arrow_right(draw, x1, y, x2, fill="#5B6573"):
    draw.line((x1, y, x2 - 10, y), fill=fill, width=3)
    draw.polygon([(x2, y), (x2 - 12, y - 7), (x2 - 12, y + 7)], fill=fill)


def arrow_down(draw, x, y1, y2, fill="#5B6573"):
    draw.line((x, y1, x, y2 - 10), fill=fill, width=3)
    draw.polygon([(x, y2), (x - 7, y2 - 12), (x + 7, y2 - 12)], fill=fill)


def make_pipeline() -> None:
    w, h = 1400, 620
    img = Image.new("RGB", (w, h), "#F7F8FA")
    d = ImageDraw.Draw(img)
    title_f = font(28, True)
    box_f = font(22, True)
    sub_f = font(16)
    cap_f = font(18)

    d.text((48, 28), "总链路：先分流，再决定要不要生成", font=title_f, fill="#1F2933")

    boxes = [
        (40, 160, 280, 300, "#FFFFFF", "#2F6FED", "质检员提问", "短问 / 复杂判断"),
        (340, 160, 620, 300, "#FFFFFF", "#1F8A4C", "FAQ 快通道", "高置信直接返回"),
        (680, 90, 980, 230, "#FFFFFF", "#2F6FED", "RAG 检索生成", "文档 + Qwen"),
        (680, 270, 980, 410, "#FFFFFF", "#C45C00", "拒答转现场", "不足或标准冲突"),
        (1040, 160, 1360, 300, "#FFFFFF", "#4B5563", "人工签字仍有效", "系统只是辅助"),
    ]
    for x1, y1, x2, y2, fill, edge, t1, t2 in boxes:
        rounded_rect(d, (x1, y1, x2, y2), 16, fill, edge, 3)
        multiline_center(d, (x1, y1, x2, y2 - 18), [t1, t2], box_f if t1 else sub_f, "#1F2933")

    # Relabel with mixed sizes: redraw text properly
    # Clear inner by redrawing boxes then text with two fonts
    img = Image.new("RGB", (w, h), "#F7F8FA")
    d = ImageDraw.Draw(img)
    d.text((48, 28), "总链路：先分流，再决定要不要生成", font=title_f, fill="#1F2933")

    specs = [
        (40, 170, 290, 330, "#E8F1FF", "#2F6FED", "质检员提问", "返工复检 / 异响排故"),
        (360, 170, 640, 330, "#E7F6EE", "#1F8A4C", "FAQ 快通道", "高置信、带出处直出"),
        (710, 80, 1000, 220, "#E8F1FF", "#2F6FED", "RAG 检索生成", "作业指导 → Qwen"),
        (710, 280, 1000, 420, "#FFF3E6", "#C45C00", "拒答转现场", "不足或标准冲突"),
        (1070, 170, 1360, 330, "#EEF0F3", "#4B5563", "人工签字仍有效", "系统不代替终审"),
    ]
    for x1, y1, x2, y2, fill, edge, t1, t2 in specs:
        rounded_rect(d, (x1, y1, x2, y2), 18, fill, edge, 3)
        d.text((0, 0), "", font=box_f)
        b1 = d.textbbox((0, 0), t1, font=box_f)
        b2 = d.textbbox((0, 0), t2, font=sub_f)
        tw1, th1 = b1[2] - b1[0], b1[3] - b1[1]
        tw2, th2 = b2[2] - b2[0], b2[3] - b2[1]
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2
        d.text((cx - tw1 / 2, cy - th1 - 6), t1, font=box_f, fill="#1F2933")
        d.text((cx - tw2 / 2, cy + 8), t2, font=sub_f, fill="#4B5563")

    arrow_right(d, 290, 250, 360)
    arrow_right(d, 640, 250, 710)
    arrow_right(d, 1000, 250, 1070)
    # split from FAQ to RAG / refuse conceptually: second arrow already to RAG column
    d.text((648, 236), "未命中", font=cap_f, fill="#5B6573")
    arrow_down(d, 855, 220, 280)
    d.text((870, 236), "冲突/不足", font=cap_f, fill="#C45C00")

    d.text((40, 470), "短问尽量走 FAQ；复杂判断才生成；拿不准就停，把人转回现场。", font=cap_f, fill="#4B5563")
    d.text((40, 510), "图 1  ·  示意图，非真实系统截图", font=sub_f, fill="#9AA3AD")
    img.save(OUT / "01-pipeline.png", "PNG")


def make_routing() -> None:
    w, h = 1400, 720
    img = Image.new("RGB", (w, h), "#F7F8FA")
    d = ImageDraw.Draw(img)
    title_f = font(28, True)
    box_f = font(22, True)
    sub_f = font(16)
    cap_f = font(18)

    d.text((48, 28), "分流：宁可漏中，也不要把错的制度说成对的", font=title_f, fill="#1F2933")

    def box(xy, fill, edge, t1, t2):
        x1, y1, x2, y2 = xy
        rounded_rect(d, xy, 18, fill, edge, 3)
        b1 = d.textbbox((0, 0), t1, font=box_f)
        b2 = d.textbbox((0, 0), t2, font=sub_f)
        tw1, th1 = b1[2] - b1[0], b1[3] - b1[1]
        tw2, th2 = b2[2] - b2[0], b2[3] - b2[1]
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2
        d.text((cx - tw1 / 2, cy - th1 - 6), t1, font=box_f, fill="#1F2933")
        d.text((cx - tw2 / 2, cy + 8), t2, font=sub_f, fill="#4B5563")

    box((500, 90, 900, 200), "#E8F1FF", "#2F6FED", "BM25 打分", "相对分 + 绝对分同时过")
    box((80, 320, 420, 460), "#E7F6EE", "#1F8A4C", "高置信：FAQ 直出", "带来源条款，写入缓存")
    box((490, 320, 910, 460), "#E8F1FF", "#2F6FED", "未过阈值：进 RAG", "检索作业指导再生成")
    box((980, 320, 1320, 460), "#FFF3E6", "#C45C00", "不足或冲突：拒答", "转现场，不给和稀泥结论")

    # diamond-like decision via arrows
    arrow_down(d, 700, 200, 250)
    d.text((720, 214), "阈值判定", font=cap_f, fill="#5B6573")

    # three arrows from center
    d.line((700, 250, 700, 300), fill="#5B6573", width=3)
    d.line((250, 300, 1150, 300), fill="#5B6573", width=3)
    arrow_down(d, 250, 300, 320)
    arrow_down(d, 700, 300, 320)
    arrow_down(d, 1150, 300, 320)
    d.text((150, 268), "过关", font=cap_f, fill="#1F8A4C")
    d.text((610, 268), "中间分 / 未命中", font=cap_f, fill="#2F6FED")
    d.text((1160, 268), "生成后仍无据", font=cap_f, fill="#C45C00")

    d.text((80, 520), "FAQ 误中比漏中更麻烦：漏中最多再走 RAG，误中会把错的制度直接当成标准答案。", font=cap_f, fill="#4B5563")
    d.text((80, 560), "寒暄和明显跑题的问题不进知识库，避免检索去解释无关闲聊。", font=cap_f, fill="#4B5563")
    d.text((80, 620), "图 2  ·  示意图，非真实系统截图", font=sub_f, fill="#9AA3AD")
    img.save(OUT / "02-routing.png", "PNG")


if __name__ == "__main__":
    make_pipeline()
    make_routing()
    print("wrote", OUT / "01-pipeline.png")
    print("wrote", OUT / "02-routing.png")
