from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import os
import random
import subprocess
import sys
import time

import requests

sys.path.insert(0, os.path.expanduser("~/Whisplay/apps/pisugar-wx"))
from src.display import Display

W, H = 280, 240
ROTATION = Image.Transpose.ROTATE_270

LAT = "44.9778"
LON = "-93.2650"
OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY")

ASSET_DIR = "assets"
WEATHER_DIR = f"{ASSET_DIR}/display/weather"
DATETIME_DIR = f"{ASSET_DIR}/display/date_time"
MOON_DIR = f"{ASSET_DIR}/display/moonphases"
SOUND_WEATHER_DIR = f"{ASSET_DIR}/audio/weather"

HALLWAY_BG = f"{ASSET_DIR}/hallway.png"
DOJIMA_SHEET = f"{WEATHER_DIR}/sheet_dojima_residence.png"
BARSWOOPCIRCLE = f"{ASSET_DIR}/display/fixed_template/persona_weather_layout.png"
WEATHER_ICONS = f"{WEATHER_DIR}/sheet_weathericons_100px.png"
DAYTIME_LABELS = f"{DATETIME_DIR}/sheet_daytimes.png"
WEEKDAYS = f"{DATETIME_DIR}/sheet_weekdays.png"
DIGITS = f"{DATETIME_DIR}/sheet_digits.png"
DATESLASH = f"{DATETIME_DIR}/dateslash.png"
MOON_PHASES = f"{MOON_DIR}/sheet_moonphases_v250px.png"
FONTSONA = f"{ASSET_DIR}/display/Fontsona4Golden.ttf"

STARTUP_WAV = f"{ASSET_DIR}/audio/affirmation/overnight.wav"
EXPAND_WAV = f"{ASSET_DIR}/audio/ui/sparkly expand.wav"
ERROR_WAV = f"{ASSET_DIR}/audio/ui/error.wav"
SHRINK_WAV = f"{ASSET_DIR}/audio/ui/low shrink.wav"

NEWS_CIRCLE = f"{ASSET_DIR}/weather news circle.png"
WEATHERNEWS_TITLE = f"{ASSET_DIR}/WEATHERNEWS_title.png"

RAIN_LOOP = f"{SOUND_WEATHER_DIR}/rain_tinroof.mp3"
THUNDER_SOUNDS = [
    f"{SOUND_WEATHER_DIR}/heavythunder.wav",
    f"{SOUND_WEATHER_DIR}/mediumthunder.wav",
    f"{SOUND_WEATHER_DIR}/lightthunder.wav",
]

AUDIO_CARD = "wm8960soundcard"
AUDIO_DEVICE = "plughw:wm8960soundcard"

DAYTIME_W, DAYTIME_H = 128, 32
WEEKDAY_W, WEEKDAY_H = 50, 20
DIGIT_W, DIGIT_H = 33, 35
WEATHER_W, WEATHER_H = 100, 100
MOON_W, MOON_H = 50, 50
BG_W, BG_H = 280, 240

DAYTIME_MAP = {
    "early_morning": 0,
    "morning": 1,
    "lunchtime": 2,
    "daytime": 3,
    "afternoon": 4,
    "after_school": 5,
    "evening": 6,
}

WEEKDAY_MAP = {
    "mon": 0,
    "tue": 1,
    "wed": 2,
    "thu": 3,
    "fri": 4,
    "sat": 5,
    "sun": 6,
}

WEATHER_MAP = {
    "sun": 0,
    "snow": 1,
    "rain": 2,
    "storm": 3,
    "moon": 4,
    "fog": 5,
    "snow_rain": 6,
    "heavyrain": 7,
    "cloudy": 8,
    "partly_cloudy": 9,
}

DOJIMA_MAP = {
    "fog": 0,
    "cloudy": 1,
    "sunset": 2,
    "evening": 3,
    "rain": 4,
    "sun": 5,
    "snow": 6,
    "snowing": 7,
}

MOON_MAP = {
    "newmoon": 0,
    "waxingcrescent": 1,
    "firstquarter": 2,
    "waxinggibbous": 3,
    "full": 4,
    "waninggibbous": 5,
    "thirdquarter": 6,
    "waningcrescent": 7,
}


