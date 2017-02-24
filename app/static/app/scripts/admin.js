
        //url: "https://d3f63e9d.ngrok.io/fcm",
function sendESAS() {
    $.ajax({
        url: "/fcm",
        type: "POST",
        data: { 
            event: 'COMPLETED',
            timestamp: Number($('#timestamp').val()),
            patient: $('#patient').val(),
            category: 'ESAS',
            data: JSON.stringify({
                pain: $('#pain').val(), 
                fatigue: $('#fatigue').val(), 
                nausea: $('#nausea').val(), 
                depression: $('#depression').val(), 
                anxiety: $('#anxiety').val(), 
                drowsiness: $('#drowsiness').val(), 
                appetite: $('#appetite').val(), 
                well_being: $('#well_being').val(), 
                lack_of_air: $('#lack_of_air').val(), 
                insomnia: $('#insomnia').val(), 

                fever: $('#fever').val(), 

                constipated: $('#constipated').val(), 
                constipated_days: $('#constipated_days').val(), 
                constipated_bothered: $('#constipated_bothered').val(), 

                vomiting: $('#vomiting').val(), 
                vomiting_count: $('#vomiting_count').val(), 

                confused: $('#confused').val(), 
            })
        },
        dataType: "json",
        success: function (result) {
            console.log('result');
            console.log(result);
        },
        error: function (xhr, ajaxOptions, thrownError) {
            alert(xhr.status);
            alert(thrownError);
        }
    });
}

$(function() {
    console.log('admin.js');




    /*
    $.ajax({
        url: "https://d3f63e9d.ngrok.io/fcm",
        type: "POST",
        data: { 
            apiKey: "23462", 
            method: "example", 
            ip: "208.74.35.5" 
        },
        dataType: "json",
        success: function (result) {
            console.log('result');
            console.log(result);
        },
        error: function (xhr, ajaxOptions, thrownError) {
            alert(xhr.status);
            alert(thrownError);
        }
    });
    */

})
