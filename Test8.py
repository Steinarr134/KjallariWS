def fall(name):
    exec "global " + name
    exec name + " = 10"

A = None
fall("A")
exec "B = 10"

print A