console.log("new_messages.js");

function uploadImage(patient_sid) {
    $('#upload-image-error').text("");

    var data = new FormData(document.getElementById('upload-image-form'));
    data.set('sid', patient_sid);

    $.ajax({
        url: "/upload-image",
        method: "POST",
        data: data,
        enctype: 'multipart/form-data',
        success: function(data) {
            if (data["success"]) {
                console.log(channel);
                //location.reload();

            } else {
                $('#upload-image-error').text(data["message"]);
            }

            console.log(data);
            console.log('uploadImage success');
        },
        error: function(data){},
        processData: false,
        contentType: false,
    });
    console.log('uploadImage');
}

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
     * djangoUsername = identity / username logged in
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




    function clearUploadImageModal() {
        // Clears the input file selection.
        var input = $('#id_image');
        input.wrap('<form>').closest('form').get(0).reset();
        input.unwrap();
    }
    $('#close-upload-image-btn').click(clearUploadImageModal);
    $('#x-upload-image-btn').click(clearUploadImageModal);

     // Clear it initially upon page load.
    clearUploadImageModal();



    // Print out previous messages.
    function loadPreviousMessages(twilioChannel) {

        twilioChannel.getMessages().then(function(messages) {

            messages.items.forEach(function(message) {
                displayMessage(message, twilioChannel);
            })

        });
    }

    // Helper function to print chat message to the chat window
    function displayMessage(message, twilioChannel) {
        var $user = $('<span class="username">').text(message.author+ ' [' + message.timestamp.toString() + ']: ');
        if (message.author === djangoUsername) {
            $user.addClass('me');
        }

        var $message;
        if ('blob_name' in message.attributes && 'container_name' in message.attributes) {
            $image = $('<img class="img-message">');
            $image .attr('src', "https://palliassistblobstorage.blob.core.windows.net/" + message.attributes['container_name'] + "/" + message.attributes['blob_name']);

            $message = $('<div>');
            $message.append($image);

        } else {
            $message = $('<span class="message">').text(message.body);
        }

        var $container = $('<div class="message-container">');
        var $chatWindow = $('#' + twilioChannel.uniqueName + '-chat-messages');

        $container.append($user).append($message);
        $chatWindow.append($container);
        $chatWindow.scrollTop($chatWindow[0].scrollHeight);
    }


    // Set up channel after it has been found
    function setupChannel(twilioChannel) {
        loadPreviousMessages(twilioChannel);

        // Listen for new messages sent to the channel
        twilioChannel.on('messageAdded', function(message) {
            displayMessage(message, twilioChannel);
        });
    }


    // Initialize the IP messaging client
    // var token set in html. from django variable.
    accessManager = new Twilio.AccessManager(token);
    //messagingClient = new Twilio.IPMessaging.Client(accessManager);
    messagingClient = new Twilio.Chat.Client(token);
    messagingClient.initialize().then(function() {

        // Save the first channel in the list to var channel.
        var promise = messagingClient.getChannelByUniqueName(channels[0]['unique_name']);
        promise.then(function(ch) {
            channel = ch;
        });

        // Get all channels
        channels.forEach(function(channel) {

            var promise = messagingClient.getChannelByUniqueName(channel['unique_name']);
            promise.then(function(twilioChannel) {

                if (!twilioChannel) {
                    console.log('ERROR channel = null');
                } else {
                    setupChannel(twilioChannel);
                }
            });
            
        });

        /* Detects which channel is clicked on and saves it to local var channel. */
        $('.chat-list-item').each(function() {
            $(this).click(function() {
                //var sid = $(this).attr('href').slice(1); // Ignore the # in the href
                var uniqueName = $(this).attr('href').slice(1); // Ignore the # in the href
                //var promise = messagingClient.getChannelBySid(sid);
                var promise = messagingClient.getChannelByUniqueName(uniqueName);
                promise.then(function(ch) {
                    channel = ch;
                });
            })
        })

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

        $('#upload-image-btn').click(function() {
            patientUsername = $('#messages-panel-body').children('.active').attr('id');

            $('#upload-image-error').text('');

            var data = new FormData(document.getElementById('upload-image-form'));
            data.set('username', patientUsername);

            $.ajax({
                url: "/upload-image",
                method: "POST",
                data: data,
                enctype: 'multipart/form-data',
                success: function(data) {
                    if (data['success']) {
                        channel.sendMessage('Image sent.', {'blob_name': data['blob_name'], 'container_name': data['container_name']});
                        $('#upload-image-modal').modal('hide');

                        //location.reload();

                    } else {
                        $('#upload-image-error').text(data['message']);
                    }

                    console.log(data);
                    console.log('uploadImage success');
                },
                error: function(data){
                    if (data['success']) {
                        //location.reload();

                    } else {
                        $('#upload-image-error').text(data['message']);
                    }
                },
                processData: false,
                contentType: false,
            });
            console.log('uploadImage');
        })

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




});

