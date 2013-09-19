document.addEventListener('DOMContentLoaded',domloaded,false);
function domloaded(){
    var mbW=document.getElementById("myCanvas");
    var mbWx=mbW.getContext("2d");
    mbWx.moveTo(100,230);
    mbWx.lineTo(700,230);
    mbWx.stroke();

    var p1W=document.getElementById("myCanvas");
    var p1Wx=p1W.getContext("2d");
    p1Wx.moveTo(100,230);
    p1Wx.lineTo(100,155);
    p1Wx.stroke();

    var p2W=document.getElementById("myCanvas");
    var p2Wx=p2W.getContext("2d");
    p2Wx.moveTo(300,230);
    p2Wx.lineTo(300,155);
    p2Wx.stroke();

    var p3W=document.getElementById("myCanvas");
    var p3Wx=p3W.getContext("2d");
    p3Wx.moveTo(500,230);
    p3Wx.lineTo(500,155);
    p3Wx.stroke();

    var mmW=document.getElementById("myCanvas");
    var mmWx=mmW.getContext("2d");
    mmWx.strokeStyle="black";
    mmWx.moveTo(700,230);
    mmWx.lineTo(700,210);
    mmWx.stroke();

    var arc1=document.getElementById("myCanvas");
    var arc1tx=arc1.getContext("2d");
    arc1tx.strokeStyle="teal";
    arc1tx.beginPath();
    arc1tx.arc(100,55,50,Math.PI,2*Math.PI);
    arc1tx.stroke();

    var p1=document.getElementById("myCanvas");
    var p1x=p1.getContext("2d");
    p1x.font="12px Arial";
    p1x.fillText("Processor 1",65,35);

    var c1=document.getElementById("myCanvas");
    var c1x=c1.getContext("2d");
    c1x.font="11px Arial";
    c1x.fillText("Cache",83,65);

    var box1 = document.getElementById("myCanvas");
    var box1tx = box1.getContext("2d");
    box1tx.strokeStyle = "darkblue";
    box1tx.strokeRect(25,55,150,100);

    var arc2 = document.getElementById("myCanvas");
    var arc2tx = arc2.getContext("2d");
    arc2tx.strokeStyle="teal";
    arc2tx.beginPath();
    arc2tx.arc(300,55,50,Math.PI,2*Math.PI);
    arc2tx.stroke();

    var p2=document.getElementById("myCanvas");
    var p2x=p2.getContext("2d");
    p2x.font="12px Arial";
    p2x.fillText("Processor 2",265,35);
	
	var c2=document.getElementById("myCanvas");
    var c2x=c2.getContext("2d");
    c2x.font="11px Arial";
    c2x.fillText("Cache",283,65);

    var box2 = document.getElementById("myCanvas");
    var box2tx = box2.getContext("2d");
    box2tx.strokeStyle = "darkblue";
    box2tx.strokeRect(225,55,150,100);


    var arc3 = document.getElementById("myCanvas");
    var arc3tx = arc3.getContext("2d");
    arc3tx.strokeStyle="teal";
    arc3tx.beginPath();
    arc3tx.arc(500,55,50,Math.PI,2*Math.PI);
    arc3tx.stroke();

    var p3=document.getElementById("myCanvas");
    var p3x=p3.getContext("2d");
    p3x.font="12px Arial";
    p3x.fillText("Processor 3",465,35);

    var c3=document.getElementById("myCanvas");
    var c3x=c3.getContext("2d");
    c3x.font="11px Arial";
    c3x.fillText("Cache",483,65);
	
    var box3 = document.getElementById("myCanvas");
    var box3tx = box3.getContext("2d");
    box3tx.strokeStyle = "darkblue";
    box3tx.strokeRect(425,55,150,100);


    var mainbox = document.getElementById("myCanvas");
    var mainboxtx = mainbox.getContext("2d");
    mainboxtx.strokeStyle ="red";
    mainboxtx.strokeRect(625,10,150,200);

    var p4=document.getElementById("myCanvas");
    var p4x=p4.getContext("2d");
    p4x.font="15px Arial";
    p4x.fillText("Main Memory",660,25);
	

}