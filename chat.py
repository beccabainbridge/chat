import socket
import select

class Server:
    def __init__(self):
        self.s = socket.socket()
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.open = True

    def fileno(self):
        return self.s.fileno()

    def bind(self, ip, port, capacity):
       self.s.bind((ip, port))
       self.s.listen(capacity)

    def timeout(self, time):
        self.s.settimeout(time)

    def read(self, clients):
        client_info = self.s.accept()
        print "accepted client at %s:%d" % (client_info[1][0], client_info[1][1])
        new_client = Client(client_info)
        clients.append(new_client)
        return new_client

    def close(self):
        self.open = False
        self.s.close()


class Client:
    def __init__(self, (client, (ip, port))):
        self.c = client
        self.ip = ip
        self.port = port
        self.name = "Unknown"
        self.open = True
        self.c.send("Welcome to chat! To change your name type 'name:' followed by your name.\nType 'listall' to see everyone in the chat. Type 'private:' followed by the \nname of a user and your message to send a private message to another user. \nType 'exit' to leave the chat.\n")

    def fileno(self):
        return self.c.fileno()

    def set_name(self, name, clients):
        self.send("** is now %s **\n" % name, clients)
        self.name = name

    def read(self, clients):
        message = self.parse_command(self.c.recv(10000), clients)
        if message: self.send(message, clients)

    def parse_command(self, text, clients):
        split = text.split()
        if not split:
            return text
        if text == "exit\n":
            self.exit(clients)
            return
        first = split[0]
        if first == "name:":
            self.set_name("".join(split[1:]), clients)
        elif first == "listall":
            self.listall(clients)
        elif first == "private:":
            self.send_private(split[1], " ".join(split[2:]), clients)
        else:
            return text

    def send(self, message, clients):
        header = self.name + ": "
        for client in clients:
            if client is not self:
                client.c.send(header + message)

    def exit(self, clients):
        clients.remove(self)
        self.send("** has left the chat **\n", clients)
        self.c.close()
        self.open = False

    def listall(self, clients):
        names = ""
        for client in clients:
            if client != self:
                if client.name:
                    names += client.name + ", "
                else:
                    names += "Unknown, "
        names = names[:-2] + "\n"
        self.c.send(names)

    def send_private(self, name, message, clients):
        for client in clients:
            if name == client.name:
                self.send("*private* " + message + "\n", [client])


def chat(ip="", port=1234, user_limit=5):
    """ initiates a chat server that listens for clients at ip:port """
    server =  Server()
    server.bind(ip, port, user_limit)
    clients = []
    while server.open:
        rs, ws, es = select.select(clients + [server], [], [])

        for r in rs:
            r.read(clients)

        if not clients:
            server.close()

if __name__ == '__main__':
    ip = input("Enter ip for server (default is localhost): ")
    port = int(input("Enter port for server (default is 1234): "))
    user_limit = int(input("Enter user limit for server (default is 5): "))
    chat(ip, port, user_limit)
