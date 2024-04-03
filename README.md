# PythonC8
Quick and dirty Chip-8 Emulator written in python, using pygame.

Requires python version 3.10 or higher due to the use of match (switch statements).

If this is a project you would like to undertake for yourself, I primarily used these resources:

[Chip-8 - Wikipedia](https://en.wikipedia.org/wiki/CHIP-8)

[Cowgod's Chip-8 Technical Reference](http://devernay.free.fr/hacks/chip8/C8TECH10.HTM)

[Timendus' Chip-8 Test Suite](https://github.com/Timendus/chip8-test-suite)

[How to write an emulator (CHIP-8 interpreter) by Laurence Muller](https://multigesture.net/articles/how-to-write-an-emulator-chip-8-interpreter/)


## Install guide:
The only dependency required for this project is pygame.
```bash
pip3 install pygame
```

## Launch:
The location of the rom file must be given as a command line argument.

Launch the emulator using the following command.
```bash
python3 ./run.py rom_file_path.ch8
```

## Licence
All code is provided as-is and is licensed under the [MIT](https://choosealicense.com/licenses/mit/) license.
