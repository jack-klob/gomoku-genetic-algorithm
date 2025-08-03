# gomoku-genetic-algorithm

### Instructions for compilation of template agent executable via PyInstaller, provided by agent template creator:

The Piskvork manager is a Win32 application and currently supports only Win32 compatible .exe files (furthermore whose name starts with pbrain- prefix). There are several ways how to create .exe from Python files.

Here I present the approach using PyInstaller and Windows command line:

1. Install Windows (or Wine for Linux, originally the project was created and tested on Ubuntu 16.04 using Wine)
2. Install Python (the code and also following instructions were tested with versions 2.7 and 3.6).
3. Install pywin32 Python package:
   
      `pip.exe install pypiwin32` (if not present "by default")
5. Install PyInstaller:
   
      `pip.exe install pyinstaller`

#### To compile the agent template, first change directories to the base_brain directory, then run pyinstaller to bundle the agent template and pisqpipe dependency as a one file exe. Note that the exe MUST begin with "pbrain-" to be recognized by the gomoku manager as a valid agent program.

      cd C:\path\to\base_brain\
      pyinstaller.exe gomoku_agent_template.py pisqpipe.py --name pbrain-peabrain.exe --onefile

Pisqpipe is a provided dependency for the Gomocup python agent template implementing the Gomocup protocol functions; the stock python agent example is available as example.py for reference.
