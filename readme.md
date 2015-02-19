# Rationale
Sublime 3 Plugin to interact with a external console for interactive development workflow 
in many languages and tools. 

I prefer this workflow as it allow flexibity to work on the console, 
with some added persistence in the editor.


* osx and linux: [tmux](http://tmux.sourceforge.net). Start a new na`````mes session with `tmux new -s repl`.

## Installation 
* Install [Sublime Text 3](http://www.sublimetext.com/3)
* Install [Package Control](https://packagecontrol.io/installation)
* Install this Plugin from Sublime with `CTrl-Shift-P / Package Control: Install Package / ExternalREPL`

### windows
Add Sublime Directory to Path
Adjust ConEmu Settings: deactivate `Keys & Macro/Paste/Confirm <Enter> keypress`

![ConEmu Settings](images/ConEmuSettings.png)


### Linux
* Install [Tmux](http://www.sublimetext.com/3) for Mac / Linux 


## Usage
Start sublime from ConEmu with `subl`
Press f1 for 

| Language | load        | run | test | test_one|testfile
| ---------| ------------| ----| -----| ----| -----|
| powershell | . <file>| <file>| psspec <file> | psspec <file> -example <name>| <file>.tests.ps1 |
| ruby     | ruby <file>| load '<file>'|       |                              |                  |

## License    
MIT-License (see license.txt)
