function get_answer() {
  return circuit_expression;
}

function correct(json_rdata) {
    $("#solution").toggleClass("no-display");
}

circuit_expression_fn = function(exp) {
    if ((exp.length === 0) || (exp.indexOf("-") !== -1) || (exp.indexOf("()") !== -1)) {
        $("#submit").removeClass('btn-primary').addClass('disabled');
    } else {
        $("#submit").removeClass('disabled').addClass('btn-primary');
    }
}

var num_terminals = {{question.terminals|length}};
var level = {{submit.level}};
var problem_type = "build";
var qtype = "{{ question.qtype }}";
var num_inputs = {{ question.num_inputs }};
var num_select = {{ question.num_select }};

$(document).ready(function() {
    circuit_init("workspace");
})
