String.prototype.repeat = function(num)
{
    return new Array(num + 1).join(this);
}

function fillInBits(correct_answer, ptype, level) {
  var bits = correct_answer.toString(2);
  if (ptype == "dec") {
    switch(level) {
      case 0:
        bits = ("0".repeat(2) + bits).substr(-2);
        break;
      case 1:
        bits = ("0".repeat(4) + bits).substr(-4);
        break;
      case 2:
        bits = ("0".repeat(8) + bits).substr(-8);
        break;
    }
  }
  bits = bits.split("").reverse();
  $('.pcor').each(function() {
    var inputId = $(this).attr("data-output");
    var i = 0;
    if (ptype == "dec") {
      var i = parseInt(inputId.substring(1));
    }
    var bitVal = $("input[data-output='"+ inputId +"']").first().val();
    $(this).html(bits[i]);
    if (bitVal == bits[i]) {
      $(this).css('color', 'green');
    }
    else {
      $(this).css('color', 'red');
    }
  });  
}