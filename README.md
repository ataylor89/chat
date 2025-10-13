# chat

## Deploying to AWS cloud (foreword)

Today, I was able to successfully deploy my chat application to AWS cloud

It took some investigative work to set it up properly

First, I fixed a small problem in packet_io.py

I was getting the error "to_bytes requires an additional argument... byteorder... etc"

In my file packet_io.py, I was using the phrase packet_type.to_bytes(1) in certain places

I had to change this phrase to packet_type.to_bytes(1, byteorder="big"), so that it includes the required byteorder argument

After making that change, the error went away, and it worked

Now, let's describe the process that I used to deploy my chat application to AWS cloud

## Deploying to AWS cloud (download script)

In order to run my chat server on AWS cloud, I have to download the code to my EC2 instance

I used the following script to download the code to my EC2 instance

    #!/usr/bin/bash

    # This script downloads the code that is needed for the chat application
    # Sunday, October 12, 2025

    # Create the config folder if it does not exist
    if [ ! -d "config" ]; then
            mkdir config
    fi

    # Create the rsa folder if it does not exist
    if [ ! -d "rsa" ]; then
            mkdir rsa
    fi

    # Download all of the files that are needed
    export prefix="https://raw.githubusercontent.com/ataylor89/chat/refs/heads/main"
    curl -O $prefix/client.py
    curl -O $prefix/cmdlist.py
    curl -O $prefix/gui.py
    curl -O $prefix/packet_io.py
    curl -O $prefix/packet_types.py
    curl -O $prefix/packet_utils.py
    curl -O $prefix/server.py
    curl -o config/client_settings.ini $prefix/config/client_settings.ini
    curl -o config/server_settings.ini $prefix/config/server_settings.ini
    curl -o rsa/decrypt.py $prefix/rsa/decrypt.py
    curl -o rsa/encrypt.py $prefix/rsa/encrypt.py
    curl -o rsa/keygen.py $prefix/rsa/keygen.py
    curl -o rsa/keytable.py $prefix/rsa/keytable.py
    curl -o rsa/parser.py $prefix/rsa/parser.py
    curl -o rsa/primetable.py $prefix/rsa/primetable.py
    curl -o rsa/privatekey.txt $prefix/rsa/privatekey.txt
    curl -o rsa/publickey.txt $prefix/rsa/publickey.txt
    curl -o rsa/util.py $prefix/rsa/util.py

I logged into my EC2 instance, via ssh

I created a chat folder in the home directory of my EC2 instance

Then I saved the script (above) in the chat folder, as download.sh

I made it executable with the command `chmod +x download.sh`

Then I executed the script with the command `./download.sh` within the chat directory

The script downloaded all of the needed files, which brought me one step closer to deploying my server

## Deploying to AWS cloud (setting up the EC2 instance)

This step actually precedes the previous step, so it's a little out of order

I logged into the AWS console on AWS cloud

I use the link https://*.signin.aws.amazon.com/console, where the * represents my account ID or alias

I logged in using my IAM username and password

Then, after logging in, I navigated to the EC2 console

I ended up using an EC2 instance that already exists, which I call, "myserver" (without the quotes)

The EC2 instance "myserver" is a basic t2.micro EC2 instance

If I remember correctly, it installs Python, and perhaps some other software, in the user data

But it's really just a basic t2.micro EC2 instance

I favor the t2.micro instance type because it's one of the cheapest offerings and it saves money

Now, here's the important part

We have to add a rule to our security group rules in order to allow a client to connect to our server

When I select "myserver" and then click on the Security tab, I see the following...

There is a security group called "launch-wizard-3" under a header that says "Security groups"

I click on this security group, launch-wizard-3, and then I see the inbound rules

Earlier today, I added a new inbound rule, which allows Custom TCP traffic from anywhere (0.0.0.0/0) to access port 12345

In addition to this, I also have an inbound rule that allows HTTP traffic from anywhere (0.0.0.0/0) to acccess port 80

Furthermore, I have an inbound rule that allows SSH traffic from anywhere (0.0.0.0/0) to access port 22

So my inbound rules consist of those three rules:

1. The first rule allows HTTP traffic from anywhere to access port 89
2. The second rule allows Custom TCP traffic from anywhere to access port 12345
3. The third rule allows SSH traffic from anywhere to access port 22

