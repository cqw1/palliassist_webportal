

$(function() {
    google.charts.load('current', {'packages':['line']});
    google.charts.setOnLoadCallback(drawChart);

    console.log('google charts load');

    var data;
    var options;
    var chart;
    var $chartDiv = $('#linechart_material');

    /*
     * Django variables passed in from patient_profile.html
     * django_username: Username of currently logged in user.
     * esasSurveys: Array of Objects. created in views.py patient_profile.
     * patientFullName: Full name of patient whose page we're on.
     * channels: List of channels the patient is in.
     * token: Twilio IPMessaging access token.
     */


    function initialize() {
        drawChart();
    }

    function drawChart() {
        data = new google.visualization.DataTable();

        var values = {"Date": []};
        var esasCount = 0;
        esasSurveys.forEach(function(esas) {

            var date = new Date(esas.created_date);

            // Always have date as first values.
            values["Date"].push(new Date(date.getYear(), date.getMonth(), date.getDate()))
            //values["Date (DD/MM)"].push(date.getDate() + '/' + (date.getMonth() + 1));

            esas.questions.forEach(function(question) {
                if (values.hasOwnProperty(question["question"])) {
                    // Array of answers for this question already exists. Just add.
                    values[question["question"]].push(question["answer"])
                } else {
                    // Haven't seen this question before. 
                    var new_answers = [];

                    for (var i = 0; i < esasCount; i++) {
                        // Account for past esas's that dont have an answer for 
                        // this new question.
                        new_answers.push(0);
                    }
                    new_answers.push(question["answer"]);
                    values[question["question"]] = new_answers;
                }
            });

            // Keep track of how many ESAS surveys we've seen.
            // Lets us know how many default answers we should insert when we 
            // see an esas with a question we haven't seen before. Should cover 
            // the case when doctors add in a new question that old esas 
            // surveys don't have a field for.
            esasCount += 1;
        });

        keys = Object.keys(values);
        keys.sort(); // Alphabetizes the keys/questions.

        data.addColumn('date', 'Date');

        keys.forEach(function(key) {
            if (key != 'Date') {
                data.addColumn('number', key.charAt(0).toUpperCase() + key.slice(1));
            }
        })

        // Reformat the answers into proper row format for the google chart.
        var rows = [];
        for (var i = 0; i < values[keys[0]].length; i++) {
            var new_row = [];
            for (var j = 0; j < keys.length; j++) {
                new_row.push(values[keys[j]][i]);
            }
            rows.push(new_row);
        }

        data.addRows(rows);



        options = {
            chart: {
                title: patientFullName + ' ESAS Responses',

            },
        };

        chart = new google.charts.Line(document.getElementById('linechart_material'));
        chart.draw(data, google.charts.Line.convertOptions(options));
    }

    // TODO: Google charts can't be drawn on hidden tabs.
    $('#esas-tab').click(function(e) {
        console.log('clicked #esas-tab');
    })

    /*
    var hidden = false;
    if ($chartDiv.parent().hasClass('active')) {
        chart.draw(data, google.charts.Line.convertOptions(options));
    } else {
        $chartDiv.show();
        chart.draw(data, google.charts.Line.convertOptions(options));
        hidden = true;
    }

    if (hidden) {
        $chartDiv.hide();
    }
    */

})
