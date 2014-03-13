import sublime, sublime_plugin
from subprocess import Popen
"""
for testing
echo "hi"
echo 'ho'
1 + 1
echo \\
"""
class ExternReplDo(sublime_plugin.TextCommand):
    def repl_command(self, text):
        if sublime.platform() == 'windows':
            command = 'ConEmuC -GuiMacro:0 Paste(0,"' + text + '\\n")'
            print("Command= " + command)
            return Popen(command)
        else:
            # Multiline with tmux needs multiple commands
            command = 'tmux send-keys -t repl "' + text + '" C-m'
            print("Command= " + command)
            return Popen(command,shell=True)

    def run(self, edit):
        for region in self.view.sel():
            if region.empty():
                line = self.view.line(region)
                line_contents = self.view.substr(line)
                quoted = line_contents.replace('\\','\\\\').replace('"','\\"')
                # print( repr( quoted ))
                line_below = sublime.Region(line.b+1)
                self.view.sel().clear()
                self.view.sel().add(line_below)
                self.repl_command( quoted )
            # else:
        #     print("Not Implemente yet: " + self.view.substr(region))

class ExternReplRepeat(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.run_command("save")
        Popen('ConEmuC -GuiMacro:0 Keys("Up");Paste(0,"\\n")')
