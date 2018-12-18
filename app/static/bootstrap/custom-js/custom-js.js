document.getElementById("hunt").onmouseover = function() {mouseOver()};
document.getElementById("hunt").onmouseout = function() {mouseOut()};




function mouseOver() {
  document.getElementById("hunt").style.background = "#683755";
  document.getElementById("hunt").style.color = "#818181";
}

function mouseOut() {
  document.getElementById("hunt").style.color = "#683755";
  document.getElementById("hunt").style.background = "#818181";
}

document.getElementById("search").onmouseover = function() {mouseOverSearch()};
document.getElementById("search").onmouseout = function() {mouseOutSearch()};
function mouseOverSearch() {
  document.getElementById("search").style.background = "#683755";
  document.getElementById("search").style.color = "#818181";
}

function mouseOutSearch() {
  document.getElementById("search").style.color = "#683755";
  document.getElementById("search").style.background = "#818181";
}


document.getElementById("after").onmouseover = function() {mouseOverAfter()};
document.getElementById("after").onmouseout = function() {mouseOutAfter()};
function mouseOverAfter() {
  document.getElementById("after").style.background = "#683755";
  document.getElementById("after").style.color = "#818181";
}

function mouseOutAfter() {
  document.getElementById("after").style.color = "#683755";
  document.getElementById("after").style.background = "#818181";
}


document.getElementById("before").onmouseover = function() {mouseOverBefore()};
document.getElementById("before").onmouseout = function() {mouseOutBefore()};
function mouseOverBefore() {
  document.getElementById("before").style.background = "#683755";
  document.getElementById("before").style.color = "#818181";
}

function mouseOutBefore() {
  document.getElementById("before").style.color = "#683755";
  document.getElementById("before").style.background = "#818181";
}
