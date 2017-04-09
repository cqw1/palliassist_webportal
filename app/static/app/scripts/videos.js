
function addVideo(patientPrimaryKey, patientUsername) {
    console.log('addVideo')
    $.post('/add-video', $("#add-video-form").serialize() + "&pk=" + patientPrimaryKey, function() {
        fcmNotification(patientUsername, 'CREATE', 'VIDEO', $('#id_url').val(), '');

        console.log('posted');
        console.log(location);
        location.reload();
    })
}

function deleteVideo(pk, el) {
    console.log('addVideo')

    $.post('/delete-video', "pk=" + pk, function() {
        console.log('posted');
        triggerToast('Video removed.');
    })

    $(el).parent().hide();
}

$(function() {

})
