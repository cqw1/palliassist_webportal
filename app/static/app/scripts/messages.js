console.log("new_messages.js");

$(function() {
    // Manages the state of our access token we got from the server
    var accessManager;

    // Our interface to the IP Messaging service
    var messagingClient;

    // A handle to the chat channel and div to display messages on
    var channel;     
    var $chatWindow;

    /*
     * Variables passed from Django
     * django_username = identity / username logged in
     * token = twilio token
     * channels = list of channels
     */

    // Clears the input fields in the modal to add a new member.
    function clearAddMemberModal() {
        $('#add-username').val('');
    }
    $('#close-add-modal-btn').click(clearAddMemberModal);
    $('#x-add-modal-btn').click(clearAddMemberModal);

     // Clear it initially upon page load.
    clearAddMemberModal();

    // Initialize the IP messaging client
    // var token set in html. from django variable.
    accessManager = new Twilio.AccessManager(token);
    messagingClient = new Twilio.IPMessaging.Client(accessManager);

    // Save the first channel in the list to var channel.
    var promise = messagingClient.getChannelBySid(channels[0]['sid']);
    promise.then(function(ch) {
        channel = ch;
    });

    // Get all channels
    channels.forEach(function(channel) {
        var promise = messagingClient.getChannelBySid(channel['sid']);
        promise.then(function(twilioChannel) {
            if (!twilioChannel) {
                console.log('ERROR channel = null');
            } else {
                setupChannel(twilioChannel);
            }
        });
        
    });

    // Set up channel after it has been found
    function setupChannel(twilioChannel) {
        loadPreviousMessages(twilioChannel);

        // Listen for new messages sent to the channel
        twilioChannel.on('messageAdded', function(message) {
            printMessage(message, twilioChannel);
        });
    }

    // Print out previous messages.
    function loadPreviousMessages(twilioChannel) {
        twilioChannel.getMessages().then(function(messages) {
            var totalMessages = messages.length; 

            for (var i = 0; i < messages.length; i++) {
                var message = messages[i];

                printMessage(message, twilioChannel);
            }
        });
    }

    // Helper function to print chat message to the chat window
    function printMessage(message, twilioChannel) {
        var $user = $('<span class="username">').text(message.author+ ' [' + message.timestamp.toString() + ']: ');
        if (message.author === django_username) {
            $user.addClass('me');
        }
        var $message = $('<span class="message">').text(message.body);
        var $container = $('<div class="message-container">');
        var $chatWindow = $('#' + twilioChannel.sid + '-chat-messages');

        $container.append($user).append($message);
        $chatWindow.append($container);
        $chatWindow.scrollTop($chatWindow[0].scrollHeight);
    }


    // Send a new message to the current channel on [Enter].
    var $chatInput = $('#chat-input');
    $chatInput.on('keydown', function(e) {
        if (e.keyCode == 13) {
            channel.sendMessage($chatInput.val())
            $chatInput.val('');
        }
    });

    // Send a message to the current channel when 'Send' button is clicked.
    $('#send-message-btn').click(function() {
        channel.sendMessage($chatInput.val())
        $chatInput.val('');

    })

    /* 
     * Send a POST request to add members to current channel on the backend.
     */
    $('#add-member-btn').click(function() {
        $('#add-member-btn').html('Adding...');
        $('#add-member-btn').prop('disabled', true);

        data = {
            'csrfmiddlewaretoken': Cookies.get('csrftoken'),
            'channel_name': $('#new-message-name').val(),
            'new_members': $('#add-username').val(),
        }

        $.post('/add-member', data, function(response) {
            location.reload();
        });

    });

    /* Detects which channel is clicked on and saves it to local var channel. */
    $('.chat-list-item').each(function() {
        $(this).click(function() {
            var sid = $(this).attr('href').slice(1); // Ignore the # in the href
            var promise = messagingClient.getChannelBySid(sid);
            promise.then(function(ch) {
                channel = ch;
            });
        })
    })

});

