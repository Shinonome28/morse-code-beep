from io import BytesIO
from pydub import AudioSegment
from pydub.playback import play
import click

DOT_ = "."
DASH_ = "-"
SLASH_ = "/"
SPACE_ = " "

TRANSLATE_: dict[str, tuple[str, ...]] = {
    "a": (DOT_, DASH_),
    "b": (DASH_, DOT_, DOT_, DOT_),
    "c": (DASH_, DOT_, DASH_, DOT_),
    "d": (DASH_, DOT_, DOT_),
    "e": (DOT_,),
    "f": (DOT_, DOT_, DASH_, DOT_),
    "g": (DASH_, DASH_, DOT_),
    "h": (DOT_, DOT_, DOT_, DOT_),
    "i": (DOT_, DOT_),
    "j": (DOT_, DASH_, DASH_, DASH_),
    "k": (DASH_, DOT_, DASH_),
    "l": (DOT_, DASH_, DOT_, DOT_),
    "m": (DASH_, DASH_),
    "n": (DASH_, DOT_),
    "o": (DASH_, DASH_, DASH_),
    "p": (DOT_, DASH_, DASH_, DOT_),
    "q": (DASH_, DASH_, DOT_, DASH_),
    "r": (DOT_, DASH_, DOT_),
    "s": (DOT_, DOT_, DOT_),
    "t": (DASH_,),
    "u": (DOT_, DOT_, DASH_),
    "v": (DOT_, DOT_, DOT_, DASH_),
    "w": (DOT_, DASH_, DASH_),
    "x": (DASH_, DOT_, DOT_, DASH_),
    "y": (DASH_, DOT_, DASH_, DASH_),
    "z": (DASH_, DASH_, DOT_, DOT_),
    "0": (DASH_, DASH_, DASH_, DASH_, DASH_),
    "1": (DOT_, DASH_, DASH_, DASH_, DASH_),
    "2": (DOT_, DOT_, DASH_, DASH_, DASH_),
    "3": (DOT_, DOT_, DOT_, DASH_, DASH_),
    "4": (DOT_, DOT_, DOT_, DOT_, DASH_),
    "5": (DOT_, DOT_, DOT_, DOT_, DOT_),
    "6": (DASH_, DOT_, DOT_, DOT_, DOT_),
    "7": (DASH_, DASH_, DOT_, DOT_, DOT_),
    "8": (DASH_, DASH_, DASH_, DOT_, DOT_),
    "9": (DASH_, DASH_, DASH_, DASH_, DOT_),
    ".": (DOT_, DASH_, DOT_, DASH_, DOT_, DASH_),
    ",": (DASH_, DASH_, DOT_, DOT_, DASH_, DASH_),
    "?": (DOT_, DOT_, DASH_, DASH_, DOT_, DOT_),
    "!": (DASH_, DOT_, DASH_, DOT_, DASH_, DASH_),
    ":": (DASH_, DASH_, DASH_, DOT_, DOT_, DOT_),
    ";": (DASH_, DOT_, DASH_, DOT_, DASH_, DOT_),
    "(": (DASH_, DOT_, DASH_, DASH_, DOT_),
    ")": (DASH_, DOT_, DASH_, DASH_, DOT_, DASH_),
    "=": (DASH_, DOT_, DOT_, DOT_, DASH_),
    "+": (DOT_, DASH_, DOT_, DASH_, DOT_),
    "-": (DASH_, DOT_, DOT_, DOT_, DOT_, DASH_),
    "_": (DOT_, DOT_, DASH_, DASH_, DOT_, DASH_),
    '"': (DOT_, DASH_, DOT_, DOT_, DASH_, DOT_),
    "$": (DOT_, DOT_, DOT_, DASH_, DOT_, DOT_, DASH_),
    "@": (DOT_, DASH_, DASH_, DOT_, DASH_, DOT_),
    "&": (DOT_, DASH_, DOT_, DOT_, DOT_),
    "/": (DASH_, DOT_, DOT_, DASH_, DOT_),
    "\\": (DASH_, DOT_, DOT_, DASH_, DOT_, DASH_),
    "'": (DOT_, DASH_, DASH_, DASH_, DASH_, DOT_),
}

LEGAL_CHARACTER_SET_ = set(TRANSLATE_.keys())


def Encode(data: str, /, ignore_illegal_character, to_lower=True) -> str:
    if to_lower:
        data = data.lower()
    res = []
    for ch in data:
        if not (ch in LEGAL_CHARACTER_SET_ or ch.isspace()):
            if ignore_illegal_character:
                continue
            else:
                raise ValueError("Illegal character: " + ch)
        if ch.isspace():
            res.append(SLASH_)
        else:
            res.extend(TRANSLATE_[ch.lower()])
            res.append(SPACE_)
    return "".join(res)


def generate_sin_sound(freq, duration) -> AudioSegment:
    import numpy as np
    from scipy.io.wavfile import write

    sampling_rate = 44100
    t = np.arange(int(sampling_rate * duration)) / float(sampling_rate)
    sin_wave = np.sin(2 * np.pi * freq * t)
    sin_wave_int = np.int16(sin_wave * 32767)
    memory_buffer = BytesIO()
    write(memory_buffer, sampling_rate, sin_wave_int)
    return AudioSegment.from_wav(memory_buffer)


def generate_silence_sound(duration) -> AudioSegment:
    return AudioSegment.silent(duration=duration * 1000)


def Play(data: str, wpm: int, freq: int, /, loop: bool, save: str):
    interval = 60 / (50 * wpm)
    sine_sound_1 = generate_sin_sound(freq, interval)
    sine_sound_3 = generate_sin_sound(freq, interval * 3)
    silence = generate_silence_sound(interval)

    audio = AudioSegment.silent(0)

    add_silence = False
    for i in data:
        if i == DOT_:
            if add_silence:
                audio += silence
            else:
                add_silence = True
            audio += sine_sound_1
        elif i == DASH_:
            if add_silence:
                audio += silence
            else:
                add_silence = True
            audio += sine_sound_3
        elif i == SPACE_:
            audio += silence * 3
            add_silence = False
        elif i == SLASH_:
            audio += silence * 7
            add_silence = False

    if save != "":
        audio.export(save, "wav")

    if loop:
        while True:
            play(audio)
            play(silence * 7)
    else:
        play(audio)


@click.command()
@click.option("-t", "--text", help="the text to be converted", prompt="Enter text")
@click.option("-f", "--freq", default=550, help="the frequency of generated sound")
@click.option(
    "--wpm",
    default=20,
    help="the speed, measured in how many units in a second (a unit is 50 beeps)",
)
@click.option("--loop/--no-loop", default=False, help="play the sound forever")
@click.option(
    "--decode/--no-decode",
    default=False,
    help="print morse code representation for the text",
)
@click.option(
    "--sound/--no-sound", default=True, help="Do not play the sound, exit immediately"
)
@click.option(
    "--ignore-illegal/--no-ignore-illegal",
    default=False,
    help="Do not exit when reading illegal character.",
)
@click.option("--save", default="", help="save the audio to a file")
def main(text, freq, wpm, loop, decode, sound, ignore_illegal, save):
    """
    Play beep sound in morse code.
    """
    data = Encode(text, ignore_illegal_character=ignore_illegal)
    if decode:
        print(data)
    if sound:
        Play(data, wpm, freq, loop=loop, save=save)


if __name__ == "__main__":
    main()
