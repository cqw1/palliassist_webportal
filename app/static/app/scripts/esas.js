
$(function() {
    //google.charts.load('current', {'packages':['line']});
    //google.charts.setOnLoadCallback(drawChart);

    var datesX = [];
    var painY = [];
    var fatigueY = [];
    var nauseaY = [];
    var depressionY = [];
    var anxietyY = [];
    var drowsinessY = [];
    var appetiteY = [];
    var wellBeingY = [];
    var lackOfAirY = [];
    var insomniaY = [];

    esasJSON.forEach(function(esas) {
        datesX.push(new Date(Number(esas.fields.created_date)));

        painY.push(esas.fields.pain)
        fatigueY.push(esas.fields.fatigue)
        nauseaY.push(esas.fields.nausea)
        depressionY.push(esas.fields.depression)
        anxietyY.push(esas.fields.anxiety)
        drowsinessY.push(esas.fields.drowsiness)
        appetiteY.push(esas.fields.appetite)
        wellBeingY.push(esas.fields.well_being)
        lackOfAirY.push(esas.fields.lack_of_air)
        insomniaY.push(esas.fields.insomnia)

    });

    var painData = {
      x: datesX,
      y: painY,
      type: 'lines+markers',
      name: 'Pain'
    };

    var fatigueData = {
      x: datesX,
      y: fatigueY,
      type: 'lines+markers',
      name: 'Fatigue'
    };

    var nauseaData = {
      x: datesX,
      y: nauseaY,
      type: 'lines+markers',
      name: 'Nausea'
    };

    var depressionData = {
      x: datesX,
      y: depressionY,
      type: 'lines+markers',
      name: 'Depression'
    };

    var anxietyData = {
      x: datesX,
      y: anxietyY,
      type: 'lines+markers',
      name: 'Anxiety'
    };

    var drowsinessData = {
      x: datesX,
      y: drowsinessY,
      type: 'lines+markers',
      name: 'Depression'
    };

    var appetiteData = {
      x: datesX,
      y: appetiteY,
      type: 'lines+markers',
      name: 'Appetite'
    };

    var wellBeingData = {
      x: datesX,
      y: wellBeingY,
      type: 'lines+markers',
      name: 'Well-Being'
    };

    var lackOfAirData = {
      x: datesX,
      y: lackOfAirY,
      type: 'lines+markers',
      name: 'Lack of Air'
    };

    var insomniaData = {
      x: datesX,
      y: insomniaY,
      type: 'lines+markers',
      name: 'Insomnia'
    };

    var data = [painData, fatigueData, nauseaData, depressionData, anxietyData, drowsinessData, appetiteData, wellBeingData, lackOfAirData, insomniaData];
    
    var layout = {
        title: patientFullName + ' ESAS Responses',
        xaxis: {
            title: 'Date'
        },
        yaxis: {
            title: 'Intensity'
        }
    }
    Plotly.newPlot('esas-chart', data, layout, {displayModeBar: false});

    console.log('google charts load');

    var data;
    var options;
    var chart;
    var $chartDiv = $('#esas-chart');

    /*
     * Django variables passed in from patient_profile.html
     * django_username: Username of currently logged in user.
     * esasJSON: String of json-serialized esas objects.
     * patientFullName: Full name of patient whose page we're on.
     * channels: List of channels the patient is in.
     * token: Twilio IPMessaging access token.
     */

    $('.esas-standard-field').find('.esas-answer').each(function(index) {
        var value = Number($(this).text());

        if (value < 3) {
            $(this).parent().addClass('success');
        } else if (value < 8) {
            $(this).parent().addClass('warning');
        } else {
            $(this).parent().addClass('danger');
        }
    })

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

        chart = new google.charts.Line(document.getElementById('esas-chart'));
        chart.draw(data, google.charts.Line.convertOptions(options));
    }
})
