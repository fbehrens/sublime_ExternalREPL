import sublime, sublime_plugin, re, shutil, functools, os
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

class ExternReplOps(sublime_plugin.TextCommand):
    def run(self, edit, what):
        if self.view.is_dirty():
            self.view.run_command("save")
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

class ExternReplFile(sublime_plugin.TextCommand):
    "opens the file under cursor"
    def run(self, edit):
        init_er(self)
        file = self.er.line
        print("opening "+file)
        self.view.window().open_file(file)

class ExternReplSwitch(sublime_plugin.TextCommand):
    "switches from file to test and reverse"
    def run(self, edit):
        init_er(self)
        other = getattr(self, "powershell")(self.view.file_name()) # send
        print("switch to: "+ other)
        self.view.window().open_file(other)

    def powershell(self,file):
        print("file=",file)
        if re.compile( r'\.tests\.',re.I).search(file):
            #c:\project\file.tests.ps1
            return re.sub(r'\.tests\.',".",file)
        else:
            # c:\project\file.ps1
            return re.sub(r'\.ps1$',".tests.ps1",file)

class ExternReplDublicateFile(sublime_plugin.TextCommand):
    "copies current file and opens it"
    def run(self, edit):
        if self.view.is_dirty():
            self.view.run_command("save")
        file = self.view.file_name()
        v = self.view.window().show_input_panel("Copy File to:", file, functools.partial(self.on_done,file), None, None)
        name, ext = os.path.splitext(file)
        v.sel().clear()
        v.sel().add(sublime.Region(0, len(name)))

    def on_done(self,src, dst):
        shutil.copyfile(src, dst)
        self.view.window().open_file(dst)

class ExternReplMoveFile(sublime_plugin.TextCommand):
    "renames current file and opens it"
    def run(self, edit):
        if self.view.is_dirty():
            self.view.run_command("save")
        file = self.view.file_name()
        v = self.view.window().show_input_panel("Copy File to:", file, functools.partial(self.on_done,file), None, None)
        name, ext = os.path.splitext(file)
        v.sel().clear()
        v.sel().add(sublime.Region(0, len(name)))

    def on_done(self,src, dst):
        try:
            os.rename(src, dst)
            self.view.retarget(dst)
        except:
            sublime.status_message("Unable to rename")

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
        self.error = None # can be set
        self.stc  = stc
        self.view = stc.view
        self.file_name = self.view.file_name()
        folders = [f for f in sublime.active_window().folders() if self.file_name.lower().startswith(f.lower())] # project directory
        if not folders:
         #   self.error ="Project Folder needs to be incuded in Side Bar (can't find project folder)"
            self.path = ""
            self.file = self.file_name
        else:
            self.path = folders[0]
            self.file = self.file_name[len(self.path)+1:]
        self.history = History(self.path)
        scopes = self.view.scope_name(self.view.sel()[0].begin()) # source.python meta.structure.list.python punctuation.definition.list.begin.python
        langs = ["python","powershell","ruby","clojure"]
        match = [l for l in langs if l in scopes]

        self.lang = "unknown"
        if match:    self.lang = match[0]

        self.ops_lang = {
            "powershell": {
                "load":              lambda: '. .\\' + self.file,
                "run":               lambda: self.file_name,
                "test":              lambda: 'invoke-pester ' + self.file,
                "test_one_pattern":  """^\s*(?:d|D)escribe\s+(?:'|")(.*)(?:'|")\s*\{\s*$""",
                "test_one":          lambda: 'invoke-pester ' + self.file + ' -testname ' + ' '.join(['"'+i+'"' for i in self.selected_testnames])
            },
            "clojure": {
                "load":              lambda: '(load-file "' + self.file.replace("\\","/") + '")'
            },
            "ruby": {
                "test_one_pattern": """^\s*it\s+(?:'|")(.*)(?:'|")\s+do\s*$""",
                "test":              lambda: 'ruby  -I test'+os.pathsep+'lib ' + self.file.replace("\\","/") ,
                "load":              lambda: 'load "' + self.file_name.replace("\\","/") + '"',
                "run":               lambda: 'ruby -I lib ' + self.file
            },
            "python": {
                "run":               lambda: 'python ' + self.file
            },
        }
        self.ops_platform = {
            "windows": {
                "cd":       lambda: 'cd "' + self.path + '"',
                "explorer": lambda: "explorer " + self.path,
            }
        }
        self.ops = {
                "line":     lambda: self.line,
                "last":     lambda: self.history.entries[0]
        }

    def ops_get(self,operation):
        return self.ops_lang.get(self.lang,{}).get(operation) \
            or self.ops_platform.get(sublime.platform(),{}).get(operation) \
            or self.ops.get(operation) \
            or (lambda: "Cannot find operation '"+operation+"' for lang="+self.lang + ", Platform="+sublime.platform())

    @property
    def line(self):
        for region in self.view.sel():
            if region.empty():
                line = self.view.line(region)
                line_contents = self.view.substr(line)
                line_below = sublime.Region(line.b+1)
                self.view.sel().clear()
                self.view.sel().add(line_below)
                return line_contents
            else:
                return self.view.substr(region)

    @property
    def testnames(self):
        "( (region, 'name'),... )"
        testnames = []
        regions = self.view.find_all(self.ops_get("test_one_pattern"),fmt="$1",extractions=testnames)
        regions[0].a  = 0
        regions[-1].b = self.view.size()
        for i,region in enumerate(regions[:-1]):
            region.b = regions[i+1].a
        return [ (region, testnames.pop(0)) for region in regions]

    @property
    def selected_testnames(self):
        "list of testnames"
        acc = []
        for region, testname in self.testnames:
            for s in self.view.sel():
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
            Popen(command)
        else:
            # Multiline with tmux needs multiple commands
            for line in quoted.split('\n'):
                command = 'tmux send-keys -t repl "' + line + '" C-m'
                Popen(command,shell=True)

# returns false if there is an error happening
def init_er(self):
    self.er = Er(self)
    if self.er.error:
        print(self.er.error)
        return False
    else:
        return True