The second rule is the important one, for our purposes, because it's the only rule that is needed by the chat application

The chat server listens on port 12345, so we need to open port 12345 to the outside world, so that a client can connect to our server

The second rule accomplishes this (i.e. allowing Custom TCP traffic from anywhere to access port 12345)

So we have to make sure that the second rule is present in our inbound rules, allowing access to port 12345

After this is done, we can save our rules

We can quickly check our outbound rules

For the EC2 instance I am speaking of, named "myserver", I only have one outbound rule, which allows all outbound traffic

So, to repeat myself... my EC2 instance has only one outbound rule, which allows all outbound traffic

(The first time I said it was a little wordy so I decided to say it again)

So... just to summarize...

I have three inbound rules, and one of them allows Custom TCP traffic to access port 12345 from anywhere

I have only one outbound rule, which allows all outbound traffic

After saving our rules, we can go back to the EC2 instances console

I created an SSH key pair for my EC2 instance

I named the key file myserver.pem

I downloaded the key file to my ~/Dowloads directory

Then I typed the command `mv ~/Downloads/myserver.pem ~/myserver.pem` to move it to my home directory

Then I logged into my EC2 instance, via ssh, with the command:

    % ssh -i ~/myserver.pem ec2-user@<public-ipv4-address>

After logging in, I verified that Python was installed, with the command:

    $ python --version
    Python 3.9.23

So, the inbound rules are set up, specifically, the one rule allowing access to port 12345

I logged into my EC2 instance by means of ssh

I verified that Python is set up

I downloaded the code to my EC2 instance using the download script above

Now there is just one more step we have to take

We can modify the server_settings.ini file inside the config folder to look like this:

[default]
host = 0.0.0.0
port = 12345

The IP addresses 0.0.0.0 and 127.0.0.1 mean slightly different things

I don't fully understand it... but in order to listen for connections from the outside world... I think we have to use 0.0.0.0

It might be that the IP address 127.0.0.1 doesn't really listen for connections from the outside world...

The IP address 127.0.0.1 means "localhost" and it refers to the local machine

If we use 127.0.0.1 as our host, it might only listen for connections coming from the same machine, i.e. localhost

If we use 0.0.0.0 as our host, then it listens for connections from the outside world

In fact, it listens for connections that originate outside of our virtual private cloud (VPC)

So if we use 0.0.0.0 for our host address, we are good to go, and we can accept connections from the outside world

In the next section, we will review all of the steps that we took

## Deploying to AWS cloud (quick review)

Here are the steps we took to set up our environment

1. I created a t2.micro EC2 instance called "myserver"
2. I created an SSH key pair for my EC2 instance, and I named the key file "myserver.pem"
3. I downloaded the key file, myserver.pem, and moved it to my home directory
4. I edited the user data of my EC2 instance to download Python3, by making a call to yum
5. I edited the security group rules for my EC2 instance, and added an inbound rule that allows Custom TCP traffic to access port 12345 from anywhere
6. I verified that the outbound rules for my EC2 instance allow all outbound traffic
7. I logged into my EC2 instance by ssh, with the command `ssh -i ~/myserver.pem ec2-user@<public-ipv4-address>`
8. I verified that Python is setup, with the command `python --version` or `python3 --version`
9. I downloaded the code for my chat application using the download.sh script that I provided above
    - I created a folder called "chat" in the home directory of my EC2 instance
    - I created a file in this folder called "download.sh"
    - I saved the download script to download.sh
    - I made the download.sh script executable with the command `chmod +x download.sh`
    - I executed the download.sh script with the command `./download.sh`
10. Then, I edited the server_settings.ini file inside the config folder, to use 0.0.0.0 for the host address

After taking all of these steps, I think... I hope... that everything is set up

## Deploying to AWS cloud (running the server on cloud)

After everything is setup, I log into my EC2 instance, which I call "myserver", by means of ssh, using the command:

    ssh -i ~/myserver.pem ec2-user@<public-ipv4-address>

Once I am logged in, I navigate to the chat folder, which contains the source code for my chat application, using the command:

    cd chat

We can verify that it has the files with the command `ls`

So, all the files are present, at least for me, and everything is setup

