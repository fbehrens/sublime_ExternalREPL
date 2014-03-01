import sublime, sublime_plugin
from subprocess import Popen
"""
echo "hi"
"""
class ExternReplDo(sublime_plugin.TextCommand):
  def run(self, edit):
    s = sublime.load_settings("ExternREPL.sublime-settings")
    for region in self.view.sel():
        if region.empty():
            line = self.view.line(region)
            line_contents = self.view.substr(line).replace('"','\\"') + '\\n'
            line_below = sublime.Region(line.b+1)
            self.view.sel().clear()
            self.view.sel().add(line_below)
            command = s.get("con_emu_c") + ' -GuiMacro:0 Paste(0,"' + line_contents + '")'
            return_code = Popen(command)
            print(return_code)
        # else:
        #     print("Not Implemente yet: " + self.view.substr(region))
