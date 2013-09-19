
function Link(a, b) {
  this.nodeA = a;
  this.nodeB = b;
    // make anchor point relative to the locations of nodeA and nodeB
  this.parallelPart = 0.5; // percentage from nodeA to nodeB
  this.perpendicularPart = 0; // pixels from line between nodeA and nodeB
}

Link.prototype.getAnchorPoint = function() {
  var dx = this.nodeB.x - this.nodeA.x;
  var dy = this.nodeB.y - this.nodeA.y;
  var scale = Math.sqrt(dx * dx + dy * dy);
  return {
    'x': this.nodeA.x + dx * this.parallelPart - dy * this.perpendicularPart / scale,
    'y': this.nodeA.y + dy * this.parallelPart + dx * this.perpendicularPart / scale
  };
};

Link.prototype.setAnchorPoint = function(x, y) {
  var dx = this.nodeB.x - this.nodeA.x;
  var dy = this.nodeB.y - this.nodeA.y;
  var scale = Math.sqrt(dx * dx + dy * dy);
  this.parallelPart = (dx * (x - this.nodeA.x) + dy * (y - this.nodeA.y)) / (scale * scale);
  this.perpendicularPart = (dx * (y - this.nodeA.y) - dy * (x - this.nodeA.x)) / scale;
  // snap to a straight line
  if (this.parallelPart > 0 && this.parallelPart < 1 && Math.abs(this.perpendicularPart) < snapToPadding) {
    this.lineAngleAdjust = (this.perpendicularPart < 0) * Math.PI;
    this.perpendicularPart = 0;
  }
};

Link.prototype.getEndPointsAndCircle = function() {
  if (this.perpendicularPart == 0) {
    var midX = (this.nodeA.x + this.nodeB.x) / 2;
    var midY = (this.nodeA.y + this.nodeB.y) / 2;
    var start = this.nodeA.closestPointOnCircle(midX, midY);
    var end = this.nodeB.closestPointOnCircle(midX, midY);
    return {
      'hasCircle': false,
      'startX': start.x,
      'startY': start.y,
      'endX': end.x,
      'endY': end.y
    };
  }
  var anchor = this.getAnchorPoint();
  var isReversed = (this.perpendicularPart > 0);
  var reverseScale = isReversed ? 1 : -1;
  return {
    'hasCircle': true,
    'reverseScale': reverseScale,
    'isReversed': isReversed
  };
};

Link.prototype.draw = function(c) {
  var stuff = this.getEndPointsAndCircle();
  // draw arc
  if(stuff.startY < stuff.endY){
  c.beginPath();
  //draws circle in the middle of the line for output dependency
  if(($('#q_type').text())=='Label all output dependencies'){
	c.arc((stuff.startX+stuff.endX)/2, (stuff.startY+stuff.endY)/2, 6, 0, Math.PI*2);
  }
  //draws line for anti-dependence //need to fix line so the line stays orthogonal when line is drawn at angle 
  else if(($('#q_type').text())=='Label all anti-dependencies'){
	dx = Math.cos(Math.atan2(stuff.startY-stuff.endY,stuff.startX-stuff.endX));
	dy = Math.sin(Math.atan2(stuff.startY-stuff.endY,stuff.startX-stuff.endX));
	c.moveTo(((stuff.startX+stuff.endX)/2)-5*dx+5*dy, ((stuff.startY+stuff.endY)/2)-5*dy-5*dx);
    c.lineTo(((stuff.startX+stuff.endX)/2)-5*dx-5*dy, ((stuff.startY+stuff.endY)/2)-5*dy+5*dx);
  }
  
  if (stuff.hasCircle) {
    c.arc(stuff.circleX, stuff.circleY, stuff.circleRadius, stuff.startAngle, stuff.endAngle, stuff.isReversed);
	
  } else {
    c.moveTo(stuff.startX, stuff.startY);
    c.lineTo(stuff.endX, stuff.endY);
  }
  c.stroke();
  // draw the head of the arrow
  if (stuff.hasCircle) {
    drawArrow(c, stuff.endX, stuff.endY, stuff.endAngle - stuff.reverseScale * (Math.PI / 2));
	} 
	else {
    drawArrow(c, stuff.endX, stuff.endY, Math.atan2(stuff.endY - stuff.startY, stuff.endX - stuff.startX));
  }
  };
};

