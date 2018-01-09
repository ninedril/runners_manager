import sys

msg = ' '.join(sys.argv[1:])

with open('hello.log', 'w') as f:
  f.write(msg)