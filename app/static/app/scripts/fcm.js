

function sendFCM() {
    $.ajax
        ({
            type: "POST",
        url: "https://fcm.googleapis.com/fcm/send",
        dataType: 'json',
        async: false,
        headers: {
            "Authorization": "key=AAAAZ4czPsc:APA91bGapJWFGh7h97L7_TO9TV6UB9vqjeA1rMxATMwDTvleJr9hvn5cB9Dppz7y_Sa4mmYD6UfePK0FOriwphvyJmEM-_MJLwkkas21uFRZgflqbk_f367uqwcWyAQ6AThRDSe_275_"
        },
        data: {
            "to": "/topics/videos",
        "data": {
            "message": "This is push for video!"
        }
        },
        success: function (){
            alert('Sent message to topic "patient"'); 
        }
        });

}
