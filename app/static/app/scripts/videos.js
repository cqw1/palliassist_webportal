
function addVideo(patientPrimaryKey) {
    console.log('addVideo')
    $.post('/add-video', $("#add-video-form").serialize() + "&pk=" + patientPrimaryKey, function() {
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
