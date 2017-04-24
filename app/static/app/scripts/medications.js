
function createMedication(patientPrimaryKey) {
    $.post('/create-medication', $("#create-medication-form").serialize() + "&pk=" + patientPrimaryKey, function() {
        console.log('posted');
        location.reload();
    })
}

$(function() {

    // Resets the radio option to be the ESAS survey category. Correspondingly updates the message text box.
    function resetCreateMedicationModal() {
        // id is auto-generated in CreateMedicationForm based on category field.
        $('#create-medication-form')[0].reset()
    }

    $('#create-medication-modal-btn').click(resetCreateMedicationModal);
    $('#close-create-medication-modal-btn').click(resetCreateMedicationModal);
    $('#x-create-medication-modal-btn').click(resetCreateMedicationModal);


    $('.delete-medication').click(function() {
        var id = $(this).parent().parent().attr('id');
        // ID is notification-row-{{pk}}
        var pk = id.split('-')[2];

        $.post('/delete-medication', "pk=" + pk, function() {
            console.log('posted');
            triggerToast('Medication removed.', 'success');
        })

        $(this).parent().parent().hide();
    });

})
