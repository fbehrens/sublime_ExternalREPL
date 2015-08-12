# What it is and how it works
This plugin is designed to optimize an interactive programmin workflow, in which you are working in the editor and a console window.
There you are editing some programm in the editor, and then run it from the console. 
Or you are developing in a TDD fashion, so you run some tests from the console. 
Or you try out some 

## Installation 
### of this plugin  
* Install [Sublime Text 3](http://www.sublimetext.com/3)
* Install [Package Control](https://packagecontrol.io/installation)
* Install this Plugin from Sublime with `CTrl-Shift-P / Package Control: Install Package / ExternalREPL`

### install console
On Windows install ConEmu
On Linux or OSX install Tmux 

* Add Sublime Directory to Path. This adds the `subl` command.

* Adjust ConEmu Settings
	* deactivate `Keys & Macro/Paste/Confirm <Enter> keypress`
![ConEmu Settings](images/ConEmuSettings.png)
Plugin send command to Konsole with  'ConEmuC -GuiMacro:0 Paste(0,"command\\n")'

### Linux
* Installation 
Install [Tmux](https://tmux.github.io/) for Mac / Linux 

### Tested Configuration
Sublime: 3 build 3083

Osx: 10.10.4 Yosemite
Linux: Ubuntu 12.04, 14.04
Tmux: 2.0

Windows: 7, 8.1
ConEmu: 150513

## Usage
Start session with `tmux new s repl`.
Start sublime from your console using the `subl` command.
`Command()-Shift P` and typing `External` shows the commands. 
Hotkeys are shown via `F1`

### repl Commands
`cs-ENTER`    Sending selected text (or current line) and <Enter> to the repl
`c-up`        Sending up arrow and Enter to the repl. This hopefully executes your last command. last repl command (doesn't work in pry on windows)  

### Editor Commands
Those Commands runs or loads the current file or executes test in the language of its syntax.
It is possible to execute only the selected test. 
There is a convention for naming of testfiles. This makes it possible to switch between implementation and tests.
The commands are run from the root of the sublime folder, so your project directory needs to be in the sublime side bar.

|  Language  | comment |      run       |     load    | test framework |      test     |            test_one           |     testfile     |
|------------|---------|----------------|-------------|----------------|---------------|-------------------------------|------------------|
| powershell | #       | <file>         | . <file>    | psspec         | psspec <file> | psspec <file> -example <name> | <file>.tests.ps1 |
| ruby       | #       | ruby <file>    | load <file> | minitest       |               |                               |                  |
| gemfile    |         | bundle install |             |                |               |                               |                  |
| fsharp     | //      |                |             |                |               |                               |                  |
| clojure    | ;       |                |             |                |               |                               |                  |
| dot        |         | dot            |             |                |               |                               |                  |
| markdown   |         | pandoc -> doc  |             |                |               |                               |                  |

`cs-.` load file  
`F5`   run file   
`cs-t` run testfile             
`cs-o` excecute selected test   
`cs-'`      switch code<->test  
`cs-s` Execute last editor Command
`sc-h` Execute from history
`cs-c` change directory/ns 

### Miscellaneous Commands
This is a grabbag for some stuff that i found useful at a time.
`cs-1` open explorer
`cs-2` dublicate file (This is quite useful)
`cs-3` open file on selected editor line (http:// in chrome or with sublime )
`f1`   show shortkeys
`cs-4` restructure mdTOC                                                                             

## Troubleshooting

### Silent Failure
#### Check if console is in your path
Open the sublime console  `c-`` 

    import os
    os.environ['PATH'] = "/usr/local/bin:" + os.environ['PATH']

Check if `tmux` or `ConEmuC` is on your path. If not consider starting sublime from the console using the `subl` command.

#### Check if you can send Keys to your console
Do this from another console and 

	# Tmux properly working
	tmux send-keys -t repl 'ls'  C-m         

	# ConEmu on Windows 
    ConEmuC -GuiMacro:0 Paste(0,"dir\\n")    

## Tmux 101
* From Tmux you can detach with `Prefix(C-b) d`.
* and reattach to your tmux session with `tmux a -t repl`
* [Making the clipboard work between iTerm2, tmux, vim and OS X.](http://evertpot.com/osx-tmux-vim-copy-paste-clipboard/)

## License    
MIT-License (see license.txt)
