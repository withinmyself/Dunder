document.getElementById("hunt").onmouseover = function() {mouseOver()};
document.getElementById("hunt").onmouseout = function() {mouseOut()};


function mouseOver() {
  document.getElementById("hunt").style.background = "darkred";
  document.getElementById("hunt").style.color = "darkslategrey";
}

function mouseOut() {
  document.getElementById("hunt").style.color = "darkred";
  document.getElementById("hunt").style.background = "darkslategrey";
}

document.getElementById("search").onmouseover = function() {mouseOverSearch()};
document.getElementById("search").onmouseout = function() {mouseOutSearch()};
function mouseOverSearch() {
  document.getElementById("search").style.background = "darkred";
  document.getElementById("search").style.color = "darkslategrey";
}

function mouseOutSearch() {
  document.getElementById("search").style.color = "darkred";
  document.getElementById("search").style.background = "darkslategrey";
}


document.getElementById("after").onmouseover = function() {mouseOverAfter()};
document.getElementById("after").onmouseout = function() {mouseOutAfter()};
function mouseOverAfter() {
  document.getElementById("after").style.background = "darkred";
  document.getElementById("after").style.color = "darkslategrey";
}

function mouseOutAfter() {
  document.getElementById("after").style.color = "darkred";
  document.getElementById("after").style.background = "darkslategrey";
}


document.getElementById("before").onmouseover = function() {mouseOverBefore()};
document.getElementById("before").onmouseout = function() {mouseOutBefore()};
function mouseOverBefore() {
  document.getElementById("before").style.background = "darkred";
  document.getElementById("before").style.color = "darkslategrey";
}

function mouseOutBefore() {
  document.getElementById("before").style.color = "darkred";
  document.getElementById("before").style.background = "darkslategrey";
}
