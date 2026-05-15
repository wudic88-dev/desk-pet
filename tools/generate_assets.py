"""
生成可爱猫咪桌宠素材
使用 Pillow 绘制扁平卡通风格的猫咪 PNG 图片
"""

from PIL import Image, ImageDraw
import os

# 画布尺寸
SIZE = 256
HALF = SIZE // 2

# 颜色定义
ORANGE = "#F5A623"
ORANGE_DARK = "#D48C1A"
WHITE = "#FFFFFF"
PINK = "#FFB6C1"
PINK_DARK = "#FF8DA1"
BLACK = "#2C2C2C"
GRAY = "#888888"


def create_base():
    """创建透明底图"""
    return Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))


def draw_cat_base(img, body_y_offset=0, tail_angle=0):
    """绘制猫咪基础形状"""
    draw = ImageDraw.Draw(img)

    # 身体（白色腹部 + 橘色背部）
    body_top = 140 + body_y_offset
    draw.ellipse([70, body_top, 186, 240 + body_y_offset], fill=ORANGE)
    draw.ellipse([90, body_top + 20, 166, 230 + body_y_offset], fill=WHITE)

    # 尾巴
    tail_x = 180 + tail_angle
    tail_y = 200 - abs(tail_angle) // 2
    points = [
        (170, 210 + body_y_offset),
        (tail_x, tail_y),
        (tail_x + 15, tail_y - 30),
        (tail_x + 5, tail_y - 50),
        (tail_x - 10, tail_y - 40),
        (tail_x - 5, tail_y - 20),
        (160, 200 + body_y_offset),
    ]
    draw.polygon(points, fill=ORANGE)
    draw.line([(tail_x, tail_y - 10), (tail_x + 8, tail_y - 15)], fill=ORANGE_DARK, width=2)
    draw.line([(tail_x + 2, tail_y - 25), (tail_x + 10, tail_y - 30)], fill=ORANGE_DARK, width=2)

    # 头部
    head_top = 45
    draw.ellipse([40, head_top, 216, head_top + 170], fill=ORANGE)
    draw.ellipse([55, head_top + 60, 201, head_top + 165], fill=WHITE)

    # 耳朵
    draw.polygon([(55, head_top + 40), (35, head_top - 10), (90, head_top + 20)], fill=ORANGE)
    draw.polygon([(58, head_top + 35), (45, head_top + 5), (80, head_top + 25)], fill=PINK)
    draw.polygon([(201, head_top + 40), (221, head_top - 10), (166, head_top + 20)], fill=ORANGE)
    draw.polygon([(198, head_top + 35), (211, head_top + 5), (176, head_top + 25)], fill=PINK)

    # 头顶条纹
    draw.polygon([(HALF - 8, head_top + 10), (HALF, head_top + 25), (HALF + 8, head_top + 10)], fill=ORANGE_DARK)
    draw.polygon([(HALF - 25, head_top + 15), (HALF - 18, head_top + 28), (HALF - 10, head_top + 15)], fill=ORANGE_DARK)
    draw.polygon([(HALF + 10, head_top + 15), (HALF + 18, head_top + 28), (HALF + 25, head_top + 15)], fill=ORANGE_DARK)

    # 鼻子
    nose_y = head_top + 105
    draw.polygon([(HALF, nose_y - 5), (HALF - 8, nose_y + 8), (HALF + 8, nose_y + 8)], fill=PINK_DARK)

    # 胡须
    whisker_y = nose_y + 5
    draw.line([(40, whisker_y), (85, whisker_y + 3)], fill=GRAY, width=1)
    draw.line([(42, whisker_y + 12), (87, whisker_y + 10)], fill=GRAY, width=1)
    draw.line([(215, whisker_y), (170, whisker_y + 3)], fill=GRAY, width=1)
    draw.line([(213, whisker_y + 12), (168, whisker_y + 10)], fill=GRAY, width=1)

    # 腮红
    draw.ellipse([50, head_top + 90, 80, head_top + 115], fill=PINK)
    draw.ellipse([176, head_top + 90, 206, head_top + 115], fill=PINK)

    return draw, head_top


