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

    /*
    $.getJSON('/save-notes', {
        content: $saveInput.val(),
        sender: username,
        channel: channelName,
        time_sent: $.now(),
        type: 'text'
    }, function(data) {})
    */
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

});
