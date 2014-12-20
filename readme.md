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
* `ctrl-shift-l(deactivated)`: sends last command to external REPL (Windows only)
* `ctrl-shift-s`: sends up-arrow and return to external REPL
* `ctrl-shift-l`: reloads a clojure file in external REPL (load_file "test/wppe_test.clj")

## ToDo    
- detection of blocks (ruby method definitions, clojure forms)

## Release    
`git tag`
`git tag 0.0.5`
`git push origin 0.0.5`

## License    
MIT

ls -l
