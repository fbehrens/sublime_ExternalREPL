# External REPL 
Sublime 3 Plugin to send lines of code to any REPL running in exteral Console.
Works on Windows with ConEmu and on OSX/Linux with tmux

## why
- simple (20 loc)
- Works on all platforms
- with all repls

## requirements
* windows: runnning [ConEmu](https://github.com/Maximus5/ConEmu)
-Terminal and `..../<ConEmu-Dir>/ConEmu` on path
* osx and linux: [tmux](http://tmux.sourceforge.net) started with `tmux new -s repl` (starts a new tmux named session)

## Keymap
* `ctrl-shift-enter`: sends current line to external REPL, cursor walks to next line 
* `ctrl-shift-s`: sends up-arrow and return to external REPL (Windows only) 

## Issues
- ConEmuC sends keys not to the active but the first editor (can have only one repl)

## ToDo
- multiline support 
- detection of blocks (ruby method definitions, clojure forms)
- support selected text

## License
MIT
