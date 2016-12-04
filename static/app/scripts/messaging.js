console.log("messaging.js");

$(function() {
    // Get handle to the chat div 
    var $chatWindow = $('#messages');

    console.log('chatWindow: ' + $chatWindow);

    // Manages the state of our access token we got from the server
    var accessManager;

    // Our interface to the IP Messaging service
    var messagingClient;

    // A handle to the "general" chat channel - the one and only channel we
    // will have in this sample app
    var channel;

    // The server will assign the client a random username - store that value
    // here
    var username;

    // Helper function to print info messages to the chat window
    function print(infoMessage, asHtml) {
        var $msg = $('<div class="info">');
        if (asHtml) {
            $msg.html(infoMessage);
        } else {
            $msg.text(infoMessage);
        }
        $chatWindow.append($msg);
    }

    // Helper function to print chat message to the chat window
    function printMessage(fromUser, message) {
        var $user = $('<span class="username">').text(fromUser + ':');
        if (fromUser === username) {
            $user.addClass('me');
        }
        var $message = $('<span class="message">').text(message);
        var $container = $('<div class="message-container">');
        $container.append($user).append($message);
        $chatWindow.append($container);
        $chatWindow.scrollTop($chatWindow[0].scrollHeight);
    }

    // Alert the user they have been assigned a random username
    print('Logging in...');

    // Get an access token for the current user, passing a username (identity)
    // and a device ID - for browser-based apps, we'll always just use the 
    // value "browser"
    $.getJSON('/token', {
        identity: username,
        device: 'browser'
    }, function(data) {
        console.log('data from /token:' + data);
        // Alert the user they have been assigned a random username
        username = data.identity;
        print('You have been assigned a random username of: ' 
            + '<span class="me">' + username + '</span>', true);

        // Initialize the IP messaging client
        accessManager = new Twilio.AccessManager(data.token);
        messagingClient = new Twilio.IPMessaging.Client(accessManager);

        channelName = 'general';
        channelFriendlyName = 'General Chat Channel';

        // Get the general chat channel, which is where all the messages are
        // sent in this simple application
        print('Attempting to join "testChannel" chat channel...');
        var promise = messagingClient.getChannelByUniqueName(channelName);
        promise.then(function(ch) {
            console.log('channel before: ' + channel);
            channel = ch;
            console.log('channel after: ' + channel);
            if (!channel) {
                console.log('channel = null');
                // If it doesn't exist, let's create it
                messagingClient.createChannel({
                    uniqueName: channelName,
                    friendlyName:channelFriendlyName
                }).then(function(channel) {
                    console.log('Created general channel:');
                    console.log(ch);
                    channel = ch;
                    setupChannel();
                }, function(err) {
                    console.log('ran into error');
                    console.log(err);
                    console.log('Found general channel:');
                    console.log(channel);
                    setupChannel();
                });
            } else {
                console.log('Found general channel:');
                console.log(channel);
                setupChannel();
            }
        })
    });

    function loadPreviousMessages() {
        channel.getMessages().then(function(messages) {
            var totalMessages = messages.length; 

            for (var i = 0; i < messages.length; i++) {
                var message = messages[i];
                printMessage(message.author, message.body);
                console.log('Author: ' + message.author);
            }
            console.log('Total Messages: ' + totalMessages);
        });
    }


    // Set up channel after it has been found
    function setupChannel() {
        // Join the general channel
        channel.join().then(function(channel) { print('Joined channel as ' 
                + '<span class="me">' + username + '</span>.', true);
        });

        // Listen for new messages sent to the channel
        channel.on('messageAdded', function(message) {
            printMessage(message.author, message.body);
        });
        loadPreviousMessages();
    }

    // Send a new message to the general channel
    var $input = $('#chat-input');
    $input.on('keydown', function(e) {
        if (e.keyCode == 13) {
            channel.sendMessage($input.val())
            $input.val('');
        }
    });
});