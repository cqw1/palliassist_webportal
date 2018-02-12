var MAX_NUM_DOSES = 6; // Grabbed from the CreateMedicationForm.

function ToggleDoseTimes() {

    // Get the user-selected number of dosages.
    var numDoses = parseInt(document.getElementById('id_num_doses').options[document.getElementById('id_num_doses').selectedIndex].value);

    // Show all the dosage times that are less than the num dosages selected
    for (var show = 1; show <= numDoses; show++) {
        document.getElementById('id_dose_time_' + show).parentNode.parentNode.style.display = '';
    }
    
    // Hide all the dosage times that are greater than the num dosages selected
    for (var hide = numDoses + 1; hide <= MAX_NUM_DOSES; hide++) {
         document.getElementById('id_dose_time_' + hide).parentNode.parentNode.style.display = 'none';
    }
}

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

        // Hide all the dosage times except 1, the default choice
        for (var hide = 2; hide <= MAX_NUM_DOSES; hide++) {
             document.getElementById('id_dose_time_' + hide).parentNode.parentNode.style.display = 'none';
        }
    }

    $('#create-medication-modal-btn').click(resetCreateMedicationModal);
    $('#close-create-medication-modal-btn').click(resetCreateMedicationModal);
    $('#x-create-medication-modal-btn').click(resetCreateMedicationModal);


    $('.delete-medication').click(function() {
        var id = $(this).parent().parent().parent().attr('id');
        // ID is notification-row-{{pk}}
        var pk = id.split('-')[2];

        triggerToast('Medication removed.', 'success');
        /*
        $.post('/delete-medication', "pk=" + pk, function() {
            console.log('posted');
            triggerToast('Medication removed.', 'success');
        })
        */

        $(this).parent().parent().parent().hide();
    });

    document.getElementById('id_num_doses').onchange = ToggleDoseTimes;

})
