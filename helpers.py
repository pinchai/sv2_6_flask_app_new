import os
import uuid
from werkzeug.utils import secure_filename

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "static", "images")
os.makedirs(UPLOAD_DIR, exist_ok=True)
ALLOWED_EXT = {"png", "jpg", "jpeg", "gif", "webp"}


def allowed(name):
    return bool(name and "." in name and name.rsplit(".", 1)[-1].lower() in ALLOWED_EXT)


def save_image(file):
    if not file or not file.filename or not allowed(file.filename):
        return None

    ext = file.filename.rsplit(".", 1)[-1].lower()
    raw_name = secure_filename(file.filename.rsplit(".", 1)[0])
    if not raw_name:
        raw_name = f"image_{uuid.uuid4().hex[:8]}"

    filename = f"{raw_name}.{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    if os.path.exists(file_path):
        filename = f"{raw_name}_{uuid.uuid4().hex[:8]}.{ext}"
        file_path = os.path.join(UPLOAD_DIR, filename)

    file.save(file_path)
    return filename
