# limit to the following terminals
function upperCase() {
  var x = document.getElementById("fname");
  var terminals =  document.getElementById("terminals").innerHTML;
  var out = ""
  for (var i = 0 ; i < x.value.length() ; i ++) {
    var c = x.value[i];
    if (terminals.indexOf(c) != -1) {
      out += c;
    }
  }
  x.value = out;
}