The next step is to run our chat server

We can run our chat server with the following command, issued from within the chat folder:

    python server.py

The server has an infinite loop, which listens for connections

The infinite loop is defined within the method listen() in server.py

When the server accepts a new connection, it creates a new thread for that client, from which it executes a read loop

The read loop constantly checks its buffer to see if any data was received from the client

It reads the incoming data one packet at a time

A packet has two parts: a head and a body

First it reads the head, to calculate the packet length

The head is always 5 bytes long, so it reads 5 bytes to read the head of an incoming packet

The packet length is stored in the first four bytes of the header

Using Python, we can convert four bytes to an integer value

The integer value is the packet length

The fifth byte of the header is the packet type (connect, disconnect, join, leave, login, logout, userlist, message, whoami, etc)

So, after we read the header, we know the packet length, by converting the first four bytes to an integer value

The body length is equal to the packet length minus the header length

That is, the body length is equal to the packet length minus five

Once we calculate the body length, we can read the rest of the packet

Let n be the body length of the packet

Now we can read n bytes, to read the rest of the packet

We can store the n bytes that we read into a variable called body

Then we can combine the header and the body to get the entire packet

So, to return to our original topic of discussion, the server has an infinite loop that constantly listens for new connections

It spawns a readloop thread for every new connection

The readloop thread looks for incoming data in its buffer

The readloop thread reads the data one packet at a time

After reading a packet, it processes the packet, based on the packet type

For example, it has a message handler to process message packets

It also has join and leave handlers to process join and leave packets

It also has login and logout handlers to process login and logout packets

It also has a registration handler to process registration packets

So, I wanted to spend some time describing how the server works

The last statement that we executed, in our ssh session, was

    python server.py

This statement runs the server

Now we can run the client in a separate tab in Terminal

Let's open a separate tab in Terminal, and run the client, and connect to the server

## Deploying to AWS cloud (interlude)

You might ask, "Why does a packet have two parts, a head and a body?"

Well, the head has a fixed length, and the body has a variable length

We can read the head of a packet because we know how many bytes it is

In our custom packets, the head is 5 bytes long

After reading the head of a packet, we can determine the length of the body

So we read a packet in two stages

First, we read the head, to calculate the packet length, and the body length

(We can do this because we know the header length in advance)

Then, we read the body, using the body length that we calculated by processing the header

After reading the header and the body, we can combine them, to create a single, uniform packet

So... our chat application uses custom packets

I think that our chat application is an excellent example of socket programming

Packets are very useful in socket programming

Sockets allow two machines to communicate, even if they reside in different networks

For example, my MacBook can communicate with a server in a different part of the country, using a socket

A client program running on my MacBook can create a socket to connect to a server, and to send and receive data to and from the server

The server has a socket that is tasked with listening for connections

(This type of socket is called a server socket)

When the server socket accepts a new connection, it creates a socket to send and receive data to and from the client

If the server has 10 clients, then it has a total of 11 sockets (a server socket that listens for connections, and ten client sockets)

So... a program running on my MacBook can communicate with a server in a different part of the country, using a socket

When applications communicate using sockets, they communicate on top of an existing protocol stack, called the TCP/IP stack

The way it works is this...

