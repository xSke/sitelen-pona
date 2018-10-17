from io import BytesIO

from flask import Flask, abort, request, send_file
from PIL import Image, ImageDraw, ImageFont

home = """
"""

font = ImageFont.truetype("linjapona.otf", 30, layout_engine=ImageFont.LAYOUT_RAQM)
padding = 10
line_spacing = 10

def size_with_newlines(text):
    total_w = 0
    total_h = 0
    for line in text.split("\n"):
        line_w, line_h = font.getsize(line)
        total_w = max(total_w, line_w)
        total_h = total_h + line_h + line_spacing
    return (total_w, total_h - line_spacing)

def draw_with_newlines(draw, coords, text):
    draw_x, draw_y = coords
    for line in text.split("\n"):
        draw.text((draw_x, draw_y), line, font=font, fill=(0, 0, 0, 255), features=["liga"])
        draw_y += font.getsize(line)[1] + line_spacing

def render(text):
    size = size_with_newlines(text)
    size = (size[0] + padding * 2, size[1] + padding * 2)
    img = Image.new("RGBA", size, (255, 255, 255, 255))

    draw = ImageDraw.Draw(img)
    draw_with_newlines(draw, (padding, padding), text)

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
    return render(text)

@app.route("/", methods=["POST"])
def render_post():
    if request.content_length and request.content_length > 64*1024:
        abort(400)
    text = request.get_data(as_text=True)
    return render(text)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port="8000")