import socketserver
import socket
import os


# noinspection PyAttributeOutsideInit
class ClientHandler(socketserver.StreamRequestHandler):

    def setup(self):
        super().setup()
        self.data_socket = None
        self.quit = False
        self.binary = False

    def handle(self):
        """ called in its own thread when a client is accepted """
        self.send(220, "Welcome")
        while not self.quit:
            cmd, args = self.receive()
            print("received", cmd, args)
            if cmd is None:
                self.quit = True
            else:
                getattr(self, "cmd_" + cmd.lower(), self.cmd_unknown)(args)

    def cmd_unknown(self, args):
        self.send(504, "Hum, I don't know that")

    def cmd_user(self, args):
        self.send(331)

    def cmd_pass(self, args):
        self.send(230)

    def cmd_syst(self, args):
        self.send(230)

    def cmd_port(self, args):
        host, port = ClientHandler.parse_port(args)
        self.data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.data_socket.connect((host, port))
        self.send(200, "I just connected back to you")

    def cmd_list(self, args):
        self.send_data(self.encode("\n".join(os.listdir('.')) + "\n", binary=False))

    def cmd_retr(self, args):
        try:
            with open(args, "r" + ("b" if self.binary else "")) as file:
                self.send_data(self.encode(file.read()))
        except FileNotFoundError:
            self.send(450, "I don't know that")
        except Exception as e:
            print(e)
            self.send(452, "Holly shit, that was bad !")

    def cmd_stor(self, args):
        try:
            with open(args, "w" + ("b" if self.binary else "")) as file:
                self.send(150, "I'm ready to handle your data, let's go !")
                buffer = self.data_socket.recv(4096)
                print("received data buffer", buffer)
                file.write(self.decode(buffer))
                while len(buffer) > 0:
                    buffer = self.data_socket.recv(4096)
                    print("received data buffer", buffer)
                    file.write(self.decode(buffer))
                self.data_socket.close()
                self.data_socket = None
                self.send(226, "All right !")
        except Exception as e:
            print(e)
            self.send(452, "Holly shit, that was bad !")

    def encode(self, s_data, binary=None):
        if binary is None:
            binary = self.binary

        if self.binary:
            return bytes(s_data)
        else:
            return bytes(s_data.replace("\n", "\r\n"), encoding="ascii")

    def decode(self, b_data, binary=None):
        if binary is None:
            binary = self.binary

        if binary:
            return b_data
        else:
            return b_data.decode("ascii").replace("\r\n", "\n")

    def cmd_type(self, args):
        if args == "I":
            self.binary = True
        elif args == "A":
            self.binary = False
        else:
            return self.cmd_unknown(args)

        self.send(200, "Command OK")

    def cmd_quit(self, args):
        self.send(200, "Bye, Thanks for visiting bro !")
        self.quit = True

    def send_data(self, data):
        """
        this function send data on the data socket
        but also takes care of sending various status on the control socket
        and closing the resources when it's done
        """
        self.send(150, "I'm going to send you the data, enjoy !")
        print("send data\n=============\n", data, "\n============")
        self.data_socket.sendall(data)
        self.data_socket.close()
        self.data_socket = None
        self.send(226, "Ok that was all.")

    def send(self, code, message="OK"):
        """ send a code and a message """
        print("send", code, message)
        data = bytes("%d %s\r\n" % (code, message), encoding="utf-8")
        self.request.sendall(data)

    def receive(self):
        """ read a line and return a tuple (command, args) """
        line = self.rfile.readline().decode("utf-8").strip()
        # line = str(self.request.recv(256))
        array = line.split()
        cmd = array[0] if len(array) >= 1 else None
        args = array[1] if len(array) >= 2 else None
        return cmd, args

    @staticmethod
    def parse_port(args):
        """
        parse the arguments of PORT command
        and return a tuple (host, port)
        """
        try:
            array = args.split(",")
            host = ".".join(array[:4])
            port = int(array[4]) * 256 + int(array[5])
            return host, port
        except ValueError:
            return None


if __name__ == "__main__":
    HOST, PORT = "localhost", 5557

    server = socketserver.TCPServer((HOST, PORT), ClientHandler, bind_and_activate=False)
    server.allow_reuse_address = True
    server.server_bind()
    server.server_activate()
    server.serve_forever()
