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
            alert('Sent message to topic "test"'); 
        }
    });

}

function fcmCreateNotification(patientUsername, category, text, primary_key) {
    console.log('fcmCreateNotification');

    console.log('patientUsername: ' + patientUsername);
    console.log('category: ' + category);
    console.log('text: ' + text);
    console.log('primary_key: ' + primary_key);


    var dataJSON = JSON.stringify({
        'to' : '/topics/test',
        'data' : {
              'event' : 'NOTIFICATION',
              'category': category,
              'patient': patientUsername,
              'text': text,
              'pk': primary_key, // Check if we can change this to medication_pk
        }
    });

    console.log(dataJSON);
    sendNotification(dataJSON);
}

