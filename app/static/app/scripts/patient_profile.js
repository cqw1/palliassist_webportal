console.log("patient_profile.js");

function clearNotes() {
    console.log("called clearNotes");
    $("#id_notes").val('');
};

function saveNotes(patient_id) {
    console.log($("#notes-form").serialize()) + "&u_id=" + patient_id;
    $.post('/save-notes', $("#notes-form").serialize() + "&u_id=" + patient_id, function() {
        console.log('posted');

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

function updateNotes(notes) {
    console.log('updateNotes('+ decodeURIComponent(notes) + ')');
    $("#id_notes").val(decodeURIComponent(notes));
}

$(function() {

});
