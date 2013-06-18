  var AND = new Image();
  AND.src = "/img/AND.png";
  var OR = new Image();
  OR.src = "/img/OR.png";
  var NOT = new Image();
  NOT.src = "/img/NOT.png";
  var BUF = new Image();
  BUF.src = "/img/BUF.png";

  function draw_circuit() {	      
    var canvas = document.getElementById("workspace");
    var context = canvas.getContext("2d");
    var gate_height = 50;
    var gate_width = 60;

    {{ circuit }} 

    context.font = "bold 1em sans-serif";
    context.textAlign = "center";

    draw_terminal_labels(context, draw_terminals);
    context.fillText("out", cwidth-15, cheight/2-5);
  };

  $(document).ready(draw_circuit());
