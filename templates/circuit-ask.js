get_answer = function() {
  return circuit_expression;
}


top_str = 'var canvas = document.getElementById("solution");\
    var context = canvas.getContext("2d");\
    var gate_height = 50;\
    var gate_width = 60;\
    var AND = new Image();\
    AND.src = "/img/AND.png";\
    var OR = new Image();\
    OR.src = "/img/OR.png";\
    var NOT = new Image();\
    NOT.src = "/img/NOT.png";\
    var BUF = new Image();\
    BUF.src = "/img/BUF.png";';

bottom_str = 'context.font = "bold 1em sans-serif";\
    context.textAlign = "center";\
    draw_terminal_labels(context, draw_terminals);\
    context.fillText("out", cwidth-15, cheight/2-5);\
    context.fillText("Solution", cwidth-50, 20);';

function correct(json_rdata) {
    str = top_str + json_rdata["circuit"] + bottom_str;
    eval(str);
    $("#solution").toggleClass("no-display");
}

circuit_expression_fn = function(exp) {
    if ((exp.length === 0) || (exp.indexOf("-") !== -1) || (exp.indexOf("()") !== -1)) {
        $("#submit").removeClass('btn-primary').addClass('disabled');
    } else {
        $("#submit").removeClass('disabled').addClass('btn-primary');
    }
}

var num_terminals = {{terminals|length}};
$(document).ready(function() {	      
    circuit_init(); 
})