def generate_idle():
    """生成待机动画帧（4帧：呼吸起伏 + 眨眼）"""
    frames = []

    def make_frame(body_off, tail_ang, eyes_open):
        img = create_base()
        draw, head_top = draw_cat_base(img, body_y_offset=body_off, tail_angle=tail_ang)
        eye_y = head_top + 65
        if eyes_open:
            draw.ellipse([70, eye_y, 110, eye_y + 45], fill=BLACK)
            draw.ellipse([78, eye_y + 8, 95, eye_y + 22], fill=WHITE)
            draw.ellipse([146, eye_y, 186, eye_y + 45], fill=BLACK)
            draw.ellipse([154, eye_y + 8, 171, eye_y + 22], fill=WHITE)
        else:
            draw.arc([70, eye_y + 15, 110, eye_y + 35], start=0, end=180, fill=BLACK, width=3)
            draw.arc([146, eye_y + 15, 186, eye_y + 35], start=0, end=180, fill=BLACK, width=3)
        mouth_y = head_top + 115
        draw.arc([HALF - 15, mouth_y, HALF + 15, mouth_y + 20], start=0, end=180, fill=BLACK, width=2)
        return img

    frames.append(make_frame(0, 0, True))
    frames.append(make_frame(3, -3, True))
    frames.append(make_frame(-2, 2, False))
    frames.append(make_frame(0, 0, True))
    return frames


def generate_click():
    """生成点击反馈帧（3帧：压缩 -> 弹回 -> 恢复）"""
    frames = []

    # Frame 0: 被点击压缩
    img = create_base()
    draw = ImageDraw.Draw(img)
    body_top = 150
    draw.ellipse([60, body_top, 196, 235], fill=ORANGE)
    draw.ellipse([85, body_top + 15, 171, 225], fill=WHITE)
    draw.polygon([(170, 215), (190, 205), (195, 185), (185, 175), (175, 190), (160, 205)], fill=ORANGE)
    head_top = 50
    draw.ellipse([35, head_top, 221, head_top + 155], fill=ORANGE)
    draw.ellipse([50, head_top + 55, 206, head_top + 150], fill=WHITE)
    draw.polygon([(50, head_top + 45), (25, head_top + 5), (80, head_top + 25)], fill=ORANGE)
    draw.polygon([(55, head_top + 40), (40, head_top + 15), (75, head_top + 30)], fill=PINK)
    draw.polygon([(206, head_top + 45), (231, head_top + 5), (176, head_top + 25)], fill=ORANGE)
    draw.polygon([(201, head_top + 40), (216, head_top + 15), (181, head_top + 30)], fill=PINK)
    eye_y = head_top + 60
    draw.line([(75, eye_y), (95, eye_y + 12)], fill=BLACK, width=3)
    draw.line([(95, eye_y + 12), (75, eye_y + 24)], fill=BLACK, width=3)
    draw.line([(181, eye_y), (161, eye_y + 12)], fill=BLACK, width=3)
    draw.line([(161, eye_y + 12), (181, eye_y + 24)], fill=BLACK, width=3)
    draw.polygon([(HALF, head_top + 95), (HALF - 8, head_top + 108), (HALF + 8, head_top + 108)], fill=PINK_DARK)
    draw.ellipse([HALF - 8, head_top + 110, HALF + 8, head_top + 130], fill=PINK_DARK)
    draw.ellipse([45, head_top + 80, 75, head_top + 105], fill=PINK)
    draw.ellipse([181, head_top + 80, 211, head_top + 105], fill=PINK)
    frames.append(img)

    # Frame 1: 弹回
    img = create_base()
    draw, head_top = draw_cat_base(img, body_y_offset=-5, tail_angle=5)
    eye_y = head_top + 60
    draw.line([(75, eye_y), (95, eye_y + 12)], fill=BLACK, width=3)
    draw.line([(95, eye_y + 12), (75, eye_y + 24)], fill=BLACK, width=3)
    draw.line([(181, eye_y), (161, eye_y + 12)], fill=BLACK, width=3)
    draw.line([(161, eye_y + 12), (181, eye_y + 24)], fill=BLACK, width=3)
    draw.polygon([(HALF, head_top + 95), (HALF - 8, head_top + 108), (HALF + 8, head_top + 108)], fill=PINK_DARK)
    draw.arc([HALF - 15, head_top + 105, HALF + 15, head_top + 125], start=0, end=180, fill=BLACK, width=2)
    frames.append(img)

    # Frame 2: 恢复
    img = create_base()
    draw, head_top = draw_cat_base(img, body_y_offset=0, tail_angle=0)
    eye_y = head_top + 65
    draw.ellipse([70, eye_y, 110, eye_y + 45], fill=BLACK)
    draw.ellipse([78, eye_y + 8, 95, eye_y + 22], fill=WHITE)
    draw.ellipse([146, eye_y, 186, eye_y + 45], fill=BLACK)
    draw.ellipse([154, eye_y + 8, 171, eye_y + 22], fill=WHITE)
    draw.arc([HALF - 15, head_top + 115, HALF + 15, head_top + 135], start=0, end=180, fill=BLACK, width=2)
    frames.append(img)

    return frames


