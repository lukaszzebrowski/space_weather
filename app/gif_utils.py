# gif_utils.py
from PIL import Image
from io import BytesIO


def create_gif_in_memory(images_data_list, duration_ms=500):
    """
    Tworzy animowanego GIF-a w pamięci, korzystając z Pillow (PIL).
    Zwraca obiekt BytesIO lub None, jeśli brak klatek albo nie udało się utworzyć animacji.

    Parametry:
    - images_data_list: lista bajtów (każdy element to np. zawartość pliku .jpg/.png)
    - duration_ms: czas w milisekundach wyświetlania każdej klatki (Pillow wymaga ms).
    """
    if len(images_data_list) < 2:
        # co najmniej 2 klatki, by mieć animację
        return None

    frames = []
    for bin_data in images_data_list:
        try:
            img = Image.open(BytesIO(bin_data))
            # Konwertujemy do 'RGBA' lub 'RGB' w razie mieszanych formatów
            frames.append(img.convert("RGBA"))
        except Exception as e:
            print("Błąd odczytu klatki PIL:", e)

    if len(frames) < 2:
        return None  # brak wystarczających klatek

    gif_buffer = BytesIO()
    # frames[0].save(...) tworzy animację:
    frames[0].save(
        gif_buffer,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration=duration_ms,  # w milisekundach
        loop=0  # 0 => nieskończona pętla
    )
    gif_buffer.seek(0)
    return gif_buffer