(I'll start by defining the word "socket")

A socket is an endpoint that allows a program on one machine to communicate with a program on a different machine

A socket contains an IP address and a port: the IP address of the foreign machine, and the port that the foreign program is listening on

So if the public IP address of my EC2 instance is 12.34.56.78, and it's listening on port 12345...

Then, my client program can create a socket for IP address 12.34.56.78 and port 12345

The socket allows my client program to communicate with a server on 12.34.56.78 listening to port 12345

I think that's an adequate definition of socket

A socket is really an (IP Address, Port) pair

But it's also an endpoint that allows communication with a foreign program on a foreign machine, like, for example, a server

A client has to create a socket to communicate with a server

When a server accepts a client, it creates a socket for that client, which it uses to communicate with that client

Now, let's return to the TCP/IP stack

When applications communicate using sockets, they communicate on top of the TCP/IP stack

The first (bottom) layer of the TCP/IP stack is the Network Access Layer

The second layer of the TCP/IP stack is the Internet Layer (e.g. IP)

The third layer of the TCP/IP stack is the Transport Layer (e.g. TCP)

The fourth (top) layer of the TCP/IP stack is the Application Layer (e.g. HTTP, HTTPS, SSH, custom protocols, etc)

In our chat application, we create a custom protocol

The custom protocol sits at the Application Layer, or the fourth layer of the TCP/IP stack

We created a custom protocol out of custom packets

For example, here are some of our packet types:

    CONNECT = 1
    DISCONNECT = 2
    ENCRYPTION_ON = 3
    ENCRYPTION_OFF = 4
    JOIN = 5
    LEAVE = 6
    REGISTER = 7
    LOGIN = 8
    LOGOUT = 9
    USERLIST = 10
    MESSAGE = 11
    WHOAMI = 12
    DATE = 13
    TIME = 14

We can call our protocol the "chat" protocol

A "chat" packet has a header and a body, and the header is 5 bytes long

The body has a variable length

The first four bytes of the header are the packet length

The fifth byte of the header is the packet type

The fourteen packets, shown above, are fourteen different packet types

So the fifth byte of the header might be 1 through 14, depending on the packet type

But we might add more packets to our protocol in the future...

So, in the future, we might have packet types 15 through 20

Getting back to the original topic...

In our chat application, we created a custom protocol, which we can call the "chat" protocol

The "chat" protocol sits at the application layer, just like HTTP, HTTPS, SSH, etc

The "chat" protocol sits above the TCP layer

How does it work?

Well listen

An IP packet has a header and a body

A TCP packet is contained within the body of an IP packet

A TCP packet has a header and a body

A "chat" packet (from our application) is contained within the body of a TCP packet

That's how it works

It follows a principle called "encapsulation"

TCP packets are encapsulated within the body of an IP packet

Application layer packets are encapsulated within the body of a TCP packet

So, an HTTP packet is stored within the body of a TCP packet, just like a "chat" packet from our application

You can see how the TCP/IP stack works

Our custom packets, which I call "chat" packets, are stored within the body of a TCP packet

The TCP packet is a container for our chat packet

The TCP packet is stored within the body of an IP packet

The IP packet is the container for the TCP packet

So, it follows a principle called encapsulation

Packets are encapsulated

I'm trying to think... is there more that we should cover, before we run our client and connect to our server?

Well, we talked about socket programming, custom packets, the TCP/IP stack, and packet encapsulation

I think this gives a good background to socket programming

A socket is an endpoint defined by an (IP address, port) pair

A socket is an endpoint that allows communication with a different machine

When we run our client, we will create a socket to connect to the server, and to send and receive data to and from the server

We needed to add an inbound rule to the security group of our EC2 instance, to allow a client to connect to our server on port 12345

In effect, we had to open port 12345 to the outside world, specifically, for all Custom TCP traffic from the outside world

Is there anything more we have to cover?

Well, let's return to the insight that started this discussion

A packet has two parts, a head and a body

The head has a fixed length and the body has a variable length

In our custom protocol, a chat packet has a five-byte header and a variable-length body

First, we read the five-byte header

We calculate the packet length using the first four bytes of the header

We determine the packet type using the fifth byte of the header

The length of the packet body is the packet length minus 5, which we can call n

We read n bytes from our socket, to read the rest of the packet

Then we combine the header and the body to create a single packet

That is how we read a packet from a socket

First we read the head, then we calculate the packet length and the body length, and then we read the body

So... that is why a packet has two parts

A packet has two parts, a head and a body

Packets are a useful paradigm in socket programming

There are some alternatives, like, reading until a stop character, e.g. a null character or a newline

But if we do that... there are all kinds of complications

Packets give us a simple way of transmitting data

We send the packet length in advance, and then we read the entire packet

The head of a packet gives us the packet length, and other useful information

So the principle is... we send the packet length in a fixed-length header, and then we read the entire packet

You can see that packets are a very useful paradigm

I'm trying to find a good stopping point

I think this is a good stopping point

Packets are really one paradigm for transmitting data over a socket

Packets are a very useful paradigm, and they're used everywhere

When we visit a web page using a web browser, the browser reads an HTTP packet from the web server

You can see that... packets are really the standard way of transmitting data over the internet

A web browser reads packets from a web server

An SSH client reads packets from an SSH server

A video game reads packets from a game server (e.g. the StarCraft client reads packets from Battle.net)

Packets are the standard way of transmitting data over the internet

## Deploying to AWS cloud (running our client and connecting to our server)

Before our interlude, we ran the Python server from within our SSH session with the EC2 instance

    python server.py

We can actually run the server in the backround with the command

    python server.py &

This way, if we log out of our SSH session, the server will still be running in the background

Now, let's open a new tab in Terminal (I"m using MacOS Sequoia on an Apple M1 ARM64 chip)

In the new tab, cd into the chat directory

(We need to download the chat code to our local machine, in addition to the EC2 instance)

So let's navigate to the chat directory on our local machine

Now, from within the chat directory, we can type the command:

    python client.py

This will open up a GUI

I actually see a rocket icon in my dock, and I can click on the rocket icon to bring up the GUI

Once we are focusing on the chat client GUI, we can type the following command from within the bottom text area:

    /connect <public-ipv4-address> 12345

If the public IPv4 address of our EC2 instance is 87.65.43.21, then we can type the command:

    /connect 87.65.43.21 12345

Hopefully, this will work

Hopefully, our chat client will connect to the chat server, after we enter this command

After entering the connect command, I got this response from the server:

    Server: Client-1 has connected to the server

Now I can turn encryption on with the command:

    /encryption on

I get the response:

    Server: Encryption turned on for Client-1

Now that encryption is turned on, I can join the chat room, and log in using my username

    /join

I get this response from the server:

    Server: Client-1 joined the chat room

Now I would like to register my username

    /register ktm5124 thisisatestpw

I get the response:

    Server: The username ktm5124 was successfully registered

Now I can log in

    /login ktm5124 thisisatestpw

I get the response:

    Client-1 logged in as ktm5124

So I am logged in as ktm5124

I was able to connect to the server, register the account, join the channel, log into the account

Now let's try sending a message

I type the message "hello world" in the bottom text area, and press the <return> key

The message appears in the top text area, as:

    ktm5124: hello world

So you can see that various features are working correctly

I caution my reader... there are still many problems in the software, problems that I have to fix

So, if you test it out, you might run into some problems

But I was able to test the above functionality successfully

I was able to connect a client on my personal MacBook to a server on my EC2 instance, turn on the encryption feature, register a username, join the chat room, log into the username, and send a "hello world" message to the chat room

In essence, I was able to deploy my chat application to AWS cloud

It really works as well as it does on my local computer

That is... the server runs just as smoothly on AWS cloud as it runs on my local computer

So, we can call this a success

I was able to deploy my chat application, successfully, to AWS cloud

We were able to open port 12345 on the EC2 instance to the outside world by creating a new inbound rule

We ran the server on the host address 0.0.0.0, so it can accept connections from the outside world

After following all of the steps outlined above, we were able to execute a successful test run

Now, it's important to say, when I read a book or a document, I don't always read it start to finish, cover to cover

I often skip around and only read what I want to read or what I need to read

I think I have reached a good stopping point...

The conclusion is this: we successfully deployed our chat application to AWS cloud

Our deployment was successful, and our test run was successful

It's time to celebrate, perhaps by watching an episode of The Legend of Korra

I might get something to eat and drink, and watch an episode of The Legend of Korra

Thanks for reading

Today is Sunday October 12 2025

I'm probably going to relax, watch some TV, and have a nice meal

The purpose of this document is to teach the reader how to deploy a chat server to AWS cloud

We have to create a new inbound rule to open a port (like 12345) to the outside world

We can run the server on the host address 0.0.0.0 to allow connections from the outside world

There might be other ways of doing it, but this way worked for me

Tomorrow is Monday, the start of a new week

I have been working through the days and the nights to get a lot of work done

I have some goals to accomplish, before I start a new project that I'm planning to undertake

The familiar cycle of day and night passes by, as I check goals off of my list of goals

After I have checked off every goal from my list of goals, I'll be ready to start a new project

So, what I'm saying is, I've been in a dream-like state the past few weeks, as I have been constantly working

My family says that Andrew stands for Always working

AW always working

AW always writing

Andrew

We r dna

I have a lot of fun with my name

Today is Sunday October 12 2025

Thanks for reading

Andrew
