Before running the Q1 Image Editor code, make sure you have installed these Python libraries
pip install pillow opencv-python numpy tkinterdnd2

Image Loading Might Fail
Your error:

text ImportError: libGL.so.1: cannot open shared object file: No such file or directory

means OpenCV cannot find the OpenGL library needed for image decoding and display.
This is a system-level problem, not a code bug.

On Windows or macOS:
This error is rare. If you see it, ensure Python and OpenCV are installed from official sources.

How to Fix
On Ubuntu/Debian (Linux):

bash
sudo apt-get update
sudo apt-get install libgl1
On Fedora/RHEL:

bash
sudo dnf install mesa-libGL
On Arch Linux:

bash
sudo pacman -S mesa

Application usage
Load Image (CTRL+O)
Save Image (CTRL+S)
Undo Image (CTRL+Z)
Redo Image (CTRL+Y)
Reset click on reset button
Use mouse for croping
Resize cropped image use the slider
