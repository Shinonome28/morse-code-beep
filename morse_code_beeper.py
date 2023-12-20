from pydub import AudioSegment
from pydub.playback import play
import pydub.generators
import click
from base64 import b32encode

TEST_STRING_ = "the quick brown fox jumps over the lazy dog 0123456789"

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

WAVE_GENERATORS_: dict[str, pydub.generators.SignalGenerator] = {
    "sin": pydub.generators.Sine,
    "square": pydub.generators.Square,
    "sawtooth": pydub.generators.Sawtooth,
}

AVAILABLE_GENERATORS_ = list(WAVE_GENERATORS_.keys())


def Encode(data: str, /, ignore_illegal_character) -> str:
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


def generate_silence_sound(duration) -> AudioSegment:
    return AudioSegment.silent(duration=duration * 1000)


def Play(data: str, wpm: int, freq: int, /, loop: bool, save: str, wave: str):
    interval = 60 / (50 * wpm) * 1000
    sine_sound_1 = WAVE_GENERATORS_[wave](
        freq, sample_rate=44100, bit_depth=16
    ).to_audio_segment(duration=interval)
    sine_sound_3 = WAVE_GENERATORS_[wave](
        freq, sample_rate=44100, bit_depth=16
    ).to_audio_segment(duration=interval * 3)
    silence = AudioSegment.silent(duration=interval)

    audio = AudioSegment.empty()

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
        format = None
        t = save.split(".")
        if len(t) < 2:
            format = "wav"
        else:
            format = t[-1]
        audio.export(save, format)

    if loop:
        while True:
            play(audio)
            play(silence * 7)
    else:
        play(audio)


@click.command()
@click.option(
    "-t",
    "--text",
    help="The text to be converted. If not specified, will use the default test string.",
    default=TEST_STRING_,
)
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
@click.option(
    "--save",
    default="",
    help="Save the audio to a file. Automatically detect format by extension name.",
)
@click.option(
    "--wave",
    default="sin",
    type=click.Choice(AVAILABLE_GENERATORS_),
)
@click.option(
    "--base32/--no-base32",
    default=False,
    help="Encode the text in base32 before converting to morse code.",
)
def main(text, freq, wpm, loop, decode, sound, ignore_illegal, save, wave, base32):
    """
    Play beep sound in morse code.
    """
    if base32:
        text = b32encode(text.encode("utf8")).decode("ascii")
    text = text.lower()
    data = Encode(text, ignore_illegal_character=ignore_illegal)
    if decode:
        print(data)
    if sound:
        Play(data, wpm, freq, loop=loop, save=save, wave=wave)


if __name__ == "__main__":
    main()