Link.prototype.containsPoint = function(x, y) {
  var stuff = this.getEndPointsAndCircle();
  if (stuff.hasCircle) {
    var dx = x - stuff.circleX;
    var dy = y - stuff.circleY;
    var distance = Math.sqrt(dx*dx + dy*dy) - stuff.circleRadius;
    if (Math.abs(distance) < hitTargetPadding) {
      var angle = Math.atan2(dy, dx);
      var startAngle = stuff.startAngle;
      var endAngle = stuff.endAngle;
      if (stuff.isReversed) {
        var temp = startAngle;
        startAngle = endAngle;
        endAngle = temp;
      }
      if (endAngle < startAngle) {
        endAngle += Math.PI * 2;
      }
      if (angle < startAngle) {
        angle += Math.PI * 2;
      } else if (angle > endAngle) {
        angle -= Math.PI * 2;
      }
      return (angle > startAngle && angle < endAngle);
    }
  } else {
    var dx = stuff.endX - stuff.startX;
    var dy = stuff.endY - stuff.startY;
    var length = Math.sqrt(dx*dx + dy*dy);
    var percent = (dx * (x - stuff.startX) + dy * (y - stuff.startY)) / (length * length);
    var distance = (dx * (y - stuff.startY) - dy * (x - stuff.startX)) / length;
    return (percent > 0 && percent < 1 && Math.abs(distance) < hitTargetPadding);
  }
  return false;
};

function Node(x, y, name,pos,pos2) {
  this.x = x;
  this.y = y;
  this.name=name;
  this.pos=pos;
  this.pos2=pos2;
  this.mouseOffsetX = 0;
  this.mouseOffsetY = 0;
}

Node.prototype.setMouseStart = function(x, y) {
  this.mouseOffsetX = this.x - x;
  this.mouseOffsetY = this.y - y;
};

Node.prototype.setAnchorPoint = function(x, y) {
  this.x = x + this.mouseOffsetX;
  this.y = y + this.mouseOffsetY;
};

Node.prototype.draw = function(c) {
  // draw the 
  
  c.beginPath();
  c.arc(this.x, this.y, nodeRadius, 0, 2 * Math.PI, false);
  c.stroke();
 

};

Node.prototype.closestPointOnCircle = function(x, y) {
  var dx = x - this.x;
  var dy = y - this.y;
  var scale = Math.sqrt(dx * dx + dy * dy);
  return {
    'x': this.x + dx * nodeRadius / scale,
    'y': this.y + dy * nodeRadius / scale
  };
};

Node.prototype.containsPoint = function(x, y) {
  return (x - this.x)*(x - this.x) + (y - this.y)*(y - this.y) < nodeRadius*nodeRadius;
};



function TemporaryLink(from, to) {
  this.from = from;
  this.to = to;
}

TemporaryLink.prototype.draw = function(c) {
  // draw the line
  
  c.beginPath();
  if( this.to.y > this.from.y){
  c.moveTo(this.to.x, this.to.y);
  c.lineTo(this.from.x, this.from.y);
  c.stroke();

  // draw the head of the arrow
  drawArrow(c, this.to.x, this.to.y, Math.atan2(this.to.y - this.from.y, this.to.x - this.from.x));
  };
};


function drawArrow(c, x, y, angle) {
  var dx = Math.cos(angle);
  var dy = Math.sin(angle);
  c.beginPath();
  c.moveTo(x, y);
  c.lineTo(x - 8 * dx + 5 * dy, y - 8 * dy - 5 * dx);
  c.lineTo(x - 8 * dx - 5 * dy, y - 8 * dy + 5 * dx);
  c.fill();
}

function canvasHasFocus() {
  return (document.activeElement || document.body) == document.body;
}

var caretTimer;
var caretVisible = true;

function resetCaret() {
  clearInterval(caretTimer);
  caretTimer = setInterval('caretVisible = !caretVisible; draw()', 500);
  caretVisible = true;
}

var canvas;
var nodeRadius = 10;
var nodes = [];
var links = [];

var cursorVisible = true;
var snapToPadding = 6; // pixels
var hitTargetPadding = 6; // pixels
var selectedObject = null; // either a Link or a Node
var currentLink = null; // a Link
var movingObject = false;
var originalClick;

