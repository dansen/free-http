import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw
import io

def svg_to_png(svg_path, png_path, size=(256, 256)):
    # 解析 SVG 文件
    tree = ET.parse(svg_path)
    root = tree.getroot()

    # 创建新的 PNG 图像
    img = Image.new('RGBA', size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    # 获取 SVG 中的矩形或路径
    for elem in root.findall('.//{http://www.w3.org/2000/svg}rect'):
        x = float(elem.get('x', 0))
        y = float(elem.get('y', 0))
        width = float(elem.get('width', 0))
        height = float(elem.get('height', 0))
        fill = elem.get('fill', '#000000')
        
        # 按比例缩放
        scale_x = size[0] / float(root.get('width', size[0]))
        scale_y = size[1] / float(root.get('height', size[1]))
        
        draw.rectangle([
            x * scale_x, 
            y * scale_y, 
            (x + width) * scale_x, 
            (y + height) * scale_y
        ], fill=fill)

    for elem in root.findall('.//{http://www.w3.org/2000/svg}path'):
        d = elem.get('d', '')
        fill = elem.get('fill', '#000000')
        # 简单处理路径（这里只是绘制一个近似形状）
        draw.ellipse([50, 50, 200, 200], fill=fill)

    # 保存 PNG 文件
    img.save(png_path)

# 转换 API 列表图标
svg_to_png(
    'd:/Sources/free-http/src/assets/icons/api_list.svg', 
    'd:/Sources/free-http/src/assets/icons/api_list.png'
)

# 转换历史记录图标
svg_to_png(
    'd:/Sources/free-http/src/assets/icons/history.svg', 
    'd:/Sources/free-http/src/assets/icons/history.png'
)

print("SVG 转换完成")
