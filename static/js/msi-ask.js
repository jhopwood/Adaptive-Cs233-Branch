function drawMuxOrDec(ptype, level, signals) {
  var canvas = $('#mux-decoder').get(0).getContext('2d');
  canvas.font = 'Bold 20px Sans-Serif';
  // Now we do the actual loading.
  // 2-to-1 mux
  var imageObj = new Image();
  if (ptype == 'mux') {
    switch(level) {
      // 2 to 1 mux
      case 0: 
        imageObj.src = '/img/MSI2_1Mux.png';
        imageObj.onload = function() {
          canvas.drawImage(imageObj,50,50);
          var xPos = 35, selectPos = 165;
          canvas.fillText((signals.inputs[1]).toString(), xPos, 140);
          canvas.fillText((signals.inputs[0]).toString(), xPos, 235);
          canvas.fillText((signals.selects[0]).toString(), selectPos, 390);
        };
        break;
      // 4 to 1 mux
      case 1:
        imageObj.src = '/img/MSI4_1Mux.png';
        imageObj.onload = function() {
          var xPos = 35, originY = 75; 
          var selectX = 130, selectY = 395;
          canvas.drawImage(imageObj,50,40, imageObj.width * .9, imageObj.height * .9);
          canvas.fillText((signals.selects[1]).toString(), selectX, selectY);
          canvas.fillText((signals.selects[0]).toString(), selectX + 60, selectY - 10);
          canvas.fillText((signals.inputs[3]).toString(), xPos, originY);
          canvas.fillText((signals.inputs[2]).toString(), xPos, originY + 88);
          canvas.fillText((signals.inputs[1]).toString(), xPos, originY + 173);
          canvas.fillText((signals.inputs[0]).toString(), xPos, originY + 248);
        };
        break;
      case 2:
        imageObj.src = '/img/MSI8_1Mux.png';
        imageObj.onload = function() {
          var xPos = 70, originY = 50; 
          var selectX = 160, selectY = 380;
          canvas.drawImage(imageObj,80,10, imageObj.width, imageObj.height * .65);
          canvas.fillText((signals.selects[2]).toString(), selectX, selectY);
          canvas.fillText((signals.selects[1]).toString(), selectX + 40, selectY - 10);
          canvas.fillText((signals.selects[0]).toString(), selectX + 80, selectY - 20);
          canvas.fillText((signals.inputs[7]).toString(), xPos, originY);
          canvas.fillText((signals.inputs[6]).toString(), xPos, originY + 30);
          canvas.fillText((signals.inputs[5]).toString(), xPos, originY + 70);
          canvas.fillText((signals.inputs[4]).toString(), xPos, originY + 100);
          canvas.fillText((signals.inputs[3]).toString(), xPos, originY + 130);
          canvas.fillText((signals.inputs[2]).toString(), xPos, originY + 180);
          canvas.fillText((signals.inputs[1]).toString(), xPos - 5, originY + 215);
          canvas.fillText((signals.inputs[0]).toString(), xPos - 5, originY + 255);
        };
        break;
    }
  }
  
  if (ptype == 'dec') {
    switch(level) {
      case 0:
        imageObj.src = '/img/MSI1_2Decoder.png';
        imageObj.onload = function() {
          var xPos = 35;
          var selectxPos = 160;
          canvas.drawImage(imageObj,50,10);
          canvas.fillText((signals.selects[0]).toString(), selectxPos - 15, 265);
          canvas.fillText("1", xPos, 125);
        };
        break;
      // 2-to-4 decoder  
      case 1:
        imageObj.src = '/img/MSI2_4Decoder.png';
        imageObj.onload = function() {
          var xPos = 35;
          var selectxPos = 160;
          canvas.drawImage(imageObj,50,10);
          canvas.fillText((signals.selects[1]).toString(), selectxPos, 380);
          canvas.fillText((signals.selects[0]).toString(), selectxPos + 40, 395);
          canvas.fillText("1", xPos, 180);
        };
        break;
      // 3-to-8 decoder
      case 2:
        imageObj.src = '/img/MSI3_8Decoder.png';
        imageObj.onload = function() {
          var enPos = 35;
          var xPos = 120;
          canvas.drawImage(imageObj,50,30, imageObj.width * 0.6, imageObj.height * 0.6);
          canvas.fillText((signals.selects[2]).toString(), 120, 390);
          canvas.fillText((signals.selects[1]).toString(), 150, 390);
          canvas.fillText((signals.selects[0]).toString(), 184, 398);
          canvas.fillText("1", enPos, 195);
        };
      }
    }
  }

/*
 * Preload all the images we need for the decoder and 
 * mux examples so that the images are in the cache.
 */
function preloadImages() {
  var image = new Image();
  var images = new Array();
  images[0] = '/img/MSI2_1Mux.png';
  images[1] = '/img/MSI4_1Mux.png';
  images[2] = '/img/MSI8_1Mux.png';
  images[3] = '/img/MSI1_2Decoder.png';
  images[4] = '/img/MSI2_4Decoder.png';
  images[5] = '/img/MSI3_8Decoder.png';
  for (var i = 0; i < images.length; i++) {
    image.src = images[i];
  }
}