function drawUsing(c) {
  c.clearRect(0, 0, canvas.width, canvas.height);
  c.save();
  c.translate(0.5, 0.5);

  // for (var i = 0; i < nodes.length; i++) { // this draws nodes for testing
    // c.lineWidth = 1;
    // c.fillStyle = c.strokeStyle = (nodes[i] == selectedObject) ? 'blue' : 'black';
    // nodes[i].draw(c);
  // }
  //this array stores the right answers
  ansl=[]; 
  //drawing the redrawing the right answer links red or green
  for (var i = 0; i < links.length; i++) {
		c.lineWidth = 1;
		c.fillStyle = c.strokeStyle = (links[i] == selectedObject) ? 'blue' : 'black'; 
		if($("#correct").text() != ''){	
			var a = $("#correct").text().split(',');
			c.fillStyle = c.strokeStyle ='red';
			if(i==0){
			for(z=0;z< a.length;z+=2){ansl.push(new Link(nodes[a[z]],nodes[a[z+1]]));}
			}
			for(var j=0; j< a.length; j+=2){
				if((links[i].nodeA.pos2 == a[j]) && (links[i].nodeB.pos2 == a[j+1])){
					for(x=0;x < ansl.length;x++){
						if ((links[i].nodeA.pos2==ansl[x].nodeA.pos2)&&(links[i].nodeB.pos2==ansl[x].nodeB.pos2)){
								ansl.splice(x,1);
						}
					}
					c.fillStyle = c.strokeStyle ='lightgreen';
				}
			}
		}
		links[i].draw(c);
		
	}
	//draws the right answers the user didnt get right
	for(m=0;m < ansl.length; m++){
			c.fillStyle = c.strokeStyle ='orange';
			ansl[m].draw(c);
		}
  if (currentLink != null) {
    c.lineWidth = 1;
    c.fillStyle = c.strokeStyle = 'black';
    currentLink.draw(c);
  }
  checkSubmit();
  c.restore();
} 
function draw() {
  drawUsing(canvas.getContext('2d'));
}

function selectObject(x, y) {
  for (var i = 0; i < nodes.length; i++) {
    if (nodes[i].containsPoint(x, y)) {
      return nodes[i];
    }
  }
  for (var i = 0; i < links.length; i++) {
    if (links[i].containsPoint(x, y)) {
      return links[i];
    }
  }
  return null;
}

function snapNode(node) {
  for (var i = 0; i < nodes.length; i++) {
    if (nodes[i] == node) continue;

    if (Math.abs(node.x - nodes[i].x) < snapToPadding) {
      node.x = nodes[i].x;
    }

    if (Math.abs(node.y - nodes[i].y) < snapToPadding) {
      node.y = nodes[i].y;
    }
  }
}

window.onload = function() {
  canvas = document.getElementById('canvas');
  var change = 10; 
  if( $('#question_type').text() == 'mips_datadependence'){
   nodeRadius = 13;
   change = 9.5;
  }
  
  //draws the initial nodes over the variables.
   var j = 20;
   var t = 28;
   var m =0;
	 for(var i =0; i < 7;i++){ // outer loop iterates through each question string
		var s = $(".test"+i).text();
			for(var k =0; k < s.length; k++){ // iterates through each char in each string
				if(s[k] == 'x' || s[k] =='y' || s[k] =='z' || s[k] == 't'|| s[k] =='m' || s[k] =='j' ){
					selectedObject = new Node(t, j, s[k],k,m); 
					m++;
					nodes.push(selectedObject);
				}
			t +=change;
			};
	t = 28;
	j +=70;
	resetCaret();
    draw();
	 };
		
  canvas.onmousedown = function(e) {
    var mouse = crossBrowserRelativeMousePos(e);
    selectedObject = selectObject(mouse.x, mouse.y);
    movingObject = false;
    originalClick = mouse;

    if (selectedObject != null) {
      if (selectedObject instanceof Node) {
        currentLink = new TemporaryLink(mouse, mouse);
      } else {
        movingObject = true;
        deltaMouseX = deltaMouseY = 0;
        if (selectedObject.setMouseStart) {
          selectedObject.setMouseStart(mouse.x, mouse.y);
        }
      }
      resetCaret();
    } else if (shift) {
      currentLink = new TemporaryLink(mouse, mouse);
    }

    draw();

    if (canvasHasFocus()) {
      // disable drag-and-drop only if the canvas is already focused
      return false;
    } else {
      // otherwise, let the browser switch the focus away from wherever it was
      resetCaret();
      return true;
    }
  };

  canvas.onmousemove = function(e) {
    var mouse = crossBrowserRelativeMousePos(e);

    if (currentLink != null) {
      var targetNode = selectObject(mouse.x, mouse.y);
      if (!(targetNode instanceof Node)) {
        targetNode = null;
      }

      if (selectedObject == null) {
                  currentLink = new TemporaryLink(originalClick, mouse);
              }
	  else {
        if (targetNode == selectedObject) {
          currentLink = new TemporaryLink(mouse, mouse);
        } else if (targetNode != null) {
          currentLink = new Link(selectedObject, targetNode);
        } else {
          currentLink = new TemporaryLink(selectedObject.closestPointOnCircle(mouse.x, mouse.y), mouse);
        }
      }
      draw();
    }

  };

  canvas.onmouseup = function(e) {
    movingObject = false;

    if (currentLink != null) {
      if (!(currentLink instanceof TemporaryLink)) {
        selectedObject = currentLink;
		for(var i=0;i<links.length;i++){
			if (links[i].nodeA == currentLink.nodeA && links[i].nodeB == currentLink.nodeB){
				links.splice(i, 1);
			}
		}
        links.push(currentLink);
        resetCaret();
      }
      currentLink = null;
      draw();
    }
  };
};

