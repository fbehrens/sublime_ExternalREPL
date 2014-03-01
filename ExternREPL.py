import sublime, sublime_plugin
import  subprocess
"""
ls
"""
class ExternReplDo(sublime_plugin.TextCommand):
  def run(self, edit):
    s = sublime.load_settings("ExternREPL.sublime-settings")
    for region in self.view.sel():
        if region.empty():
            line = self.view.line(region)
            line_contents = self.view.substr(line)
            line_below = sublime.Region(line.b+1)
            self.view.sel().clear()
            self.view.sel().add(line_below)
            command = s.get("con_emu_c") + ' -GuiMacro:0 Paste(0,"' + line_contents + '\\n")'
            return_code = subprocess.call(command)
            print(return_code)
        # else:
        #     print("Not Implemente yet: " + self.view.substr(region))
