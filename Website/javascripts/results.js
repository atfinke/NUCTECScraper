var keyDown = false;

function loadData() {
  var data;

  if (location.hostname === "localhost" || location.hostname === "127.0.0.1" || location.hostname === "") {
    data = JSON.parse(window.localStorage.getItem("ranked-local"));
  } else {
    data = JSON.parse(window.localStorage.getItem("ranked"));
  }

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
  var innerHTML = "<div class='class-box' style='cursor: pointer;' onclick=\"openURL('" + result["url"] + "');\"><h3>" + result["shortName"].split('|').join(",") + "</h3>";
  innerHTML += "<h4>" + result["instructor"] + " - " + result["term"] + "</h4>"

  innerHTML += "<table class='class-box-table'><thead><tr><th class='class-box-header'>" + result["ratingCourse"] + "</th><th class='class-box-header'>" + result["ratingChallenging"] + "</th><th class='class-box-header'>" + result["ratingInterest"] + "</th>"
  innerHTML += "<th class='class-box-header'>" + result["ratingLearned"] + "</th><th class='class-box-header'>" + result["ratingInstruction"] + "</th><th class='class-box-header'>" + result["responded"] + "</th></th></thead>"

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
