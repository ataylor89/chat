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
