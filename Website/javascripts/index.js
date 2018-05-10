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
  var ranks = {};
  var sortedClasses = [];

  for (var classIndex = 0; classIndex < classes.length; classIndex++) {
    var newClass = classes[classIndex];
    var rank = inefficentSingleClassRank(newClass);
    if (rank == 0 || isNaN(rank)) {
      continue;
    }
    ranks[newClass["report_caesar_title"] + newClass["report_caesar_instructor"] + newClass["course_overall_rating_mean"] + newClass["report_term"]] = rank;

    var insertedClass = false;
    for (var sortedClassIndex = 0; sortedClassIndex < sortedClasses.length; sortedClassIndex++) {
      var sortedClass = sortedClasses[sortedClassIndex]
      var sortedClassRank = ranks[sortedClass["report_caesar_title"] + sortedClass["report_caesar_instructor"] + sortedClass["course_overall_rating_mean"] + sortedClass["report_term"]];
      if (rank > sortedClassRank) {
          sortedClasses.splice(sortedClassIndex, 0, newClass);
          insertedClass = true;
          break;
      }
    }

    if (!insertedClass) {
      sortedClasses.push(newClass);
    }
  }

  localStorage.setItem("ranked", JSON.stringify(sortedClasses));
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

  if (indiClass["course_overall_rating_mean"] == null) {
    return 0;
  }

  if (parseInt(indiClass["report_response_count"]) < document.querySelector('input[name="responsesNeeded"]').value) {
    return 0;
  }

  var rank = 0.0;

  if (overallRatingFactor == FactorEnum.positive) {
    rank += parseFloat(indiClass["course_overall_rating_mean"]);
  } else if (overallRatingFactor == FactorEnum.negative) {
    rank += (6 - parseFloat(indiClass["course_overall_rating_mean"]));
  }

  if (learningFactor == FactorEnum.positive) {
    rank += parseFloat(indiClass["course_learned_rating_mean"]);
  } else if (learningFactor == FactorEnum.negative) {
    rank += (6 - parseFloat(indiClass["course_learned_rating_mean"]));
  }

  if (challengingFactor == FactorEnum.positive) {
    rank += parseFloat(indiClass["course_challenging_rating_mean"]);
  } else if (challengingFactor == FactorEnum.negative) {
    rank += (6 - parseFloat(indiClass["course_challenging_rating_mean"]));
  }

  if (stimulatingFactor == FactorEnum.positive) {
    rank += parseFloat(indiClass["course_interest_rating_mean"]);
  } else if (stimulatingFactor == FactorEnum.negative) {
    rank += (6 - parseFloat(indiClass["course_interest_rating_mean"]));
  }

  if (professorFactor == FactorEnum.positive) {
    rank += parseFloat(indiClass["course_instruction_rating_mean"]);
  } else if (professorFactor == FactorEnum.negative) {
    rank += (6 - parseFloat(indiClass["course_instruction_rating_mean"]));
  }

  return rank;
}
