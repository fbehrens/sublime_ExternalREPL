import sublime, sublime_plugin, re, shutil, functools, os
from subprocess import Popen, call

class GitGui(sublime_plugin.TextCommand):
  def run(self, edit,directory=None):
    if directory == None:
      directory = os.path.dirname( self.view.file_name())
    if os.name == "posix":
      self.view.window().run_command("exec",{
        "cmd": [ "git", "gui" ],
        "working_dir": directory
      })
    else:
      os.chdir( directory )
      Popen("git gui")
      # git_install_root = "C:\\Program Files (x86)\\Git\\"
      # Popen(["%sbin\\wish.exe" % (git_install_root),"%slibexec\\git-core\\git-gui" % (git_install_root)])


# replaces _ with \w+ and reduces whitespace to one single
def prep_data(a):
    f = a[0].replace("_","\w+") # _ => \w+
    f = re.sub(r'\s+', " ", f)  # '    ' => ' '
    return (f,a[1])
# assert prep_data(("a  _",41)) ==  ("a \w+",41)

def extract_http(s):
    m = re.search('\[.*\]\((.*)\)',s)
    if m:
        return m.group(1)
    m = re.search("https?://\S*",s)
    if m:
        return(m.group(0))
# assert extract_http('a http://foo b') == 'http://foo'
# assert extract_http('[Die Foo Seite](htt://foo)') == 'htt://foo'

def extract_file(s):
    "finds first word with / or \\"
    m = re.search('\S*[\\\\/]\S*',s)
    if m:
        return m.group(0)
# assert extract_file("a f/d b") == "f/d"

class ExternReplSelfTest(sublime_plugin.TextCommand):
    def run(self, edit):
        init_er(self)
        print("SelfTest")

class ExternReplUp(sublime_plugin.TextCommand):
    "sends up arrow"
    def run(self, edit):
        self.view.run_command("save")
        if sublime.platform() == 'windows':
            Popen('ConEmuC -GuiMacro:0 Keys("Up");paste(2,"\\n")')
        else:
            command= 'tmux send-keys -t repl Up C-m'
            print("Command = " + command)
            return Popen(command,shell=True)

class ExternReplOps(sublime_plugin.TextCommand):
    def run(self, edit, what):
        if self.view.is_dirty():
            self.view.run_command("save")
        init_er(self)
        command = self.er.ops_get(what)()
        self.er.command(command)

class ExternReplHistory(sublime_plugin.TextCommand):
    "runs the command from the history"
    def run(self, edit):
        init_er(self)
        self.view.window().show_quick_panel(self.er.history.entries, self.select )
    def select(self, x):
        if (x != -1):
            self.er.command(self.er.history.entries[x])

class ExternReplCustomcommand(sublime_plugin.TextCommand):
    "runs the command from the history"
    def run(self, edit):
        init_er(self)
        self.items = sublime.load_settings("ExternalRepl.custom_commands").get(sublime.platform())
        self.view.window().show_quick_panel([i[0] for i in self.items],self.select)

    def select(self, x):
        if (x != -1):
            self.er.command(self.items[x][1])

class ExternReplFile(sublime_plugin.TextCommand):
    "opens the file or webpage in current line"
    def run(self, edit):
        init_er(self)
        lc = self.er.line_content
        url = extract_http(lc)
        if url:
            c = self.er.ops_get("chrome")(url=url)
        else:
            file = extract_file(lc)
            if file:
                c = "subl " + file
        if c:
            print(c)
            self.er.command(c)
        else:
            print("can't detect url or file in " + lc )

class ExternReplRefresh(sublime_plugin.TextCommand):
    "invoked be F5, new version of run"
    def run(self, edit):
        if self.view.is_dirty():
            self.view.run_command("save")
        init_er(self)
        self.manual_refresh() or self.test() or self.runn()

    def manual_refresh(self):
        # dictionary of {file: command ,... }
        manual = {
          os.environ["scripts2"] + "\\libwba\\functions.md":"ruby \\Dropbox\\sublime\\data\\packages\\ExternalREPL\\ruby\\psdoc.rb > %scripts2%\\libwba\\functions.md"
        }
        if (self.er.file_name in manual):
            command = manual[self.er.file_name]
            return_code = call(command, shell=True)
            print ("manual refresh with: " + command + "(" + str(return_code) + ")")
            return True

    def test(self):
        if (self.er.ops_get('istest')()):
            print("run tests")
            self.er.command(self.er.ops_get('test')())
            return True

    def runn(self):
        print("runn")
        self.er.command(self.er.ops_get('run')())

