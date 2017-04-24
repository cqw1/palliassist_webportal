console.log("notifications.js");

var selectedCategory = '';
var selectedText = '';

var radioMap = {
    'esas': 'Complete ESAS survey',
    'pain': 'Complete pain survey',
    'medication': 'Take medication',
    'other': '',
}


function createNotification(patientPrimaryKey) {
    var category = $('input[name=category]:checked').val().toUpperCase();
    var text = $('#id_text').val();
    var primary_key = '';

    fcmNotification(patientUsername, 'CREATE', category, text, primary_key);

    $.post('/create-notification', $("#create-notification-form").serialize() + "&pk=" + patientPrimaryKey, function() {
        console.log('posted');
        location.reload();
    })
}

$(function() {
    // Django variables
    //
    // djangoUsername: username of logged in user
    // esasJSON: JSON array of ESAS objects
    // patientFullName: full name of patient
    // patientUsername: username of patient
    // channels: list of twilio channel names
    // token: twilio token

    // Resets the radio option to be the ESAS survey category. Correspondingly updates the message text box.
    function resetCreateNotificationModal() {
        // id is auto-generated in CreateNotificationForm based on category field.
        $('#id_category_0').prop('checked', true);
        $('#id_text').val(radioMap[$('input[name=category]:checked').val()]);
    }

    $('#create-notification-modal-btn').click(resetCreateNotificationModal);
    $('#close-create-notification-modal-btn').click(resetCreateNotificationModal);
    $('#x-create-notification-modal-btn').click(resetCreateNotificationModal);

    //$('input:radio').click(function() {
    $('input[name=category]').click(function() {
        // id is auto-generated in CreateNotificationForm based on category field.
        $('#id_text').val(radioMap[$(this).val()]);

        if ($(this).val() == "other") {
            $('#id_text').focus();
        }
    });

    $('.delete-notification').click(function() {
        var id = $(this).parent().parent().attr('id');
        // ID is notification-row-{{pk}}
        var pk = id.split('-')[2];

        $.post('/delete-notification', "pk=" + pk, function() {
            console.log('posted');
            triggerToast('Notification removed.', 'success');
        })

        $(this).parent().parent().hide();
    });

});

