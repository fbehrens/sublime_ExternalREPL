import sublime, sublime_plugin
from subprocess import Popen

class ExternReplUp(sublime_plugin.TextCommand):
    "sends up arrow"
    def run(self, edit):
        self.view.run_command("save")
        if sublime.platform() == 'windows':
            Popen('ConEmuC -GuiMacro:0 Keys("Up");Paste(0,"\\n")')
        else:
            command= 'tmux send-keys -t repl Up C-m'
            print("Command = " + command)
            return Popen(command,shell=True)

class ExternReplLast(sublime_plugin.TextCommand):
    "sends last command from History"
    def run(self, edit):
        self.view.run_command("save")
        init_er(self)
        self.er.command(self.er.history.entries[0])
        print("last")

class ExternReplOps(sublime_plugin.TextCommand):
    def run(self, edit, what):
        init_er(self)
        self.er.command(self.er.ops_get(what)())

class ExternReplHistory(sublime_plugin.TextCommand):
    "runs the command from the history"
    def run(self, edit):
        init_er(self)
        self.view.window().show_quick_panel(self.er.history.entries, self.select )
    def select(self, x):
        if (x != -1):
            self.er.command(self.er.history.entries[x])

class History:
    def __init__(self,project):
        self.project = project
        self.settings = sublime.load_settings("ExternalRepl.last-run")
        self.all_entries = self.settings.get("historys") or {}
        self.entries = self.all_entries.get( self.project) or []

    def append(self,text):
        self.entries.insert(0,text) # prepend
        self.remove_dublicates()
        self.all_entries[self.project] = self.entries
        self.settings.set("historys", self.all_entries)
        sublime.save_settings("ExternalRepl.last-run")

    def remove_dublicates(self):
        "while retaining order"
        seen = set()
        seen_add = seen.add
        self.entries = [ x for x in self.entries if x not in seen and not seen_add(x)]

class Er:
    def __init__(self,stc):
        self.stc  = stc
        view      = stc.view
        file_name = view.file_name()
        self.path = [f for f in sublime.active_window().folders() if file_name.startswith(f)][0] # project directory
        self.file = file_name[len(self.path)+1:]
        self.history = History(self.path)
        scopes = view.scope_name(view.sel()[0].begin()) # source.python meta.structure.list.python punctuation.definition.list.begin.python
        langs = ["python","powershell","ruby","clojure"]
        match = [l for l in langs if l in scopes]

        self.lang = "unknown"
        if match:    self.lang = match[0]

        self.ops = {
            "cd":       lambda: "cd " + self.path,
            "explorer": lambda: "explorer " + self.path,
            "line":     lambda: self.line()
        }
        self.ops_lang = {
            "powershell": {
                "load":              lambda: '. .\\' + self.file,
                "test":              lambda: 'invoke-pester ' + self.file,
                "test_one_pattern":  """^\s*describe\s+(?:'|")(.*)(?:'|")\s*\{\s*$""",
                "test_one":          lambda: 'invoke-pester ' + self.file + ' -testname ' + ' '.join(self.selected_testnames())
            },
            "clojure": {
                "load":              lambda: '(load-file "' + path.replace("\\","/") + '")'
            },
            "ruby": {
                "test_one_pattern": """^\s*it\s+(?:'|")(.*)(?:'|")\s+do\s*$"""
            },
            "python": {
            },
        }

    def line(self):
        view = self.stc.view
        for region in view.sel():
            if region.empty():
                line = view.line(region)
                line_contents = view.substr(line)
                line_below = sublime.Region(line.b+1)
                view.sel().clear()
                view.sel().add(line_below)
                return line_contents
            else:
                return view.substr(region)

    def ops_get(self,operation):
        return self.ops.get(operation) or self.ops_lang.get(self.lang).get(operation)

    def testnames(self):
        "( (region, 'name'),... )"
        testnames = []
        regions = self.stc.view.find_all(self.ops_get("test_one_pattern"),fmt="$1",extractions=testnames)
        regions[0].a  = 0
        regions[-1].b = self.stc.view.size()
        for i,region in enumerate(regions[:-1]):
            region.b = regions[i+1].a
        return [ (region, testnames.pop(0)) for region in regions]

    def selected_testnames(self):
        "list of testnames"
        acc = []
        for region, testname in self.testnames():
            for s in self.stc.view.sel():
                if s.intersects(region):
                    acc.append( testname )
        return acc

    def command(self,command):
        self.history.append(command)
        # \ => \\ | " => \" | remove \n
        quoted = command.replace('\\','\\\\')\
                     .replace('"','\\"')
        if sublime.platform() == 'windows':
            command = 'ConEmuC -GuiMacro:0 Paste(0,"' + quoted + '\\n")'
            print("Command= " + command)
            return Popen(command)
        else:
            # Multiline with tmux needs multiple commands
            for line in quoted.split('\n'):
                command = 'tmux send-keys -t repl "' + line + '" C-m'
                Popen(command,shell=True)

def init_er(self):
    self.er = Er(self)
