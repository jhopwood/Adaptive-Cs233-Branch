// this function limits text entry for expressions to using specified list
// of characters (held in the element with ID "terminals".  Also this code
// enables a submission button only when the "expression" box is not empty

function limitChars(event) {
    var x = document.getElementById("expression");
    var terminals =  document.getElementById("terminals").innerHTML;
    var out = "", i; 
    for (i = 0 ; i < x.value.length ; i += 1) {
        var c = x.value[i];
        if (terminals.indexOf(c) !== -1) {
            out += c;
        }
    }
    x.value = out;
    checkSubmit(out.length > 0);
    submitOnEnter(event);
};

function submitOnEnter(event) {
   if (event.keyCode == 13) {
       $("#submit").click();
   }
}

function checkSubmit(safetosubmit) {
   if ((arguments.length === 0) ? canSubmit() : safetosubmit) {
       $("#submit").removeClass('disabled').addClass('btn-primary').removeAttr('disabled');
   } else {
       $("#submit").removeClass('btn-primary').addClass('disabled').prop("disabled", true);
   }
}

function timerCheck() {
   setTimeout(function () { checkSubmit(); }, 30);
}      

function characterLimit(e) {
  var chrTyped, chrCode=0, evt=e?e:event;
  if (evt.charCode!=null)     chrCode = evt.charCode;
  else if (evt.which!=null)   chrCode = evt.which;
  else if (evt.keyCode!=null) chrCode = evt.keyCode;

  if (chrCode==0) return true;
  else chrTyped = String.fromCharCode(chrCode);

  // expected characters, special keys & backspace [\b] work as usual:
  if ($('#terminals').text().indexOf(String.fromCharCode(chrCode)) !== -1) return true;
  if (chrTyped.match(/[\b]/)) return true;
  if (evt.altKey || evt.ctrlKey || chrCode<28) return true;

  // Any other input? Prevent the default response:
  if (evt.preventDefault) evt.preventDefault();
  evt.returnValue=false;
  return false;
}

$(document).ready(function() {	      
  $('#expression').keypress(
    function(e) {
       submitOnEnter(e);
       setTimeout(function () { 
         var x = document.getElementById("expression");
         checkSubmit(x.value.length > 0);
       }, 30);
       var b = characterLimit(e);
       return b;     
    }
  );
  $("#submit").click(function () {
    if ($("#submit").hasClass("disabled")) { return; }
    var answer = get_answer();
    $.post(submission_url(), {answer: answer}, 
    function(rdata) {
      json_rdata = JSON.parse(rdata)
      $("#submit").html("Try Another?");
      $("#submit").unbind('click');
      $("#submit").click(function() {
        // Reload the page
        window.location.reload();
      });

      if (json_rdata["score"] > parseFloat($("#best_score").html())) {
        $("#best_score").html("" + json_rdata["score"] + "%");
      }
      $("#score").html("Score: " + ((json_rdata["score"] === 100.0) ? '<span style="color:lime">100%</span>' : '<span style="color:red">' + json_rdata["score"] + '%</span>'));
      if (json_rdata["score"] === 100.0) {
        $("#complete").attr("src","/img/complete.png");
      }
      correct(json_rdata);
    });
  });
});

function draw_circle(context, x, y, radius) {
  context.lineWidth = 1;
  context.fillStyle = "black";  
  context.beginPath();
  context.arc(x, y, radius, 0, Math.PI*2, true);
  context.closePath();
  context.stroke();
  context.fill();
}

function draw_line(context, from_x, from_y, to_x, to_y) {
  context.strokeStyle = 'black';
  context.lineWidth = 2;
  context.beginPath();
  context.moveTo(from_x, from_y); 
	context.lineTo(to_x, to_y); 
  context.stroke();
}

function draw_terminal_labels(context, terminals) {
  if (terminals & 1) {
     context.fillText("x", 7, 15);
  }
  if (terminals & 2) {
     context.fillText("y", 7, 35);
  }
  if (terminals & 4) {
     context.fillText("z", 7, 55);
  }
}

