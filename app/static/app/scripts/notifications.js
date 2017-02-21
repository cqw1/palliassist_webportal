console.log("notifications.js");

var radioMap = {
    'esas': 'Complete ESAS survey',
    'pain': 'Complete pain survey',
    'medication': 'Take medication',
    'other': '',
}

function handleRadioClick(radio) {
    $('#create-notification-message').val(radioMap[radio.value]);

    if (radio.value == "other") {
        $('#create-notification-message').focus();
    }

}

$(function() {
    /*
    // Clears the input fields in the modal to add a new member.
    function clearCreateNotificationModal() {
        $('#create-notification-message').val('Complete ESAS survey');
    }
    $('#close-create-notification-btn').click(clearCreateNotificationModal);
    $('#x-create-notification-modal-btn').click(clearCreateNotificationModal);

     // Clear it initially upon page load.
    clearCreateNotificationModal();
    */

    function resetCreateNotificationModal() {
        $('#esas-radio').prop('checked', true);
        $('#create-notification-message').val(radioMap[$('input[name=category]:checked').val()]);
    }

    $('#create-notification-modal-btn').click(resetCreateNotificationModal);

});

