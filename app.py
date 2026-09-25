from flask import Flask, render_template, request, jsonify, send_file
from PIL import Image
import os
import io
import uuid

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/compress", methods=["POST"])
def compress_image():

    try:
        # Check image
        if "image" not in request.files:
            return jsonify({
                "success": False,
                "message": "No image uploaded"
            })

        file = request.files["image"]

        if file.filename == "":
            return jsonify({
                "success": False,
                "message": "No image selected"
            })

        # Target size
        target_size = float(request.form.get("targetSize", 0))
        unit = request.form.get("unit", "KB")

        if target_size <= 0:
            return jsonify({
                "success": False,
                "message": "Enter a valid target size"
            })

        # Convert target to bytes
        if unit == "MB":
            target_bytes = int(target_size * 1024 * 1024)
        else:
            target_bytes = int(target_size * 1024)

        # Open image
        image = Image.open(file)

        # Convert unsupported modes
        if image.mode in ("RGBA", "P"):
            background = Image.new("RGB", image.size, "white")

            if image.mode == "P":
                image = image.convert("RGBA")

            background.paste(
                image,
                mask=image.getchannel("A") if image.mode == "RGBA" else None
            )

            image = background

        else:
            image = image.convert("RGB")

        # Original size
        file.seek(0)
        original_data = file.read()
        original_size = len(original_data)

        # Generate unique filename
        output_name = f"{uuid.uuid4().hex}.jpg"
        output_path = os.path.join(UPLOAD_FOLDER, output_name)

        # If already smaller than target
        if original_size <= target_bytes:

            image.save(
                output_path,
                "JPEG",
                quality=95,
                optimize=True
            )

        else:

            # Try different JPEG qualities
            best_data = None

            for quality in range(95, 5, -5):

                buffer = io.BytesIO()

                image.save(
                    buffer,
                    format="JPEG",
                    quality=quality,
                    optimize=True
                )

                data = buffer.getvalue()

                if len(data) <= target_bytes:
                    best_data = data
                    break

                best_data = data

            # If quality alone isn't enough,
            # gradually reduce dimensions.
            if len(best_data) > target_bytes:

                current_image = image

                while len(best_data) > target_bytes:

                    new_width = int(current_image.width * 0.85)
                    new_height = int(current_image.height * 0.85)

                    if new_width < 100 or new_height < 100:
                        break

                    current_image = current_image.resize(
                        (new_width, new_height),
                        Image.Resampling.LANCZOS
                    )

                    for quality in range(90, 5, -5):

                        buffer = io.BytesIO()

                        current_image.save(
                            buffer,
                            format="JPEG",
                            quality=quality,
                            optimize=True
                        )

                        data = buffer.getvalue()

                        best_data = data

                        if len(data) <= target_bytes:
                            break

                    if len(best_data) <= target_bytes:
                        break

            with open(output_path, "wb") as output:
                output.write(best_data)

        compressed_size = os.path.getsize(output_path)

        reduction = (
            (original_size - compressed_size)
            / original_size
        ) * 100

        return jsonify({
            "success": True,
            "message": "Image compressed successfully",
            "originalSize": original_size,
            "compressedSize": compressed_size,
            "reduction": round(reduction, 2),
            "downloadUrl": f"/download/{output_name}"
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        })


@app.route("/download/<filename>")
def download(filename):

    path = os.path.join(UPLOAD_FOLDER, filename)

    if not os.path.exists(path):
        return "File not found", 404

    return send_file(
        path,
        as_attachment=True,
        download_name="compressed_image.jpg"
    )


if __name__ == "__main__":
    app.run(debug=True)