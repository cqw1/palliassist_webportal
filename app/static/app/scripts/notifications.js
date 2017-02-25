console.log("notifications.js");

var selectedCategory = '';
var selectedText = '';

var radioMap = {
    'esas': 'Complete ESAS survey',
    'pain': 'Complete pain survey',
    'medication': 'Take medication',
    'other': '',
}


function createNotification(patient_id) {
    var category = $('input[name=category]:checked').val().toUpperCase();
    var text = $('#id_text').val();
    var primary_key = '';

    fcmCreateNotification(patientUsername, category, text, primary_key);

    $.post('/create-notification', $("#create-notification-form").serialize() + "&sid=" + patient_id, function() {
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

    $('#create-notification-btn').click(function() {
    })

    //$('input:radio').click(function() {
    $('input[name=category]').click(function() {
        // id is auto-generated in CreateNotificationForm based on category field.
        $('#id_text').val(radioMap[$(this).val()]);

        if ($(this).val() == "other") {
            $('#id_text').focus();
        }
    });

});

