
function parseMillis(millis) {
    /*
     * Takes a timestamp in milliseconds and returns it in
     * locale date format and "HH:mm"
     */
    var date = new Date(Number(millis));
    var hours;
    var minutes;

    // Want hours to be in hh format
    if (date.getHours() < 10) {
        hours = '0' + date.getHours();
    } else {
        hours = date.getHours();
    }

    // Want minutes to be in mm format
    if (date.getMinutes() < 10) {
        minutes = '0' + date.getMinutes();
    } else {
        minutes = date.getMinutes();
    }

    return date.toLocaleDateString() + ' ' + hours + ':' + minutes
}
