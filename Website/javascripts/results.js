var keyDown = false;

function loadData() {
  var data = JSON.parse(localStorage.getItem("ranked"));

  var results = 15;
  var firstFive = data.slice(0, results);
  var lastFive = data.slice(-results).reverse();

  var resultsLength = firstFive.length;

  var innerHTML = "";
  for (var resultsIndex = 0; resultsIndex < resultsLength; resultsIndex++) {
    var goodClass = firstFive[resultsIndex];
    var badClass = lastFive[resultsIndex];
    innerHTML += "<tr><td class='class-td-box'>" + resultDiv(goodClass) + "</td>"
    innerHTML += "<td class='class-td-box'>" + resultDiv(badClass) + "</td></tr>"
  }

  document.getElementById('results-body').innerHTML = innerHTML;

  document.onkeydown = function(event) {
    keyDown = event.metaKey == true;
  }
  document.onkeyup = function(event) {
    keyDown = false;
  }
}

function resultDiv(result) {
  var innerHTML = "<div class='class-box' style='cursor: pointer;' onclick=\"openURL('" + result["report_url"] + "');\"><h3>" + result["report_caesar_title"].split('|').join(",") + "</h3>";
  innerHTML += "<h4>" + result["report_caesar_instructor"] + " - " + result["report_term"] + "</h4>"

  innerHTML += "<table class='class-box-table'><thead><tr><th class='class-box-header'>" + result["course_overall_rating_mean"] + "</th><th class='class-box-header'>" + result["course_challenging_rating_mean"] + "</th><th class='class-box-header'>" + result["course_interest_rating_mean"] + "</th>"
  innerHTML += "<th class='class-box-header'>" + result["course_learned_rating_mean"] + "</th><th class='class-box-header'>" + result["course_instruction_rating_mean"] + "</th><th class='class-box-header'>" + result["report_response_count"] + "</th></th></thead>"

  innerHTML += "<tbody><tr><td class='class-box-data'>OVERALL</td><td class='class-box-data'>CHALLENGE</td><td class='class-box-data'>INTEREST</td><td class='class-box-data'>LEARNED</td><td class='class-box-data'>PROF</td><td class='class-box-data'>RESPONSES</td></tr></tbody></table>"

  return innerHTML + "</div"
}

function openURL(url) {
  if (keyDown) {
    var win = window.open(url, '_blank');
    win.focus();
  } else {
    window.location = url;
  }
}