def generate_talk():
    """生成说话动画帧（2帧：张嘴 / 闭嘴）"""
    frames = []

    # 张嘴
    img = create_base()
    draw, head_top = draw_cat_base(img, body_y_offset=0, tail_angle=0)
    eye_y = head_top + 65
    draw.ellipse([70, eye_y, 110, eye_y + 45], fill=BLACK)
    draw.ellipse([78, eye_y + 8, 95, eye_y + 22], fill=WHITE)
    draw.ellipse([146, eye_y, 186, eye_y + 45], fill=BLACK)
    draw.ellipse([154, eye_y + 8, 171, eye_y + 22], fill=WHITE)
    mouth_y = head_top + 110
    draw.arc([HALF - 15, mouth_y, HALF + 15, mouth_y + 20], start=0, end=180, fill=BLACK, width=2)
    draw.ellipse([HALF - 8, mouth_y + 8, HALF + 8, mouth_y + 22], fill=PINK)
    frames.append(img)

    # 闭嘴
    img = create_base()
    draw, head_top = draw_cat_base(img, body_y_offset=0, tail_angle=-2)
    eye_y = head_top + 65
    draw.ellipse([70, eye_y, 110, eye_y + 45], fill=BLACK)
    draw.ellipse([78, eye_y + 8, 95, eye_y + 22], fill=WHITE)
    draw.ellipse([146, eye_y, 186, eye_y + 45], fill=BLACK)
    draw.ellipse([154, eye_y + 8, 171, eye_y + 22], fill=WHITE)
    draw.arc([HALF - 15, head_top + 115, HALF + 15, head_top + 135], start=0, end=180, fill=BLACK, width=2)
    frames.append(img)

    return frames


def generate_tray_icon():
    """生成系统托盘图标（64x64 简化版）"""
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([4, 8, 60, 56], fill=ORANGE)
    draw.ellipse([10, 22, 54, 54], fill=WHITE)
    draw.polygon([(10, 16), (4, 2), (20, 10)], fill=ORANGE)
    draw.polygon([(54, 16), (60, 2), (44, 10)], fill=ORANGE)
    draw.ellipse([14, 20, 26, 32], fill=BLACK)
    draw.ellipse([16, 22, 22, 27], fill=WHITE)
    draw.ellipse([38, 20, 50, 32], fill=BLACK)
    draw.ellipse([40, 22, 46, 27], fill=WHITE)
    draw.polygon([(32, 32), (28, 38), (36, 38)], fill=PINK_DARK)
    draw.arc([26, 34, 38, 44], start=0, end=180, fill=BLACK, width=1)
    return img


def save_frames(frames, folder, prefix):
    os.makedirs(folder, exist_ok=True)
    for i, frame in enumerate(frames):
        path = os.path.join(folder, f"{prefix}_{i}.png")
        frame.save(path)
        print(f"  Saved: {path}")


def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    assets_dir = os.path.join(base_dir, "assets", "pet")

    print("=" * 50)
    print("  正在生成桌宠猫咪素材...")
    print("=" * 50)

    print("\n[1/4] 生成待机动画帧 (idle)...")
    save_frames(generate_idle(), os.path.join(assets_dir, "idle"), "idle")

    print("\n[2/4] 生成点击反馈帧 (click)...")
    save_frames(generate_click(), os.path.join(assets_dir, "click"), "click")

    print("\n[3/4] 生成说话动画帧 (talk)...")
    save_frames(generate_talk(), os.path.join(assets_dir, "talk"), "talk")

    print("\n[4/4] 生成托盘图标 (tray_icon)...")
    tray_path = os.path.join(base_dir, "assets", "icons", "tray_icon.png")
    os.makedirs(os.path.dirname(tray_path), exist_ok=True)
    generate_tray_icon().save(tray_path)
    print(f"  Saved: {tray_path}")

    print("\n" + "=" * 50)
    print("  素材生成完成！")
    print(f"  输出目录: {assets_dir}")
    print("=" * 50)


if __name__ == "__main__":
    main()
