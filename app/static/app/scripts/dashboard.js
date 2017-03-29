
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
        var pk =$(this).attr('id');

        $.post('/delete-dashboard-alert', "pk=" + pk, function() {
            console.log('posted');
        })


    })
})
