# gif_utils.py
from PIL import Image
from io import BytesIO


def create_gif_in_memory(images_data_list, duration_ms=500):
    if len(images_data_list) < 2:
        return None

    frames = []
    for bin_data in images_data_list:
        try:
            img = Image.open(BytesIO(bin_data))
            frames.append(img.convert("RGBA"))
        except Exception as e:
            print("Błąd odczytu klatki PIL:", e)

    if len(frames) < 2:
        return None

    gif_buffer = BytesIO()
    frames[0].save(
        gif_buffer,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration=duration_ms,
        loop=0
    )
    gif_buffer.seek(0)
    return gif_buffer