var shift = false;

document.onkeydown = function(e) {
  var key = crossBrowserKey(e);

  if (key == 16) {
    shift = true;
  } else if (!canvasHasFocus()) {
    // don't read keystrokes when other things have focus
    return true;
  } else if (selectedObject != null) {
    if (key == 8 && selectedObject.text) { // backspace key
      selectedObject.text = selectedObject.text.substr(0, selectedObject.text.length - 1);
      resetCaret();
      draw();
    } else if (key == 8 || key == 46) { // delete key
      for (var i = 0; i < links.length; i++) {
        if (links[i] == selectedObject || links[i].node == selectedObject || links[i].nodeA == selectedObject || links[i].nodeB == selectedObject) {
          links.splice(i--, 1);
        }
      }
      selectedObject = null;
      draw();
    }
  }

  // backspace is a shortcut for the back button, but do NOT want to change pages
  if (key == 8) return false;
};

document.onkeyup = function(e) {
  var key = crossBrowserKey(e);

  if (key == 16) {
    shift = false;
  }
};

document.onkeypress = function(e) {
  // don't read keystrokes when other things have focus
  var key = crossBrowserKey(e);
  if (!canvasHasFocus()) {
    // don't read keystrokes when other things have focus
    return true;
  } else if (key >= 0x20 && key <= 0x7E && !e.metaKey && !e.altKey && !e.ctrlKey && selectedObject != null && 'text' in selectedObject) {
    selectedObject.text += String.fromCharCode(key);
    resetCaret();
    draw();

    // don't let keys do their actions (like space scrolls down the page)
    return false;
  } else if (key == 8) {
    // backspace is a shortcut for the back button, but do NOT want to change pages
    return false;
  }
};

function crossBrowserKey(e) {
  e = e || window.event;
  return e.which || e.keyCode;
}

function crossBrowserElementPos(e) {
  e = e || window.event;
  var obj = e.target || e.srcElement;
  var x = 0, y = 0;
  while(obj.offsetParent) {
    x += obj.offsetLeft;
    y += obj.offsetTop;
    obj = obj.offsetParent;
  }
  return { 'x': x, 'y': y };
}

function crossBrowserMousePos(e) {
  e = e || window.event;
  return {
    'x': e.pageX || e.clientX + document.body.scrollLeft + document.documentElement.scrollLeft,
    'y': e.pageY || e.clientY + document.body.scrollTop + document.documentElement.scrollTop
  };
}

function crossBrowserRelativeMousePos(e) {
  var element = crossBrowserElementPos(e);
  var mouse = crossBrowserMousePos(e);
  return {
    'x': mouse.x - element.x,
    'y': mouse.y - element.y
  };
}



function fixed(number, digits) {
  return number.toFixed(digits).replace(/0+$/, '').replace(/\.$/, '');
}

