/*
        data: JSON.stringify({
            'to' : '/topics/test',
            'data' : {
                  'action' : 'REQUEST',
                  'type' : 'ESAS'
            }
        }),
*/

function sendNotification(dataJSON) {
    console.log('firebase_cloud_messaging.js: sendNotification');

    // Authorization key taken from firebase console
    $.ajax({
        type: 'POST',
        url: 'https://fcm.googleapis.com/fcm/send',
        dataType: 'json',
        async: true, headers: {
            'Authorization': 'key=AAAAZ4czPsc:APA91bGapJWFGh7h97L7_TO9TV6UB9vqjeA1rMxATMwDTvleJr9hvn5cB9Dppz7y_Sa4mmYD6UfePK0FOriwphvyJmEM-_MJLwkkas21uFRZgflqbk_f367uqwcWyAQ6AThRDSe_275_',
            'Content-Type': 'application/json'
        },
        data: dataJSON,
        success: function (data) {
            console.log('returned data: ');
            console.log(data);
            //alert('Sent message to topic "test"'); 
        }
    });

}

function fcmNotification(patientUsername, action, category, text, primary_key) {
    console.log('fcmCreateNotification');

    console.log('patientUsername: ' + patientUsername);
    console.log('category: ' + category);
    console.log('text: ' + text);
    console.log('primary_key: ' + primary_key);

    let toast = true;
    var prettyCategory = '';
    if (category == 'PAIN') {
       prettyCategory = 'Pain' ;
    } else if (category == 'MEDICATION') {
       prettyCategory = 'Medication' ;
    } else if (category == 'ESAS') {
       prettyCategory = 'ESAS' ;
    } else if (category == 'MESSAGE') {
       prettyCategory = 'Message' ;
       toast = false;
    } else if (category == 'VIDEO') {
       prettyCategory = 'Video' ;
    }

    let toastText = prettyCategory + ' notification sent.';

    if (toast) {
        triggerToast(gettext(toastText), 'success');
    }


    if (category == 'MESSAGE') {
        var dataJSON = JSON.stringify({
            'to' : '/topics/test',
            'data' : {
                  'event' : 'NOTIFICATION',
                  'action': action,
                  'category': category,
                  'patient': patientUsername,
                  'sender': djangoUsername,
                  'text': text,
                  'pk': primary_key, 
            }
        });
    } else {
        var dataJSON = JSON.stringify({
            'to' : '/topics/test',
            'data' : {
                  'event' : 'NOTIFICATION',
                  'action': action,
                  'category': category,
                  'patient': patientUsername,
                  'text': text,
                  'pk': primary_key, 
            }
        });
    }

    console.log(dataJSON);
    sendNotification(dataJSON);
}

