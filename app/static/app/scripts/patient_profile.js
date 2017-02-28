console.log("patient_profile.js");

function clearNotes() {
    console.log("called clearNotes");
    $("#id_notes").val('');
};

function saveNotes(patientPrimaryKey) {
    console.log($("#notes-form").serialize()) + "&pk=" + patientPrimaryKey;
    $.post('/save-notes', $("#notes-form").serialize() + "&pk=" + patientPrimaryKey, function() {
        console.log('posted');

        triggerToast('Notes saved.');
    })
}

$(function() {

    // Javascript to enable link to tab
    var url = document.location.toString();
    if (url.match('#')) {
        $('.nav-tabs a[href="#' + url.split('#')[1] + '"]').tab('show');
    } 

    // Change hash for page-reload
    $('.nav-tabs a').on('shown.bs.tab', function (e) {
        window.location.hash = e.target.hash;
    })

    $('.millis-date').each(function() {
        // Replace all the elements with class millis-date.
        // Original value was timestamp in millis, returns a readable date string.
        $(this).text(parseMillis($(this).text()));

    })

    $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
        var target = $(e.target).attr("href") // activated tab
        console.log(target);
        if (target == '#messages') {
            var $chatWindow = $('#' + twilioChannel.uniqueName + '-chat-messages');
            $chatWindow.scrollTop($chatWindow[0].scrollHeight);
            console.lg('scrollTop');
        }
    });

    $('.delete-notification').click(function() {
        var id = $(this).parent().parent().attr('id');
        // ID is notification-row-{{pk}}
        var pk = id.split('-')[2];

        $.post('/delete-notification', "pk=" + pk, function() {
            console.log('posted');
            triggerToast('Notification removed.');
        })

        $(this).parent().parent().hide();
    });

});
