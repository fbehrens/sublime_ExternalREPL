# print documentation of powershell modules
require 'map'
require 'awesome_print'

Dir.chdir "#{ENV['scripts2']}/libwba/modules"

$f = []

def delta_brackets line
  line.scan(/{/).count - line.scan(/}/).count
end

def analyse mo,fi
  current = 'main'
  functions = Map(current ,
                  Map(:name, current,
                      :body,[] ,
                      :module, mo,
                      :file, fi ))
  open_brackets = 0
  File.new("#{mo}/#{fi}.ps1").each  do |line|
    if line =~ /^(function|filter)\s+([\w-]+)/
      type, current, open_brackets = $1, $2, 0
      functions.set(current,Map(:name, current,:body,[] , :module, mo, :file, fi ))
    end
    functions.get(current,:body) << line
    open_brackets += delta_brackets(line)
    head = false if open_brackets > 0
    current = 'main' if open_brackets == 0 && line['}']
  end
  functions.values.each {|f| $f << f}
end

# inplace uupdate of function node
def analyse_function f
  # puts f[:file],f[:name]
  return if f.name == 'main'
  f.doc = []
  while f.body[1] =~ /^\s*#(.*)$/
     f.doc << f.body.delete_at(1)
  end
  # all until the return after to opening bracket
  header = f.body.join("\n")[/^[^{]*[^\n]*/m]
  # all after the first opening bracket
  if param = header[/(?<=\().*/m]
    f.param = param.gsub(/^\n/,'').gsub(/\)|\{|,/,'')
  end
  f.doc = f.doc.map{|l| l[/[^#]*$/].chomp.strip}.join(" ")
end

Dir['*/*.ps1'].
    reject {|s| s=~ /test/}.
    reject {|s| s=~ /^Pester/}.each do |file|
  file =~ %r{([\w]+)/([\w]+)}
  mo, fi = $1, $2
  analyse mo, fi
end
$f.each {|f|  analyse_function f }

def out
  g = Map()
  name_max = $f.map(&:name).map(&:length).max + 2
  $f.reject{|f|f.name == 'main'}.each do |f|
    g.set f.delete(:module),f.delete(:file),f.delete(:name),f
  end
  g.each do |m,r|
    puts "##{m}"
    r.each do |f,r|
      puts "###{f}"
        r.each do |name,r|
          # puts name
          # ap r
          puts "%-#{name_max}s %s" % [name , r.get(:doc)]
          puts r[:param ]
        end
    end
  end
end
out
exit


names = bodies.keys
names.delete 'main'
filter = /#{names.join "|"}/i

bodies.each do |name,body|
  bodies[name] = body.scan(filter).uniq
  bodies[name].delete name
end

puts "digraph G {"
  bodies.each do |name,calls|
    if calls.empty?
      puts %{"#{name}";}
    else
      calls.each do |call|
        puts %{"#{name}" -> "#{call}";}
      end
    end
  end
puts "}"
