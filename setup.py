from cx_Freeze import setup, Executable

build_exe_options = {"includes": ["OpenGL"]}
setup(
    name='happy_ville',
    version=1.0,
    description='metroidvania yeehaw',
    options = {"build_exe": {"packages": ["OpenGL", "moderngl", "glcontext"]}},
    executables=[Executable('game.py',base='Win32GUI')],
)
