
$(function() {
    $('.patient-header').click(function() {
        var rightChevron = $(this).find('.glyphicon-chevron-right');
        var downChevron= $(this).find('.glyphicon-chevron-down');

        rightChevron.removeClass('glyphicon-chevron-right');
        rightChevron.addClass('glyphicon-chevron-down');

        downChevron.removeClass('glyphicon-chevron-down');
        downChevron.addClass('glyphicon-chevron-right');
    })

    $('.dashboard-alert').click(function() {
        // ID is esas-alert-{{pk}}
        var pk = $(this).attr('id').split('-')[2];
        console.log('pk');
        console.log(pk);

        $.post('/delete-dashboard-alert', "pk=" + pk, function() {
            console.log('posted');
        })


    })
})
