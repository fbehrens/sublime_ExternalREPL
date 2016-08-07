# this restructures the target file
# no output piping is used because we don't want to render if there is an error
source, target = ARGV
md  = IO.readlines(target)
out = ""
toc = IO.readlines(source).map do |line|
  if line =~ /^(.*)\((\d+),(\d+)\)/
    heading , from, to = $1, $2.to_i, $3.to_i
    out << heading << "\n"
    out << md[from+1...to].join
  else
    out << "!!!#{line }: not matching"
  end
end
IO.write target, out