class ExternReplAlternate(sublime_plugin.TextCommand):
    "switches from file to test and reverse"
    def run(self, edit):
        init_er(self)
        other = self.er.alternate(self.view.file_name())
        print("switch to: "+ other)
        self.view.window().open_file(other)

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

class ExternReplMarkdownToc(sublime_plugin.TextCommand):
    "copies current file and opens it"
    def run(self, edit):
        if self.view.is_dirty():
            self.view.run_command("save")
        file = self.view.file_name()
        if re.compile( r'\.md$',re.I).search(file):
            #c:\project\file.tests.ps1
            toc = re.sub(r'\.md$',".md.toc",file)
            command = "ruby "+sublime.packages_path()+"\\ExternalREPL\\ruby\\toc.rb "+file+" > "+toc
            return_code = call(command, shell=True)
            self.view.window().open_file(toc)
        elif re.compile( r'\.md.toc$',re.I).search(file):
            md = re.sub(r'\.md\.toc$',".md",file)
            command = "ruby "+sublime.packages_path()+"\\ExternalREPL\\ruby\\retoc.rb "+file+" "+md #+" > "+md
            return_code = call(command, shell=True)
            self.view.window().open_file(md)

class ExternReplShowOutput(sublime_plugin.WindowCommand):
    "pipes textbuffer into command"
    def run(self):
        text="""
repl                           run             test                          misc
cs-EN selected                 cs-. load file  cs-t run testfile             cs-c change directory/ns
c-up  <up> last repl command   f5   run file   cs-o excecute selected test   cs-1 open explorer
cs-s  last editor command                      cs-'      switch code<->test  cs-2 dublicate file
cs-h  execute from history                                                   f2   rename
                                                                             cs-3 open file or http:// on line
                                                                             f1   show shortkeys
                                                                             cs-4 restructure mdTOC
        """
        self.output_view = self.window.create_output_panel("exec")
        self.output_view.run_command('append', {'characters': text, 'force': True, 'scroll_to_end': True})
        self.window.run_command("show_panel", {"panel": "output.exec"})

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


        if self.file == "Gemfile":
            self.lang = "gemfile"
        else:
            scopes = self.view.scope_name(self.view.sel()[0].begin()) # source.python meta.structure.list.python punctuation.definition.list.begin.python
            # print(scopes)
            langs = ["fsharp","python","powershell","ruby","clojure","markdown","dot"]
            match = [l for l in langs if l in scopes]

            self.lang = "unknown"
            if match:
                self.lang = match[0]
            else:
                print("Cant find lang for scopes")

        methods = [
            ("run    python _",     lambda: 'python ' + self.file),
            ("load   python _",     lambda: 'exec(open("'+self.file+'").read())'),

            ("istest  powershell _",  lambda: re.match(".*\.tests\.ps1$",self.file_name)),
            ("load   powershell _",  lambda: '. ' + self.file_name),
            ("run    powershell _",  lambda: self.file_name),
            ("test   powershell _",  lambda: 'psspec ' + self.file),
            ("test1p powershell _",  """^\s*(?:it|It|describe|Describe)\s+(?:'|")(.*)(?:'|").*\{\s*$"""),
            ("test1  powershell _",  lambda: 'psspec ' + self.file + ' -example "' + '|'.join([i for i in self.selected_testnames]) + '"'),

            ("load clojure _",   lambda: '(load-file "' + self.file.replace("\\","/") + '")'),

            ("test   ruby _",   lambda: 'ruby  -I test'+os.pathsep+'lib ' + self.file.replace("\\","/") ),
            ("load   ruby _",   lambda: 'load "' + self.file_name.replace("\\","/") + '"'),
            ("run    gemfile _",   lambda: 'bundle install'),
            ("run    ruby _",   lambda: 'ruby -I lib ' + self.file),
            ("test1  ruby _",   lambda: 'ruby -I lib' + os.pathsep +'test ' + self.file + ' --name "/' + '|'.join([ '^test_\d{4}_'+i+'$' for i in self.selected_testnames]) +'/"'),
                                # ruby -I lib;test test\couch_test.rb --name /^test_\d{4}_describe1$|^test_\d{4}_describe2$/"
            ("test1p ruby _",   """^\s*it\s+(?:'|")(.*)(?:'|")\s+do\s*$"""),
            ("load markdown _", lambda: "pandoc -r markdown_github+footnotes+grid_tables -o \"" + re.sub("\..+$",".docx",self.file) + "\" \"" + self.file +"\""),
            ("run  markdown _",  lambda: self.ops_lang.get("markdown").get("load")() + " && \"" + re.sub("\..+$",".docx",self.file) + "\""),

            ("load   fsharp _", lambda: "#load \"" + self.file_name + "\";;"),

            ("run dot _", lambda: 'dot -Tpng -O ' + self.file),

            ("explorer _ windows", lambda: "explorer " + self.path),
            ("explorer _ osx"    , lambda: "open "     + self.path),

            ("cd clojure _",   lambda: self.cd_clojure),
            ("cd _       _",   lambda: 'cd "' + self.path + '"'),

            ("line clojure _",   lambda: self.line_clojure),
            ("line fsharp  _",   lambda: self.line() + ";;"),
            ("line _       _",  self.line),

            ("lineuncomment fsharp _", lambda s: re.sub(r"^\s*//\s*","",s)), # strip leading //
            ("lineuncomment _ _"    , lambda s: re.sub(r'^# ', r'', s,0,re.MULTILINE)), # strip leading #

            ("last  _ _",    lambda: self.history.entries[0]),
            ("istest _ _",   lambda: False),
            ("chrome _ _",   lambda **a: "chrome " + a['url'] ),
        ]
        self.methods  = list(map( prep_data,methods ))

    def ops_get(self,method):
        string = method + " " + self.lang +  " " + sublime.platform()
        print("opsget: "+string)
        f =  next(pl[1] for pl in self.methods if re.match( pl[0], string))
        return f

    @property
    def line_content(self):
        region = self.view.sel()[0]
        line = self.view.line(region)
        return self.view.substr(line)

    def line(self):
        for region in self.view.sel():
            if region.empty():
                # select current line
                line = self.view.line(region)
                line_contents = self.view.substr(line)
                line_below = sublime.Region(line.b+1)
                self.view.sel().clear()
                self.view.sel().add(line_below)
                return self.ops_get("lineuncomment")(line_contents)
            else:
                return self.ops_get("lineuncomment")(self.view.substr(region))
                return self.view.substr(region)

    @property
    def line_clojure(self):
        opening = []
        regions = self.view.find_all("^\(",fmt="$1",extractions=opening)
        for i,region in enumerate(regions[:-1]):
            region.b = regions[i+1].a-1
        regions[-1].b = self.view.size()
        forms = []
        for region in regions:
            for s in self.view.sel():
                if s.intersects(region):
                    forms.append( self.view.substr(region) )
        return "".join(forms)

    @property
    def cd_clojure(self):
        ns = self.view.find(r"\(\s*ns [\w\.]+", 0)
        return self.view.substr(ns) + ")"

    @property
    def testnames(self):
        "( (region, 'name'),... )"
        testnames = []
        regions = self.view.find_all(self.ops_get("test1p"),fmt="$1",extractions=testnames)
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
        print("command:"+command)
        self.history.append(command)
        # \ => \\ | " => \" | remove \n
        quoted = command.replace('\\','\\\\')\
                        .replace('"','\\"')
        if sublime.platform() == 'windows':
            command = 'ConEmuC -GuiMacro:0 paste(2,"' + quoted + '\\n")'
            Popen(command)
        else:
            # Multiline with tmux needs multiple commands
            for line in quoted.split('\n'):
                line = re.sub(r";$","\\;",line)   # quote ; at end of line
                line = re.sub(r"\$","\\\$", line) # quote $
                command = 'tmux send-keys -l -t repl "' + line + '"'
                print(command)
                Popen(command,shell=True)
                Popen('tmux send-keys -t repl C-m',shell=True)

    # test switching
    def alternate(self,file):
        return getattr(self, "alternate_"+ self.lang)(file)

    # converters for alternate file witching named altenate_syntax
    def alternate_powershell(self,file):
        if re.compile( r'\.tests\.',re.I).search(file):
            # c:\project\file.tests.ps1
            return re.sub(r'\.tests\.',".",file)
        else:
            # c:\project\file.ps1
            return re.sub(r'\.ps1$',".tests.ps1",file)

    def alternate_ruby(self,file):
        if re.compile( r'\\test_',re.I).search(file):
            # c:\project\test\bar\test_foo.ps1
            a = re.sub(r'\\test\\',"\\\\lib\\\\",file)
            return re.sub(r'\\test_',"\\\\",a)
        else:
            # c:\project\lib\bar\foo.ps1
            a = re.sub(r'\\lib\\',"\\\\test\\\\",file)
            return re.sub(r'\\([^\\]+)$',"\\\\test_\g<1>", a)

# returns false if there is an error happening
def init_er(self):
    self.er = Er(self)
    if self.er.error:
        print(self.er.error)
        return False
    else:
        return True

