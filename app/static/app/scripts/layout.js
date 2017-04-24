

$(function() {
    $('#sync-redcap').click(function() {
        triggerToast('Syncing...', 'warning');
        $.post('/sync-redcap', function() {
            console.log('synced with redcap');

            $('#pa-warning-toast').removeClass('in');

            triggerToast('Synced.', 'success');
        })
    })
})
