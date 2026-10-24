"""Genera icon.ico (T verde menta sobre fondo oscuro). Requiere Pillow."""
from PIL import Image, ImageDraw
S = 256
im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
d = ImageDraw.Draw(im)
d.rounded_rectangle((8, 8, S - 8, S - 8), 56, fill=(11, 15, 20, 255), outline=(94, 242, 176, 255), width=8)
d.rounded_rectangle((60, 66, 196, 100), 10, fill=(94, 242, 176, 255))
d.rounded_rectangle((110, 66, 146, 200), 10, fill=(94, 242, 176, 255))
d.ellipse((150, 150, 196, 196), fill=(79, 216, 255, 255))
im.save("icon.ico", sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
print("icon.ico listo")
