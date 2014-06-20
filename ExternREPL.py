import sublime, sublime_plugin
from subprocess import Popen
"""
echo "hi"
echo 'ho'
1 + 1
echo \\
"""

def append_to_history(text,path):
    def remove_dublicates(seq):
        "while retaining order"
        seen = set()
        seen_add = seen.add
        return [ x for x in seq if x not in seen and not seen_add(x)]
    s = sublime.load_settings("ExternalRepl.last-run")
    historys = s.get("historys") or {}
    history  = historys.get(path) or []
    history.insert(0,text) # prepend
    historys[path] = remove_dublicates(history)[:9]
    s.set("historys", historys)
    sublime.save_settings("ExternalRepl.last-run")

def repl_command(text,path):
    append_to_history(text,path)
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
                repl_command( line_contents,"Do" )
            else:
                repl_command( self.view.substr(region),"Do")

class ExternReplRepeat(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.run_command("save")
        if sublime.platform() == 'windows':
            Popen('ConEmuC -GuiMacro:0 Keys("Up");Paste(0,"\\n")')
        else:
            command= 'tmux send-keys -t repl Up C-m'
            print("Command = " + command)
            return Popen(command,shell=True)

class ExternReplLoad(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.run_command("save")
        set_path_file(self)
        repl_command(clj_load(self.file),self.path)

class ExternReplTest(sublime_plugin.TextCommand):
    "Runs the Current File"
    def run(self, edit):
        self.view.run_command("save")
        set_path_file(self)
        repl_command(powershell_test(self.file),self.path)

class ExternReplTestOne(sublime_plugin.TextCommand):
    "runs the selected tests"
    def run(self, edit):
        self.view.run_command("save")
        set_path_file(self)
        repl_command(powershell_test_one(self.file,selected_testnames(self)),self.path)

class ExternReplHistory(sublime_plugin.TextCommand):
    "runs the command from the history"
    def run(self, edit):
        set_path_file(self)
        self.history = sublime.load_settings("ExternalRepl.last-run").get("historys")[self.path]
        self.view.window().show_quick_panel(self.history, self.select )
        print("path", self.file)
    def select(self, x):
        repl_command(self.history[x],self.path)

def set_path_file(self):
    file_name = self.view.file_name()
    self.path = [f for f in sublime.active_window().folders() if file_name.startswith(f)][0] # project directory
    self.file = file_name[len(self.path)+1:]

def clj_load(path):
    return '(load-file "' + path.replace("\\","/") + '")'

def powershell_test(path):
    return 'invoke-pester ' + path

def powershell_test_one(path,testnames):
    return 'invoke-pester ' + path + ' -testname ' + ' '.join(testnames)

def selected_testnames(self):
    "list of testnames"
    acc = []
    for region, test_name in region_testnames(self):
        for s in self.view.sel():
            if s.intersects(region):
                acc.append( test_name )
    return acc

def region_testnames(self):
    """does the pattern matching for "describe "" do"
    return [ (region, 'test_name' ), ..  ]"""
    patterns = {
      "powershell": """^\s*describe\s+(?:'|")(.*)(?:'|")\s*\{\s*$""",
      "ruby": """^\s*it\s+(?:'|")(.*)(?:'|")\s+do\s*$"""
    }

    test_names = []
    regions = self.view.find_all(patterns["powershell"],fmt="$1",extractions=test_names)
    regions[0].a  = 0
    regions[-1].b = self.view.size()
    for i,region in enumerate(regions[:-1]):
        region.b = regions[i+1].a
    return [ (region, test_names.pop(0)) for region in regions]

class ExternReplTest1(sublime_plugin.TextCommand):
    # view.run_command("extern_repl_test")
    def test(self, message, truthy):
        if(not truthy):
            print(message)

    def run(self, edit):
        self.test("folder_path", folder_path( ["a","b","c"], "b\\hh") \
                                 == ["b","hh"])
        print(1)