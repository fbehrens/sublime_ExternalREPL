import sublime, sublime_plugin
from subprocess import Popen
"""
echo "hi"
echo 'ho'
1 + 1
echo \\
"""
def repl_command(text):
    s = sublime.load_settings("ExternalRepl.last-run")
    s.set("last-text", text)
    # \ => \\ | " => \" | remove \n
    quoted = text.replace('\\','\\\\')\
                 .replace('"','\\"')\
                 .replace('\n','')
    if sublime.platform() == 'windows':
        command = 'ConEmuC -GuiMacro:0 Paste(0,"' + quoted + '\\n")'
        print("Command= " + command)
        return Popen(command)
    else:
        # Multiline with tmux needs multiple commands
        command = 'tmux send-keys -t repl "' + quoted + '" C-m'
        print("Command= " + command)
        return Popen(command,shell=True)

class ExternReplDo(sublime_plugin.TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            if region.empty():
                line = self.view.line(region)
                line_contents = self.view.substr(line)
                # print( repr( quoted ))
                line_below = sublime.Region(line.b+1)
                self.view.sel().clear()
                self.view.sel().add(line_below)
                repl_command( line_contents )
            else:
                repl_command( self.view.substr(region) )

class ExternReplRepeat(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.run_command("save")
        if sublime.platform() == 'windows':
            Popen('ConEmuC -GuiMacro:0 Keys("Up");Paste(0,"\\n")')
        else:
            command= 'tmux send-keys -t repl Up C-m'
            print("Command = " + command)
            return Popen(command,shell=True)

class ExternReplLast(sublime_plugin.TextCommand):
    def run(self, edit):
        s = sublime.load_settings("ExternalRepl.last-run")
        repl_command(s.get("last-text"))

class ExternReplLoad(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.run_command("save")
        _, path = folder_path( sublime.active_window().folders(), \
                               self.view.file_name())
        repl_command(clj_load(path))

def folder_path(folders,path):
    "split path according to current folders"
    folder = [f for f in folders if path.startswith(f)][0]
    return [folder, path[len(folder)+1:] ]

def clj_load(path):
    return '(load-file "' + path.replace("\\","/") + '")'

class ExternReplTest(sublime_plugin.TextCommand):
    # view.run_command("extern_repl_test")
    def test(self, message, truthy):
        if(not truthy):
            print(message)

    def run(self, edit):
        self.test("folder_path", folder_path( ["a","b","c"], "b\\hh") \
                                 == ["b","hh"])
        print("ok")