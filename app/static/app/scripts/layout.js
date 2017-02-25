

$(function() {
    $('#sync-redcap').click(function() {
        $.post('/sync-redcap', function() {
            console.log('synced with redcap');
        })

    })




})
