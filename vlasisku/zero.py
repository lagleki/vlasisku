import zerorpc
import subprocess
import os.path

# this only happens once, since modules are singletons
server = subprocess.Popen(['node', 'zmq'],
                          cwd=os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                           'ilmentufa'))
client = zerorpc.Client()
client.connect("tcp://127.0.0.1:4242")

def parse(text, grammar="", rule="text", mode=1):
    result = client.parse(text, grammar, rule, mode)
    if isinstance(result, dict):
        raise Exception("%(name)s from camxes: %(message)s (line %(line)d, column %(column)d, offset %(offset)d)" % result)
    else:
        return eval(result)

