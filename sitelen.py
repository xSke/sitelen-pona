from io import BytesIO

from flask import Flask, abort, request, send_file
from PIL import Image, ImageDraw, ImageFont

# API:
# - GET /<text>
#   (optional .png extension ignored)
# - POST /
#   (POST data = <text>)
# Query params (for both endpoints):
# - size (font size) [int, clamped between 10 and 250]
# - padding (padding around text) [int, clamped between 0 and 500]

size_min = 10
size_max = 250
default_size = 30
padding_max = 500

font_sizes = {}
for size in range(size_min, size_max + 1):
    font = ImageFont.truetype("linjapona.otf", size, layout_engine=ImageFont.LAYOUT_RAQM)
    font_sizes[size] = font

def get_int_or_default(container, key, default):
    try:
        if key in container:
            return int(container[key])
        else:
            return default
    except ValueError:
        return default

def size_with_newlines(text, font, line_spacing):
    total_w = 0
    total_h = 0
    for line in text.split("\n"):
        line_w, line_h = font.getsize(line)
        total_w = max(total_w, line_w)
        total_h = total_h + line_h + line_spacing
    return (total_w, total_h - line_spacing)

def draw_with_newlines(draw, font, coords, text, line_spacing):
    draw_x, draw_y = coords
    for line in text.split("\n"):
        draw.text((draw_x, draw_y), line, font=font, fill=(0, 0, 0, 255), features=["liga"])
        draw_y += font.getsize(line)[1] + line_spacing

def parse_args():
    return (
        get_int_or_default(request.args, "size", default_size),
        get_int_or_default(request.args, "padding", None),
    )

def render(text, font_size, padding):
    font_size = int(min(max(font_size, size_min), size_max))
    font = font_sizes[font_size]

    if padding is None:
        padding = font_size // 3
    padding = max(min(padding, 500), 0)

    line_spacing = font_size // 3

    size = size_with_newlines(text, font, line_spacing)
    size = (size[0] + padding * 2, size[1] + padding * 2)
    img = Image.new("RGBA", size, (255, 255, 255, 255))

    draw = ImageDraw.Draw(img)
    draw_with_newlines(draw, font, (padding, padding), text, line_spacing)

    out = BytesIO()
    img.save(out, format="png")
    out.seek(0)

    return send_file(out, mimetype="image/png")

app = Flask(__name__)
@app.route("/")
def root():
    return send_file("index.html")

@app.route("/<path:text>")
def render_get(text):
    if text.endswith(".png"):
        text = text[:-4]
        
    font_size, padding = parse_args()
    return render(text, font_size, padding)

@app.route("/", methods=["POST"])
def render_post():
    if request.content_length and request.content_length > 64*1024:
        abort(400)
    text = request.get_data(as_text=True)
    font_size, padding = parse_args()
    return render(text, font_size, padding)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port="8000")