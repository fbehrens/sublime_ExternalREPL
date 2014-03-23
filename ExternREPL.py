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
        s = sublime.load_settings("ExternalRepl.last-run")
        s.set("last-text", text)
        quoted = text.replace('\\','\\\\').replace('"','\\"')
        if sublime.platform() == 'windows':
            command = 'ConEmuC -GuiMacro:0 Paste(0,"' + quoted + '\\n")'
            print("Command= " + command)
            return Popen(command)
        else:
            # Multiline with tmux needs multiple commands
            command = 'tmux send-keys -t repl "' + quoted + '" C-m'
            print("Command= " + command)
            return Popen(command,shell=True)

    def run(self, edit):
        for region in self.view.sel():
            if region.empty():
                line = self.view.line(region)
                line_contents = self.view.substr(line)
                # print( repr( quoted ))
                line_below = sublime.Region(line.b+1)
                self.view.sel().clear()
                self.view.sel().add(line_below)
                self.repl_command( line_contents )
            else:
                self.repl_command( self.view.substr(region) )

class ExternReplRepeat(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.run_command("save")
        Popen('ConEmuC -GuiMacro:0 Keys("Up");Paste(0,"\\n")')

class ExternReplLast(sublime_plugin.TextCommand):
    def run(self, edit):
        s = sublime.load_settings("ExternalRepl.last-run")
        ExternReplDo.repl_command(self, s.get("last-text"))
