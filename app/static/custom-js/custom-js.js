document.getElementById("hunt").onmouseover = function() {mouseOver()};
document.getElementById("hunt").onmouseout = function() {mouseOut()};


function mouseOver() {
  document.getElementById("hunt").style.background = "black";
  document.getElementById("hunt").style.color = "#0e62c4";
}

function mouseOut() {
  document.getElementById("hunt").style.color = "whitesmoke";
  document.getElementById("hunt").style.background = "darkslategrey";
}

document.getElementById("search").onmouseover = function() {mouseOverSearch()};
document.getElementById("search").onmouseout = function() {mouseOutSearch()};
function mouseOverSearch() {
  document.getElementById("search").style.background = "black";
  document.getElementById("search").style.color = "#0e62c4";
}

function mouseOutSearch() {
  document.getElementById("search").style.color = "whitesmoke";
  document.getElementById("search").style.background = "darkslategrey";
}


document.getElementById("after").onmouseover = function() {mouseOverAfter()};
document.getElementById("after").onmouseout = function() {mouseOutAfter()};
function mouseOverAfter() {
  document.getElementById("after").style.background = "black";
  document.getElementById("after").style.color = "#0e62c4";
}

function mouseOutAfter() {
  document.getElementById("after").style.color = "whitesmoke";
  document.getElementById("after").style.background = "darkslategrey";
}


document.getElementById("before").onmouseover = function() {mouseOverBefore()};
document.getElementById("before").onmouseout = function() {mouseOutBefore()};
function mouseOverBefore() {
  document.getElementById("before").style.background = "black";
  document.getElementById("before").style.color = "#0e62c4";
}

function mouseOutBefore() {
  document.getElementById("before").style.color = "whitesmoke";
  document.getElementById("before").style.background = "darkslategrey";
}
