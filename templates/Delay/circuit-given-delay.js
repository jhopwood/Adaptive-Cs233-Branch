  var AND = new Image();
  AND.src = "/img/ANDD.png";
  var OR = new Image();
  OR.src = "/img/ORD.png";
  var NOT = new Image();
  NOT.src = "/img/NOTD.png";
  var NOR = new Image();
  NOR.src = "/img/NORD.png";
  var NAND = new Image();
  NAND.src = "/img/NANDD.png";
  var BUF = new Image();
  BUF.src = "/img/BUF.png";

  function draw_circuit() {	      
    var canvas = document.getElementById("workspace");
    var context = canvas.getContext("2d");
    var gate_height = 50;
    var gate_width = 60;

    {{ question.circuit }} 

    context.font = "bold 1em sans-serif";
    context.textAlign = "center";

    draw_terminal_labels(context, draw_terminals);
    context.fillText("out", cwidth-15, cheight/2-5);
  };

  $(document).ready(function() { 
      draw_circuit("workspace");    
      $("#exp").width(30);   
      validate_d($("#exp"));
      checkSubmit();
    });
  