# Morse Code Beeper

Morse Code Beeper is a simple cross-platform script to generate morse code beep sound
with a cli interface.
Run `python morse_code_beeper.py --help` for more information.

You can also decode the sound using the [App](https://play.google.com/store/apps/details?id=org.jfedor.morsecode).

## Examples

Generate beep sound for text "Hello,world!" and plays it forever (you can exit by typing Ctrl+C).

```sh
python morse_code_beeper.py --text "Hello,world!" --forever
```

Save the sound to a wav file instead of playing it:

```sh
python morse_code_beeper.py --text "Hello,world!" --save a.wav --no-sound
```