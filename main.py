import socket
import re
import time

def send_command(socket, cmd, delay=None, parse=True):
    cmd += b"\r" # tutti i comandi finiscono con carriage return
    socket.send(cmd) # invio
    delayed = 0.0

    if delay is not None:
        time.sleep(delay)
        delayed += delay
    
    r = read(socket, parse)

    while delayed < 1.0 and len(r) <= 0:
        d = 0.1
        time.sleep(d)
        delayed += d
        r = read(socket, parse)
    
    return r

    
def read(socket, parse=True):
    buf = bytearray() # ti tieni questo array di byte
    while True:
        # leggi tutti i byte un po' per volta 
        data = socket.recv(32)
        if not data:
            return [] # si è rotto il socket in questo caso

        buf.extend(data)

        if b'OK' in buf or b'>' in buf:
            break # mi fermo quando trovo > o OK dentro al buffer

    buf = re.sub(b"\x00", b"", buf) # tolgo tutti i null characters (per qualche motivo, c'è scritto sul manuale)

    if buf.endswith(b'>'):
        buf = buf[:-1] # tolgo > dal messaggio

    if parse == True:
        string = buf.decode("utf-8", "ignore")
        lines = [s.strip() for s in re.split("[\r\n]", string) if bool(s)]
        return lines
    else:
        return buf
    
def has(lines, text):
    for line in lines:
        if text in line:
            return True
    return False
    
def protocol_setup(socket):
    res = send_command(socket, b"0100")
    print(res)
    if has(res, "UNABLE TO CONNECT"):
        return None
    
    atdpn = send_command(socket, b"ATDPN")
    if len(atdpn) != 1:
        return None

    proto = atdpn[0]
    proto = proto[1:] if (len(proto) > 1 and proto.startswith("A")) else proto

    print("protocol is", proto)

def set_header(socket):
    send_command(socket, b'AT SH' + b'7E0' + b' ')

sock = socket.socket()
sock.connect(("192.168.0.10", 35000))
send_command(sock, b"ATZ", delay=2) # reset della board
send_command(sock, b"ATE0") # no echo dei comandi
send_command(sock, b"ATH1") # headers on
send_command(sock, b"ATL0") # linefeeds off (no caratteri magici nei messagi, grazie)
protocol_setup(sock)
# set_header(sock)
raw = send_command(sock, b"012F", parse=False) # benza
string = raw.decode("utf-8", "ignore").split() # parsing (credo)
fourth_byte = string[2:][3] # capire perché faccio questo
print(int(fourth_byte, 16) * 100 / 255)