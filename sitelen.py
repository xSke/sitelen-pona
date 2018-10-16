from io import BytesIO

from flask import Flask, abort, request, send_file
from PIL import Image, ImageDraw, ImageFont

home = """
ilo pi sitelen pona
===================

ni li ilo. ilo ni li ken pali e sitelen pona tan lipu pona.

pali tan jan Asata"""

font = ImageFont.truetype("linjapona.otf", 30, layout_engine=ImageFont.LAYOUT_RAQM)
def render(text):
    padding = 10

    size = font.getsize(text)
    size = (size[0] + padding * 2, size[1] + padding * 2)
    img = Image.new("RGBA", size, (255, 255, 255, 255))

    draw = ImageDraw.Draw(img)
    draw.text((padding, padding), text, font=font, fill=(0, 0, 0, 255), features=["liga"])

    out = BytesIO()
    img.save(out, format="png")
    out.seek(0)

    return send_file(out, mimetype="image/png")

app = Flask(__name__)
@app.route("/")
def root():
    return "<pre>{}</pre>".format(home)

@app.route("/<path:text>")
def render_get(text):
    return render(text)

@app.route("/", methods=["POST"])
def render_post():
    if request.content_length > 64*1024:
        abort(400)
    text = request.get_data(as_text=True)
    return render(text)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port="8000")