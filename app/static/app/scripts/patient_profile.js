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
}

function handleTabLinks() {
    var hash = window.location.href.split("#")[1];
    if (hash !== undefined) {
        var hpieces = hash.split("/");
        for (var i=0;i<hpieces.length;i++) {
            var domelid = hpieces[i];
            var domitem = $('a[href=#' + domelid + '][data-toggle=tab]');
            if (domitem.length > 0) {
                if (i+1 == hpieces.length) {
                    // last piece
                    setTimeout(function() {
                      // Highly unclear why this code needs to be inside a timeout call.
                      // Possibly due to the fact that the first ?.tag('show') call needs
                      // to have it's animation finishing before the next call is being
                      // made.
                      domitem.tab('show');
                    },
                    // This magic timeout is based on trial and error. I bumped it
                    // partially to catch the visitor's attention.
                    1000);
                } else {
                    domitem.tab('show');
                }
            }
        }
    }
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

    $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
        var target = $(e.target).attr("href") // activated tab
        console.log(target);
        if (target == '#messages') {
            var $chatWindow = $('#' + twilioChannel.uniqueName + '-chat-messages');
            $chatWindow.scrollTop($chatWindow[0].scrollHeight);
            console.log('scrollTop');
        }
    });

    handleTabLinks();

});
