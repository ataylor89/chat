# readme

## Requirements

At the time of writing, this project has only one external dependency.

The external dependency is a library called tzlocal. It can be used to get a system's IANA time zone name.

I use this library to get the client's local date and time. (Both date and time depend on timezone.)

In particular, I use tzlocal to implement the "/date" and "/time" commands.

The tzlocal dependency can be installed with the following command:

    pip install tzlocal

Alternatively, it can be installed using the requirements.txt file as an input.

    pip install -r requirements.txt

This dependency has to be installed in order for the program to work.

If you don't want to install the dependency, you can modify the implementation of the "/date" and "/time" commands, so that they don't rely on tzlocal.

It's possible to modify the implementation of the "/date" and "/time" commands, so that they rely on the standard library and only the standard library.

The reason I use tzlocal is that it made the implementation simpler. I tried doing it without tzlocal, but found it a little difficult.

So I use tzlocal because it makes time zones easier to work with.

## Usage

The chat server can be run with the following commands:
    
    % cd ~/Github/chat/src
    % python -m server.main

    # ICYW, when you run a script, the directory of the script becomes the top-level directory
    # So if I ran the command `python src/server/main.py`, the Python interpeter wouldn't be able to find the files inside the shared package
    # The src/server folder would be the top-level directory, and it wouldn't be able to locate files like shared/packet_io.py
    # That's why I run it as a module

The chat client can be run with the following commands:

    % cd ~/Github/chat/src
    % python -m client.main

Then I open the window of the chat client, and type the command "/connect".

This opens a socket to my chat server at localhost:12345.

It also sends the client's public key to the server, and waits to receive the server's public key, before continuing.

(These steps are needed in order to enable encryption.)

So... just to review.

The command for starting the server is `python -m server.main`.

The command for starting the client is `python -m client.main`.

I'm planning to make a lot of improvements to this project. It's still a work in progress.

## Usage (detailed)

I do a lot of my computer work in Terminal.

For example, I write source code in Terminal, I write readmes in terminal, I run and compile programs in Terminal.

What is Terminal? Terminal is a command-line processor for MacOS.

Terminal is pre-installed with MacOS. You can find it by opening Finder, going to Application->Utilities, and double clicking on Terminal.

After you open Terminal, it should show up in your Dock.

You can right-click on the Terminal icon in your Dock, go to Options, and then check "Keep in Dock".

This makes it easier to find and open Terminal in the future. You can launch it straight from your Dock, by clicking on the Terminal icon in your Dock.

So, let's assume that you have opened Terminal and you see it on your screen.

I like to maximize the Terminal window so it fills up the screen.

Also, I like to set a color theme. You can set a color theme by going to Terminal->Settings, which appears in the menu bar at the top of your screen. The Terminal menu should be to the right of the Apple logo. The Apple logo is in the upper left corner of your screen.

(The menu bar might be hidden, but if you move your cursor to the top of your screen, it will show up.)

So, let's assume that Terminal is open.

I use the key sequence command+t to open a new tab in terminal.

Let's open two tabs, to create a total of three tabs.

In the first tab, I type the following commands:

    % cd ~/Github/chat/src

    # If you don't have tzlocal installed, then you can run this command, but it only needs to be run once
    % pip install tzlocal
    
    % python -m server.main

In the second tab, I type the following commands:

    % cd ~/Github/chat/src
    % python -m client.main

