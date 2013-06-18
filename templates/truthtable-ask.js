  get_answer = function() {
    var actives = "";
    $.each($(".btn.active"), function(index, value) { actives += value.id + " "; });
    return actives;
  }
  function correct(json_rdata) {
    var result_tt = json_rdata["result_tt"];
    for (var i = 0 ; i < result_tt.length ; i ++) {
        $("#btn"+i+result_tt[i]).addClass('btn-correct');
        $("#btn"+i+(1-result_tt[i])).addClass('btn-incorrect');
    }
  }
  function checkSubmit() {	
    var active = $(".btn.active").length;
    if (active === {{numrows}}) {
      $("#submit").removeClass('disabled').addClass('btn-primary');
    }
  }
  function timerCheck() {
    setTimeout(function () { checkSubmit(); }, 30);
  }      
