# readme

## Usage

The chat server can be run with the following commands:
    
    # First, I navigate to the root directory of the project, which for me is ~/Github/chat
    % cd ~/Github/chat

    # Now, I run the chat server
    % python -m src.server.main

    # ICYW, when you run a script, the directory of the script becomes the top-level directory
    # So if I ran the command `python src/server/main.py`, the Python interpeter wouldn't be able to find the files inside the shared package
    # The src/server folder would be the top-level directory, and it wouldn't be able to locate files like shared/packet_io.py
    # That's why I run it as a module

The chat client can be run with the following commands:

    % cd ~/Github/chat
    % python -m src.chat.main

Then I open the window of the chat client, and type the command "/connect".

This opens a socket to my chat server at localhost:12345.

It also sends the client's public key to the server, and waits to receive the server's public key, before continuing.

(These steps are needed in order to enable encryption.)

So... just to review.

The command for starting the server is `python -m src.server.main`.

The command for starting the client is `python -m src.client.main`.

I'm planning to make a lot of improvements to this project. It's still a work in progress.