In the third tab, I type the following commands (it's the same as above):

    % cd ~/Github/chat/src
    % python -m client.main

After doing this, we have run our server program, and we have created two instances of our client program.

The server program (chat server) is running, listening for connections.

The two client programs are running an event loop, listening for keyboard input.

In the bottom right of your screen, in the Dock, you should see two Python icons.

You can click on each of them to open up the chat client windows.

You should have two chat client windows.

Why two? Because we want to make sure that messages from Client1 are able to reach Client2, and vice versa.

I type the command "/connect" in each of my chat windows. Both of my chat clients connect to the server.

I am able to see Client-1 and Client-2 in the userlist.

Now, let's register a user.

In the first chat window, I type the command "/register Sun testpw1".

This registers user "Sun" with password "testpw1".

Now I log in. In the first chat window, I type the command "/login Sun testpw1".

The server responds with a message, saying that I logged in as user "Sun".

In the second chat window, I type the command "/register Moon testpw2".

Now I log in. In the second chat window, I type the command "/login Moon testpw2".

The server responds and says that I logged in as user "Moon".

Now the userlist shows two users, "Sun" and "Moon".

I send the message "hello moon" from the first chat window. It appears in both of my chat windows. It appears as a message from "Sun".

I send the message "hello sun" from the second chat window. It appears in both of my chat windows. It apppears as a message from "Moon".

Voila. It works. Our chat server (instant messenger) works.

There are more commands we can run. For example, in the first chat window I type the command "/date". It shows me the current date.

Then I type the command "/time". It shows me the current time.

Then I type the command "/whoami". It shows me the client name, client IP, and client port, of the chat client.

(It actually shows the port that the client is listening on. A connection consists of two sockets. A socket is defined by an IP address and a port.)

In addition, the "/whoami" command shows my username.

If you run "/whoami" in both chat windows, you can see that the chat clients have the same IP (127.0.0.1) but different ports.

Let's draw a diagram.

```
Client socket                                                           Server socket
IP address: 127.0.0.1 ------------------ connection ------------------  IP address: 127.0.0.1
Port: ad hoc port                                                       Port: 12345
```

You can see that a connection is defined by two sockets, and a socket is defined by an IP address and a port.

The IP of the server socket does not have to be localhost (127.0.0.1). It can be the IP of a remote machine, like an EC2 instance on AWS cloud.

The IP of the client socket is either localhost (127.0.0.1) or the public IP address of the local machine.

The port of the client socket is "ad hoc" because the operating system creates an ad hoc port for the client socket when it opens a connection.

The port of the server socket is predetermined, because the server chooses which port it wants to listen on... and it has to choose an available port.

I wanted to talk a little about sockets and connections. But I digress.

I wanted to give this detailed guide on usage. You can see that I do almost everything in Terminal, from coding to writing readmes.

To review, we opened three tabs in Terminal to test the chat client and the chat server.

In the first tab, we ran the server program, with the following commands:

    % cd ~/Github/chat/src
    % python -m server.main

In the second tab, we ran an instance of the chat client, with the following commands:

    % cd ~/Github/chat/src
    % python -m client.main

In the third tab, we ran another instance of the chat client, with the following commands:

    % cd ~/Github/chat/src
    % python -m client.main

I wanted to make sure that messages from one client reach another client, so I tested the software by creating one server and two clients.

To exit the program, we can use the "/exit" command.

I type the "/exit" command in the first chat window, and it exits the program.

I type the "/exit" command in the second chat window, and it exits the program.

I think that concludes our detailed usage guide.

I hope this was enjoyable and instructive.

As I said before, I do almost everything in Terminal and vi.

My coding environment primarily consists of Terminal and vi.

I have a MacBook running MacOS Sequoia on an Apple M1 chip.

One reason I like MacBooks, is that I want to be able to use Terminal and vi.

The shell programs used in Terminal, bash or zsh, are available on MacOS, Unix and Linux.

The text editor vi is available on MacOS, Unix, and Linux.

I think that's all for now.

I might add more to this readme later.

For example, I plan to write a section on generating a custom RSA key.

## Generating a custom RSA key

I use the code in my [rsa](https://github.com/ataylor89/rsa) project to generate a custom RSA key.

The first step is to open Terminal. Then I type the following commands in Terminal.

    # Navigate to the directory of the rsa project
    % cd ~/Github/rsa

    # Generate a prime table consisting of 10,000 primes
    % python primetable.py 1e4

    # Create 128 RSA keys from this prime table, with the condition that p and q are beneath 10,000
    % python keytable.py 128 -tmax 1e4

    # Create an RSA key of length 64, which means that the RSA key consists of 64 (n, e, d) tuples
    # Also, stipulate that the keys used are based on primes less than 10,000
    # Write to a file named custom_key_client.txt
    % python keygen.py 64 -tmax 1e4 -o custom_key_client.txt

    # The last key was for the client
    # Now we will do the same for the server, using the same parameters
    % python keygen.py 64 -tmax 1e4 -o custom_key_server.txt

I wanted to explain each command in comments. Here are the commands, without comments.

    % cd ~/Github/rsa
    % python primetable.py 1e4
    % python keytable.py 128 -tmax 1e4
    % python keygen.py 64 -tmax 1e4 -o custom_key_client.txt
    % python keygen.py 64 -tmax 1e4 -o custom_key_server.txt

After completing these steps, we have created a custom RSA key for the client, and another custom RSA key for the server.

We can copy these keys into the rsa folder, within the chat project, with the following commands.

    % cd ~/Github/rsa

    % ls custom_key*
    custom_key_client.txt	custom_key_server.txt

    % cp custom_key_client.txt ~/Github/chat/src/client/rsa/customkey.txt

    % cp custom_key_server.txt ~/Github/chat/src/server/rsa/customkey.txt

    % ls ~/Github/chat/src/client/rsa
    customkey.txt	defaultkey.txt

    % ls ~/Github/chat/src/server/rsa
    customkey.txt	defaultkey.txt

We just copied the client's custom key into the client's rsa folder, and the server's custom key into the server's rsa folder.

Now we have to edit the configuration files so they point to the custom key.

The rsa section of my client/config/client_settings.ini file looks like this:

    [rsa]
    keypath = rsa/customkey.txt

Similarly, the rsa section of my server/config/server_settings.ini file looks like this:

    [rsa]
    keypath = rsa/customkey.txt

Okay, I think that's all the changes we have to make.

To review, the steps we took are the following:

1. We navigated to the ~/Github/rsa folder to use the scripts in that folder
2. We used primetable.py, keytable.py, and keygen.py to create custom RSA keys for the client and the server
3. We copied the client's custom key into the client's rsa folder
4. We copied the server's custom key into the server's rsa folder
5. We edited client/config/client_settings.ini and server/config/server_settings.ini to point to the custom key files

After completing these steps, I tested the chat server with two chat clients, using the custom RSA keys that we generated.

It works like a charm. All we did was simply swap the default key with the custom key, for the client and the server.

This way, the public and private keys are secret. (If we use the default key, they're not secret.)

One of the main ideas behind public key cryptography is this...

If your public key gets discovered, when it is being sent over a network, the message is still secure, because the person who discovers it needs to derive the private key in order to decrypt the message.

If you use a large public key, with large p and q values, then it is hard to derive the private key. It is a difficult problem, computationally, when the p and q values are large enough. It is hard to factor large numbers, and it is even harder to derive the decryption exponent given the modulus.

That's the nice thing about public key cryptography.

What if you used symmetric key cryptography, instead of public key (asymmetric) cryptography?

What if you used an XOR algorithm to encrypt your messages?

If you use a symmetric key algorithm like XOR, and your key gets discovered, then it can be used to decrypt your messages.

This is why public key cryptography is so useful.

If your key gets discovered, it is still really hard to decrypt the message.

The chat client sends its public key to the server, but it keeps its private key a secret.

The private key stays on the local machine, and doesn't leave the local machine.

The public key is used to encrypt messages, and the private key is used to decrypt messages.

To be more specific...

The client uses the server's public key to encrypt messages that it sends to the server.

The server uses the server's private key to decrypt messages that it receives from the client.

The server uses the client's public key to encrypt messages that it sends to the client.

The client uses the client's private key to decrypt messages that it receives from the server.

This is how public key cryptography works.

When the client connects, the client and server create a secure connection, by exchanging public keys.

The process of exchanging public keys is often called an RSA handshake.

The handshake itself is unencrypted... because we need to exchange public keys before we create an encrypted connection.

But everything after the handshake is encrypted.

I wanted to take some time to talk about public key cryptography.

I find cryptography to be a fascinating subject.

I believe that the RSA encryption algorithm is used in the SSH and HTTPS protocols. This makes it a widely used algorithm.

I think that wraps up this section...

It's a lot to process, but I wanted to explain the encryption mechanism in detail.
