# Extern REPL 
Sublime 3 Plugin to send code to active tab Console Window

## why
- Works on all platforms
- with all repls
- simple (20 loc)

## requirements
* windows: runnning [ConEmu](https://github.com/Maximus5/ConEmu)
-Terminal and `..../<ConEmu-Dir>/ConEmu` on path
* osx and linux: [tmux](http://tmux.sourceforge.net) started with `tmux new -s repl` (starts a new tmux session named )

## Keymap
`Ctrl-1`:  sends current line to current Tab, cursor walks to next line 

## Issues
- ConEmuC
        build140225 returns error code 134
        current build doesn't work

## ToDo
- multiline support 
- detection of blocks (ruby method definitions, clojure forms)
- support selected text
