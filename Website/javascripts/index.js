function updatedForm() {

  var FactorEnum = Object.freeze({
    "positive": 1,
    "negative": 2,
    "none": 3
  })

  var overallRatingFactor = document.querySelector('input[name="q1"]:checked').value;
  var learningFactor = document.querySelector('input[name="q2"]:checked').value;
  var challengingFactor = document.querySelector('input[name="q3"]:checked').value;
  var stimulatingFactor = document.querySelector('input[name="q4"]:checked').value;
  var professorFactor = document.querySelector('input[name="q5"]:checked').value;

  var factors = [];

  if (overallRatingFactor == FactorEnum.positive) {
    factors.push("[Overall Rating]");
  } else if (overallRatingFactor == FactorEnum.negative) {
    factors.push("[6 - (Overall Rating)]");
  }

  if (learningFactor == FactorEnum.positive) {
    factors.push("[Learning Rating]");
  } else if (learningFactor == FactorEnum.negative) {
    factors.push("[6 - (Learning Rating)]");
  }

  if (challengingFactor == FactorEnum.positive) {
    factors.push("[Challenge Rating]");
  } else if (challengingFactor == FactorEnum.negative) {
    factors.push("[6 - (Challenge Rating)]");
  }

  if (stimulatingFactor == FactorEnum.positive) {
    factors.push("[Stimulating Rating]");
  } else if (stimulatingFactor == FactorEnum.negative) {
    factors.push("[6 - (Stimulating Rating)]");
  }

  if (professorFactor == FactorEnum.positive) {
    factors.push("[Professor Rating]");
  } else if (professorFactor == FactorEnum.negative) {
    factors.push("[6 - (Professor Rating)]");
  }

  document.getElementById("forumla").innerText = "Rating = " + factors.join(" + ");
}


function rate() {

  // Yes there would be a more efficent way so we only
  // pass through the list once, but I don't care right now.

  // Thank you quora user whose name I forgot.
  var filesUploaded = document.getElementById("fileUpload").files;

  var keys = [];
  var classes = [];
  var loads = 0
  for (var i = 0; i < filesUploaded.length; i++) {
    if (typeof(FileReader) != "undefined") {
      var reader = new FileReader();
      reader.onload = function(e) {
        var rows = e.target.result.split("\n");

        for (var rowIndex = 0; rowIndex < rows.length; rowIndex++) {
          var columns = rows[rowIndex].split(",");

          var classInfo = {};
          for (var columnIndex = 0; columnIndex < columns.length; columnIndex++) {
            if (rowIndex == 0) {
              keys.push(columns[columnIndex])
            } else {
              var key = keys[columnIndex];
              classInfo[key] = columns[columnIndex];
            }
          }
          classes.push(classInfo);
        }

        loads += 1;
        if (loads == filesUploaded.length) {
          console.log("loaded");
            theMostInefficentSortingFunction(classes);
        }
      }
      reader.readAsText(filesUploaded[i]);
    } else {
      alert("This browser does not support HTML5.");
    }
  }


}
// I don't care enfough to make it better
function theMostInefficentSortingFunction(classes) {

  var ranked = [];
  var existingRanks = {};

  var classesLength = classes.length;
  for (var classIndex = 0; classIndex < classesLength; classIndex++) {
    var inserted = false;

    var r = inefficentSingleClassRank(classes[classIndex]);

    if (r == 0 || isNaN(r)) {
      continue;
    }
    var rankedLength = ranked.length;
    for (var rankIndex = 0; rankIndex < rankedLength; rankIndex++) {

      newItem = classes[classIndex];
      existingItem = ranked[rankIndex];
      existingRank = existingRanks[existingItem["shortName"] + existingItem["instructor"] + existingItem["ratingCourse"]]
      if (r > existingRank) {
        ranked.splice(rankIndex, 0, newItem);
        inserted = true;
        existingRanks[newItem["shortName"] + newItem["instructor"] + newItem["ratingCourse"]] = r;
        break;
      }

    }

    if (inserted == false) {
      ranked.push(classes[classIndex])
    }

  }
  
  if (location.hostname === "localhost" || location.hostname === "127.0.0.1" || location.hostname === "") {
    window.localStorage.setItem("ranked-local", JSON.stringify(ranked));
  } else {
    window.localStorage.setItem("ranked", JSON.stringify(ranked));
  }

  var win = window.open("./results.html", '_blank');
  win.focus();

}

function inefficentSingleClassRank(indiClass) {

  var FactorEnum = Object.freeze({
    "positive": 1,
    "negative": 2,
    "none": 3
  })

  var overallRatingFactor = document.querySelector('input[name="q1"]:checked').value;
  var learningFactor = document.querySelector('input[name="q2"]:checked').value;
  var challengingFactor = document.querySelector('input[name="q3"]:checked').value;
  var stimulatingFactor = document.querySelector('input[name="q4"]:checked').value;
  var professorFactor = document.querySelector('input[name="q5"]:checked').value;

  if (indiClass == null) {
    return 0;
  }

  if (indiClass["ratingCourse"] == null) {
    return 0;
  }

  if (parseInt(indiClass["responded"]) < document.querySelector('input[name="responsesNeeded"]').value) {
    return 0;
  }

  var rank = 0.0;

  if (overallRatingFactor == FactorEnum.positive) {
    rank += parseFloat(indiClass["ratingCourse"]);
  } else if (overallRatingFactor == FactorEnum.negative) {
    rank += (6 - parseFloat(indiClass["ratingCourse"]));
  }

  if (learningFactor == FactorEnum.positive) {
    rank += parseFloat(indiClass["ratingLearned"]);
  } else if (learningFactor == FactorEnum.negative) {
    rank += (6 - parseFloat(indiClass["ratingLearned"]));
  }

  if (challengingFactor == FactorEnum.positive) {
    rank += parseFloat(indiClass["ratingChallenging"]);
  } else if (challengingFactor == FactorEnum.negative) {
    rank += (6 - parseFloat(indiClass["ratingChallenging"]));
  }

  if (stimulatingFactor == FactorEnum.positive) {
    rank += parseFloat(indiClass["ratingInterest"]);
  } else if (stimulatingFactor == FactorEnum.negative) {
    rank += (6 - parseFloat(indiClass["ratingInterest"]));
  }

  if (professorFactor == FactorEnum.positive) {
    rank += parseFloat(indiClass["ratingInstruction"]);
  } else if (professorFactor == FactorEnum.negative) {
    rank += (6 - parseFloat(indiClass["ratingInstruction"]));
  }

  return rank;
}
