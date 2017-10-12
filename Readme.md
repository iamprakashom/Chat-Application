##### 1. Introduction
Chat console application contains one module - chatServer. Server uses `localhost` as ip address and port - 8500. After starting the server module, a client can connect to server by using telnet command with same ip address (`localhost` or `127.0.0.1`) and port number - 8500.

##### 2. How to Run
Application uses python's inbuilt library, thus no hassles of installing library.

######  2.1 Run chatServer(Server) :
``python chatServer.py``

###### 2.2 To connect client to server:
`telnet <ip> <port>`

where ip = localhost/127.0.0.1 and port = 8500

e.g. - open new terminal and type this command

``telnet 127.0.0.1 8500``

or

``telnet localhost 8500``


Note : Max number of client allowed to connect with server is 5.

###### 2.3 To login :
``login <user_name>``

e.g. - ``login anaconda``

###### 2.4 To Chat/send message:
To send message, use `say` command

`say <message>`

e.g.`say Hello bro`

###### 2.4 To end session :
To end the chat session, use `stop` command.

   e.g. `stop`


##### Screenshot
![](https://github.com/iamprakashom/Chat-Application/blob/master/screenshot.png)
