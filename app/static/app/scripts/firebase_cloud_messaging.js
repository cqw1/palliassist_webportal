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

function fcmRequestESAS(patientUsername, text) {
    console.log('fcmRequestESAS ' + text);

    var dataJSON = JSON.stringify({
        'to' : '/topics/test',
        'data' : {
              'action' : 'REQUEST',
              'type' : 'NOTIFICATION',
              'timestamp' : Date.now(),
              'patient': patientUsername,
              'data': {
                  'category': 'ESAS',
                  'text': text,
                  'done': 'N'
              }
        }
    });

    console.log(dataJSON);
    //sendNotification(dataJSON);
}

function fcmRemoveESAS(patientUsername, text) {
    console.log('fcmRequestESAS ' + text);

    var dataJSON = JSON.stringify({
        'to' : '/topics/test',
        'data' : {
              'action' : 'REQUEST',
              'type' : 'NOTIFICATION',
              'timestamp' : Date.now(),
              'patient': patientUsername,
              'data': {
                  'category': 'ESAS',
                  'text': text,
                  'done': 'N'
              }
        }
    });

    console.log(dataJSON);
    //sendNotification(dataJSON);
}