def setup_audio():
    subprocess.run(["amixer", "-D", AUDIO_CARD, "sset", "Speaker", "121"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["amixer", "-D", AUDIO_CARD, "sset", "Playback", "230"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def play_wav(path, blocking=False):
    if not os.path.exists(path):
        print(f"Missing sound: {path}")
        return None

    cmd = ["aplay", "-D", AUDIO_DEVICE, path]
    if blocking:
        return subprocess.run(cmd)
    return subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def start_rain_loop():
    if not os.path.exists(RAIN_LOOP):
        print(f"Rain loop missing: {RAIN_LOOP}")
        return None

    return subprocess.Popen(
        ["mpg123", "-q", "-a", AUDIO_DEVICE, "--loop", "-1", RAIN_LOOP],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def stop_process(proc):
    if proc and proc.poll() is None:
        proc.terminate()


def play_random_thunder():
    existing = [path for path in THUNDER_SOUNDS if os.path.exists(path)]
    if existing:
        play_wav(random.choice(existing))


def show(display, image):
    display.show_image(image.transpose(ROTATION))


def crop_horizontal(path, index, cell_w, cell_h):
    sheet = Image.open(path).convert("RGBA")
    return sheet.crop((index * cell_w, 0, (index + 1) * cell_w, cell_h))


def crop_vertical(path, index, cell_w, cell_h):
    sheet = Image.open(path).convert("RGBA")
    return sheet.crop((0, index * cell_h, cell_w, (index + 1) * cell_h))


def get_daytime():
    hour = datetime.now().hour

    if 5 <= hour < 8:
        return "early_morning"
    if 8 <= hour < 12:
        return "morning"
    if 12 <= hour < 13:
        return "lunchtime"
    if 13 <= hour < 15:
        return "afternoon"
    if 15 <= hour < 20:
        return "after_school"

    return "evening"


def map_openweather_to_persona(weather_id, main, description):
    if 200 <= weather_id < 300:
        return "storm"
    if 300 <= weather_id < 400:
        return "rain"
    if 500 <= weather_id < 600:
        return "heavyrain" if weather_id >= 502 else "rain"
    if 600 <= weather_id < 700:
        return "snow_rain" if "rain" in description or "sleet" in description else "snow"
    if 700 <= weather_id < 800:
        return "fog"
    if weather_id == 800:
        return "sun"
    if weather_id == 801:
        return "partly_cloudy"
    if 802 <= weather_id < 900:
        return "cloudy"

    if "thunder" in main or "thunder" in description:
        return "storm"
    if "rain" in main or "drizzle" in main:
        return "rain"
    if "snow" in main:
        return "snow"
    if "cloud" in main:
        return "cloudy"

    return "sun"


def fetch_weather():
    if not OPENWEATHER_API_KEY:
        return {
            "ok": False,
            "error": "OPENWEATHER_API_KEY not set",
            "weather_key": "sun",
            "weather_id": 800,
            "description": "fallback",
            "sunset": None,
        }

    try:
        response = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={
                "lat": LAT,
                "lon": LON,
                "appid": OPENWEATHER_API_KEY,
                "units": "imperial",
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        weather = data["weather"][0]
        weather_id = int(weather["id"])
        main = weather["main"].lower()
        description = weather["description"].lower()
        sunset = data.get("sys", {}).get("sunset")

        weather_key = map_openweather_to_persona(weather_id, main, description)

        print(f"Weather OK: {weather_key} / {weather_id} / {description}")

        return {
            "ok": True,
            "error": None,
            "weather_key": weather_key,
            "weather_id": weather_id,
            "description": description,
            "sunset": sunset,
        }

    except Exception as e:
        msg = str(e)
        print(f"Weather fetch failed: {msg}")
        return {
            "ok": False,
            "error": msg,
            "weather_key": "sun",
            "weather_id": 800,
            "description": "fallback",
            "sunset": None,
        }


def is_after_sunset(sunset_epoch):
    if sunset_epoch is None:
        hour = datetime.now().hour
        return hour >= 20 or hour < 5

    return time.time() >= sunset_epoch


def is_near_sunset(sunset_epoch):
    if sunset_epoch is None:
        hour = datetime.now().hour
        return 17 <= hour < 20

    seconds_until_sunset = sunset_epoch - time.time()
    return 0 <= seconds_until_sunset <= 2 * 60 * 60


def display_weather_key(weather_key, sunset_epoch):
    if weather_key == "sun" and is_after_sunset(sunset_epoch):
        return "moon"
    return weather_key


def get_dojima_background(weather_key, sunset_epoch):
    if is_after_sunset(sunset_epoch):
        if weather_key in ("snow", "snow_rain"):
            return "snowing"
        return "evening"

    if weather_key == "sun":
        if is_near_sunset(sunset_epoch):
            return "sunset"
        return "sun"

    if weather_key in ("rain", "heavyrain", "storm"):
        return "rain"
    if weather_key in ("snow", "snow_rain"):
        return "snow"
    if weather_key == "fog":
        return "fog"
    if weather_key in ("cloudy", "partly_cloudy"):
        return "cloudy"

    return "sun"


def paste_digit(scene, digit, x, y, scale=1.0):
    img = crop_horizontal(DIGITS, int(digit), DIGIT_W, DIGIT_H)

    if scale != 1.0:
        img = img.resize((int(DIGIT_W * scale), int(DIGIT_H * scale)), Image.Resampling.LANCZOS)

    scene.paste(img, (x, y), img)


def paste_two_digit_number(scene, number, x, y, scale=1.0, spacing=-3):
    text = f"{number:02d}"
    step = int(DIGIT_W * scale) + spacing

    paste_digit(scene, text[0], x, y, scale)
    paste_digit(scene, text[1], x + step, y, scale)


def load_font(size):
    try:
        return ImageFont.truetype(FONTSONA, size)
    except Exception:
        return ImageFont.load_default()


def render(weather_state):
    now = datetime.now()
    weather_key = weather_state["weather_key"]
    sunset = weather_state["sunset"]

    scene = Image.new("RGB", (W, H), (0, 0, 0))

    bg_key = get_dojima_background(weather_key, sunset)
    bg = crop_horizontal(DOJIMA_SHEET, DOJIMA_MAP[bg_key], BG_W, BG_H).convert("RGB")
    scene.paste(bg, (0, 0))

    overlay = Image.open(BARSWOOPCIRCLE).convert("RGBA")
    scene.paste(overlay, (0, 0), overlay)

    weekday_key = now.strftime("%a").lower()
    weekday = crop_vertical(WEEKDAYS, WEEKDAY_MAP[weekday_key], WEEKDAY_W, WEEKDAY_H)
    weekday = weekday.resize((75, 30), Image.Resampling.LANCZOS)
    scene.paste(weekday, (170, 26), weekday)

    paste_two_digit_number(scene, now.month, 28, 32, scale=0.75, spacing=-2)

    slash = Image.open(DATESLASH).convert("RGBA")
    slash = slash.resize((14, 26), Image.Resampling.LANCZOS)
    scene.paste(slash, (70, 32), slash)

    paste_two_digit_number(scene, now.day, 82, 32, scale=0.75, spacing=-2)

    daytime_key = get_daytime()
    daytime = crop_vertical(DAYTIME_LABELS, DAYTIME_MAP[daytime_key], DAYTIME_W, DAYTIME_H)
    daytime = daytime.resize((166, 42), Image.Resampling.LANCZOS)
    scene.paste(daytime, (28, 68), daytime)

    icon_key = display_weather_key(weather_key, sunset)
    weather_icon = crop_horizontal(
        WEATHER_ICONS,
        WEATHER_MAP.get(icon_key, WEATHER_MAP["sun"]),
        WEATHER_W,
        WEATHER_H,
    )
    weather_icon = weather_icon.resize((92, 92), Image.Resampling.LANCZOS)
    scene.paste(weather_icon, (124, 137), weather_icon)

    try:
        print(f"Moon sheet size: {Image.open(MOON_PHASES).size}")
        moon = crop_horizontal(MOON_PHASES, MOON_MAP["waxinggibbous"], MOON_W, MOON_H)
        moon = moon.resize((54, 54), Image.Resampling.LANCZOS)
        scene.paste(moon, (224, 4), moon)
    except Exception as e:
        print(f"Moon render failed: {e}")

    return scene


def render_error_overlay(base, message):
    layer = Image.new("RGBA", (W, H), (120, 0, 0, 150))
    draw = ImageDraw.Draw(layer)

    font_big = load_font(22)
    font_small = load_font(15)

    draw.rectangle((22, 58, 258, 176), fill=(40, 0, 0, 210), outline=(255, 255, 255, 230), width=2)
    draw.text((38, 72), "ERROR", font=font_big, fill=(255, 255, 255, 255))

    wrapped = []
    words = message.split()
    line = ""
    for word in words:
        test = f"{line} {word}".strip()
        if len(test) > 28:
            wrapped.append(line)
            line = word
        else:
            line = test
    if line:
        wrapped.append(line)

    for i, line in enumerate(wrapped[:4]):
        draw.text((38, 106 + i * 16), line, font=font_small, fill=(255, 255, 255, 255))

    output = base.convert("RGBA")
    output.alpha_composite(layer)
    return output.convert("RGB")


def show_error_sequence(display, base, message):
    play_wav(ERROR_WAV)

    for alpha in range(0, 181, 45):
        frame = base.convert("RGBA")
        overlay = render_error_overlay(base, message).convert("RGBA")
        overlay.putalpha(alpha)
        frame.alpha_composite(overlay)
        show(display, frame.convert("RGB"))
        time.sleep(0.05)

    error_frame = render_error_overlay(base, message)
    show(display, error_frame)
    time.sleep(2.0)

    play_wav(SHRINK_WAV)

    for alpha in range(180, -1, -45):
        frame = base.convert("RGBA")
        overlay = render_error_overlay(base, message).convert("RGBA")
        overlay.putalpha(alpha)
        frame.alpha_composite(overlay)
        show(display, frame.convert("RGB"))
        time.sleep(0.05)

    show(display, base)


def center_paste(scene, img):
    x = (scene.width - img.width) // 2
    y = (scene.height - img.height) // 2
    scene.paste(img, (x, y), img)


def startup_sequence(display):
    play_wav(STARTUP_WAV)

    circle = Image.open(NEWS_CIRCLE).convert("RGBA")
    title = Image.open(WEATHERNEWS_TITLE).convert("RGBA")

    hallway = Image.open(HALLWAY_BG).convert("RGB")
    hallway = hallway.resize((W, H), Image.Resampling.LANCZOS)

    circle = circle.resize((160, 160), Image.Resampling.LANCZOS)
    title = title.resize((220, int(title.height * (220 / title.width))), Image.Resampling.LANCZOS)

    for i in range(24):
        alpha = min(255, int(i / 12 * 255))
        angle = i * 6

        scene = hallway.copy()

        rotated = circle.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
        rotated.putalpha(rotated.getchannel("A").point(lambda p: int(p * alpha / 255)))

        title_fade = title.copy()
        title_fade.putalpha(title_fade.getchannel("A").point(lambda p: int(p * alpha / 255)))

        center_paste(scene, rotated)
        scene.paste(title_fade, ((W - title_fade.width) // 2, 93), title_fade)

        show(display, scene)
        time.sleep(0.055)


def fade_to_app(display, app_image):
    play_wav(EXPAND_WAV)

    white = Image.new("RGB", (W, H), (255, 255, 255))

    for i in range(12):
        alpha = int((i + 1) / 12 * 255)
        frame = Image.blend(white, app_image, alpha / 255)
        show(display, frame)
        time.sleep(0.045)


def main():
    setup_audio()
    display = Display()

    startup_sequence(display)

    weather_state = fetch_weather()
    image = render(weather_state)

    fade_to_app(display, image)

    if not weather_state["ok"]:
        show_error_sequence(display, image, weather_state["error"] or "Weather fetch failed")

    rain_proc = None
    if weather_state["weather_key"] in ("rain", "heavyrain", "storm"):
        rain_proc = start_rain_loop()

    try:
        if weather_state["weather_key"] == "storm":
            next_thunder = time.time() + random.randint(45, 180)
        else:
            next_thunder = None

        last_weather_refresh = time.time()

        while True:
            now = time.time()

            if now - last_weather_refresh >= 15 * 60:
                weather_state = fetch_weather()
                image = render(weather_state)
                show(display, image)
                last_weather_refresh = now

                if rain_proc:
                    stop_process(rain_proc)
                    rain_proc = None

                if weather_state["weather_key"] in ("rain", "heavyrain", "storm"):
                    rain_proc = start_rain_loop()

                if weather_state["weather_key"] == "storm":
                    next_thunder = now + random.randint(45, 180)
                else:
                    next_thunder = None

            if next_thunder and now >= next_thunder:
                play_random_thunder()
                next_thunder = now + random.randint(90, 360)

            time.sleep(10)

    finally:
        stop_process(rain_proc)
        try:
            display.clear()
            display.set_brightness(0)
        except Exception as e:
            print(f"Display cleanup failed: {e}")


if __name__ == "__main__":
    main()
