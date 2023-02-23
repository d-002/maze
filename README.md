# maze

![Logo](https://user-images.githubusercontent.com/69427207/220354305-eec77b99-6ca9-466c-9d82-48938836f4de.png)

Doom-like maze with randomly generated levels. School project.

## DISCLAIMER
If you want to download the game as an executable, **it is very likely that your antivirus software will see the game as a virus**.  
This is because I used a Python library to convert the file, and because I'm not a huge recognised firm that has money to spend in certificates and all that kind of stuff.

This game is **not** a virus, so if you want to play it, maybe disable your antivirus software when downloading it.

You can also consider **downloading the game as Python files** to avoid this issue completely.

## Trailer
https://youtu.be/k_p-beKNRV4

## Download

<details>
  <summary><h3>Download as Python files</h3></summary>
  
  Download all the files above.  
  Make sure you download all the required files (images, sound effects...), otherwise the game won't be able to run properly.
  
  You will need Python 3.x or newer, and a few Python modules available on `pip`. To install them, navigate to the game folder with a command prompt and execute: `pip install requirements.txt` (Windows: `py -m pip install requirements.txt`).
  
  The main file you will need to execute to play the game is `main.pyw`.
</details>

<details>
  <summary><h3>Download .exe binaries</h3></summary>
  
  Use the "releases" tab and download the latest version.
  
  Make sure you read the disclaimer above.
</details>

## Overview
This project is a Python game where you try to find the exit gate to a maze and go to the next level, where a bigger maze will be waiting for you. Yet beware, evil monsters will try and stop you from doing so!

There is an infinite amount of levels, with a random generation every time, generated by an algorithm coded for a school project.

Other than the main file, you can also find two other python files: `entities.py` (entities handling) and `maze.py` (maze generation).  
The remaining `.py` files were used in the development process in order to resize images. You don't need them.

## Handling and options
Pan with the mouse, left click to attack and right click to open doors.  
WASD to move around.

### Editing options
You can edit the file `files/options.txt` to change settings like the keys used to move (order: up, left, down, right), the FOV or the render distance.

You don't want to increase the render distance, as the fog will hide most of the far away parts of the maze.  
It is also very unlikely that long straight paths would generate, which would be the only reason why you would need high rander distance.  
I recommend to only change this setting if you want to lower it, for example if you are playing on a potato.

### Defaults
- **move_keys**: wasd
- **fov**: 70
- **render_distance**: 20

You can also delete the `options.txt` file to revert everything back to default.

## Sources

**Textures**: [doomworld.com](https://www.doomworld.com/forum/topic/99021-doom-neural-upscale-2x-v-10)  
**Music**: myself (youtube video will be available soon)  
**SFX**: edited from [pixabay.com](https://pixabay.com)  
