lines_from = []

lines = IO.readlines(ARGV.first).map(&:chomp)
lines.each_with_index do |line,nr|
  lines_from << [line,nr] if  line =~ /^#/
end

max = lines.count
lines_from.reverse.each do |line_from|
  line_from << max
  max = line_from[1]
end
# to is exclusive Array item
lines_from.each do |line_from|
  puts "%s (%s,%s)" % line_from
end