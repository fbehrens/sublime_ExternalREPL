import sublime, sublime_plugin
from subprocess import Popen
"""
for testing
echo "hi"
echo 'ho'
1 + 1
"""
class ExternReplDo(sublime_plugin.TextCommand):
    def repl_command(self, text):
        if sublime.platform() == 'windows':
            command = 'ConEmuC -GuiMacro:0 Paste(0,"' + text + '\\n")'
            return Popen(command)
        else:
            # Multiline with tmux needs multiple commands
            command = 'tmux send-keys -t repl "' + text + '" C-m'
            return Popen(command,shell=True)

    def run(self, edit):
        for region in self.view.sel():
            if region.empty():
                line = self.view.line(region)
                line_contents = self.view.substr(line).replace('"','\\"')
                line_below = sublime.Region(line.b+1)
                self.view.sel().clear()
                self.view.sel().add(line_below)
                return_value = self.repl_command( line_contents )
                print(return_value)
            # else:
        #     print("Not Implemente yet: " + self.view.substr(region))
