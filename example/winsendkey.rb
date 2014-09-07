require 'win32api'
def user32 name, types, return_value
  Win32API.new 'user32',name, types, return_value
end

find_window = user32 'FindWindow',['P','P'],'L'

handle = find_window.call nil, 'PuTTY'
puts handle

