

function sendNotification() {
    console.log('firebase_cloud_messaging.js: sendNotification');

    // Authorization key taken from firebase console
    $.ajax({
            type: "POST",
            url: "https://fcm.googleapis.com/fcm/send",
            dataType: 'json',
            async: true,
            headers: {
                "Authorization": "key=AAAAZ4czPsc:APA91bGapJWFGh7h97L7_TO9TV6UB9vqjeA1rMxATMwDTvleJr9hvn5cB9Dppz7y_Sa4mmYD6UfePK0FOriwphvyJmEM-_MJLwkkas21uFRZgflqbk_f367uqwcWyAQ6AThRDSe_275_"
        },
        data: {
            "to" : "/topics/test",
            "notification" : {
                  "body" : "Hello World!",
                  "title" : "PalliAssist",
                  "icon" : ""
            }
        },
        success: function (){
            alert('Sent message to topic "test"'); 
        }
    });

}
