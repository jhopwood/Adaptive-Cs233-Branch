function drag(elementToDrag, event) {
    // The initial mouse position, converted to document coordinates
    var clickX = event.clientX;
    var clickY = event.clientY;
    var baseX = elementToDrag.x;
    var baseY = elementToDrag.y;

    // Register the event handlers that will respond to the mousemove events
    // and the mouseup event that follow this mousedown event.
    document.addEventListener("mousemove", moveHandler, true);
    document.addEventListener("mouseup", upHandler, true);

    // We've handled this event. Don't let anybody else see it.
    event.stopPropagation();  

    // Now prevent any default action.
    event.preventDefault();   

    /**
     * This is the handler that captures mousemove events when an element
     * is being dragged. It is responsible for moving the element.
     **/
    function moveHandler(e) {
        // Move the element to the current mouse position, adjusted by the
        // position of the scrollbars and the offset of the initial click.
        newX = (baseX + (e.clientX - clickX));
        newY = (baseY + (e.clientY - clickY));
        elementToDrag.setXY(newX, newY);
	workspace.draw();

        // And don't let anyone else see this event.
        e.stopPropagation();  
    }

    /**
     * This is the handler that captures the final mouseup event that
     * occurs at the end of a drag.
     **/
    function upHandler(e) {
        elementToDrag.release();
	workspace.draw();

        // Unregister the capturing event handlers.
        document.removeEventListener("mouseup", upHandler, true);
        document.removeEventListener("mousemove", moveHandler, true);

        // And don't let the event propagate any further.
        e.stopPropagation();  
    }
}

var circuit_expression = "";

function relMouseCoords(event){
    "use strict";
    var totalOffsetX = 0, totalOffsetY = 0, canvasX = 0, canvasY = 0,
        currentElement = this;

    do {
        totalOffsetX += currentElement.offsetLeft;
        totalOffsetY += currentElement.offsetTop;
    } while ((currentElement = currentElement.offsetParent) !== null);

    canvasX = event.pageX - totalOffsetX;
    canvasY = event.pageY - totalOffsetY;

    return {x:canvasX, y:canvasY};
}
HTMLCanvasElement.prototype.relMouseCoords = relMouseCoords;

var workspace;

function Wire(parent, x, y) {
    this.parent = parent;
    this.x = x;
    this.y = y;
    this.dest = null;

    this.value = function () { return this.parent.value(); }
    this.exp = function () { return this.parent.exp(); }

    this.setXY = function (x, y) {
        this.x = x;
        this.y = y;
    }

    this.draw = function (context) {    
        var srcX = this.parent.x + this.parent.parent.x;
        this.x = Math.max(this.x, srcX);   // wires can't go to the left

        context.strokeStyle = 'black';
        context.lineWidth   = 2;
        context.beginPath();
        context.moveTo(srcX, this.parent.y + this.parent.parent.y); 
        if (this.dest) {
            context.lineTo(this.dest.x + this.dest.parent.x, 
                           this.dest.y + this.dest.parent.y); 
        } else {
            context.lineTo(this.x, this.y);
        }
        context.stroke();
    };

    this.disconnectAndDrag = function (e, x, y) {
        this.disconnectDest();
        this.x = x;
        this.y = y;
        drag(this, e);
    }

    this.disconnectDest = function () {
        if (this.dest !== null) {
            // destination nodes should only have 1 pointer
            this.dest.wires.splice(0, this.dest.wires.length);
            this.dest = null;
        }
    }

    this.disconnectBoth = function () {
        var idx = this.parent.wires.indexOf(this); // Find the index
        if (idx != -1) {
            this.parent.wires.splice(idx, 1); // Remove it if really found!
        }
        this.parent = null;
        this.disconnectDest();
    }

    this.release = function () {
        this.dest = workspace.wireRelease(this.x, this.y);

	if (this.dest === null) {
            this.disconnectBoth();
        } else {
            this.dest.wires.push(this);
	}
    };
}

function Workspace(canvas) {
    this.canvas = canvas;
    this.children = new Array();
    this.x = this.y = 0;

    this.compute = function (A, B, C) {
        this.inputs["x"].value = function () { return A; }
        this.inputs["y"].value = function () { return B; }
	if ("z" in inputs) {
	        this.inputs["z"].value = function () { return C; }	
        }

        if (this.output.connected()) {
            return this.output.wires[0].value();
        }
        return "z";
    }

    this.compute_exp = function () {
        if (!this.output.connected()) {
	    return "-";
        }
	return this.output.wires[0].exp();
    }

    this.computeAll = function () {
        circuit_expression = this.compute_exp();
	circuit_expression_fn(circuit_expression);

//        var td, td_desired;
//        for (var i = 0 ; i < 8 ; i ++) {
//            td = document.getElementById("current"+i);
//	    var current = this.compute((i>>2) & 1, (i>>1) & 1, (i>>0) & 1);
//            td.innerHTML = current;
//	    td_desired = document.getElementById("desired"+i);
//	    if (td_desired.innerHTML !== current) {
//                td.className -= "correct";
//                td.className += "wrong";
//            } else {
//                td.className -= "wrong";
//                td.className += "correct";
//            }
//        }
    }

    this.draw = function () {
        var context = this.canvas.getContext("2d");
        context.fillStyle = "white";
        context.fillRect(0, 0, this.canvas.width, this.canvas.height);
	
        context.font = "bold 1em sans-serif";
        context.fillStyle = "black";
        context.textAlign = "right";
        context.fillText("output", this.canvas.width - 5, this.canvas.height/2-10);
        this.output.draw(context, 0, 0);
        context.textAlign = "center";
        for (label in this.inputs) {
            context.fillText(label, 5, this.inputs[label].y-10);
            this.inputs[label].draw(context, 0, 0);
        }

        for (var i = 0 ; i < this.children.length ; i ++) {
            this.children[i].draw();
        }
        this.computeAll();
    }

    this.click = function (e, x, y) {
        for (var i = this.children.length - 1 ; i >= this.factories.length ; i --) {
            if (this.children[i].contains(x, y)) {
                if (!this.children[i].contains_connection(e, x, y)) {
                    drag(this.children[i], e);
                }
                return;
            }
        }
        for (var i = 0 ; i < this.factories.length ; i ++) {
            if (this.children[i].contains(x, y)) {
                var gate = new this.factories[i](this, (i+.5)*canvas.width/3-40, 5);
                drag(gate, e);
                return;
            }
        }
        if (this.output.contains(x, y)) {
            this.output.wires[0].disconnectAndDrag(e, x, y);
            return;	    
        } 
        for (label in this.inputs) {
            if (this.inputs[label].contains(x, y)) {
                this.inputs[label].makeWire(e, x, y);
                return;	    
            } 
        }
    }

    this.wireRelease = function (x, y) {
        for (var i = this.children.length - 1 ; i >= this.factories.length ; i --) {
            var gateX = x - this.children[i].x, gateY = y - this.children[i].y; 
            for (var j = 0 ; j < this.children[i].inputs.length ; j ++) {
                var connection = this.children[i].inputs[j];
                if (connection.contains(gateX, gateY) && 
                    !connection.connected()) {
                        return connection;
                }
            }
        }
        if (this.output.contains(x, y) && !this.output.connected()) {
            return this.output;	    
        }
        return null;
    };

    this.factories = [And, Or, Not];
    for (var i = 0 ; i < this.factories.length ; i ++) {
    	new this.factories[i](this, (i+.5)*canvas.width/3-40, 5);
    }
    this.inputs = {"x": new Connection(5, 110, 1, this), 
                   "y": new Connection(5, 190, 1, this),};
    if (num_terminals === 3) {   
        this.inputs["z"] = new Connection(5, 270, 1, this);
    }
    for (label in this.inputs) {
        this.inputs[label].exp_value = label; 
        this.inputs[label].exp = function () { return this.exp_value; }
    }

    this.output = new Connection(canvas.width - 5, canvas.height/2, 0, this);
    this.draw();
}

function Connection(x, y, source, parent) {
    this.x = x;   
    this.y = y;
    this.parent = parent;
    this.source = source;
    this.wires = new Array();

    this.value = function () { return this.parent.value(); }
    this.exp =   function () { return this.parent.exp(); }

    this.connected = function () { return (this.wires.length != 0); }

    this.contains = function (x, y) {
        return (Math.pow(x-this.x, 2) + Math.pow(y-this.y, 2)) < 100;
    }

    this.makeWire = function (e, x, y) {
        var wire = new Wire(this, x, y);
        this.wires.push(wire);
        drag(wire, e);
    }

    this.draw = function (context, x, y) {
        context.lineWidth   = 1;
        context.strokeStyle = "black";
        if ((this.source == 0)) {
            context.beginPath();
            context.arc(x + this.x, y + this.y, 5, 0, Math.PI*2, true);
            context.closePath();
            context.stroke();
        }
        if ((this.source == 1) || this.connected()) {
            context.fillStyle = "black";
            context.beginPath();
            context.arc(x + this.x, y + this.y, 3, 0, Math.PI*2, true);
            context.closePath();
            context.stroke();
            context.fill();
            for (var i = 0 ; i < this.wires.length ; i ++) {
                this.wires[i].draw(context);
            }
        }
    };
}

function Gate() {
    this.initGate = function (workspace, x, y, num_inputs) {
        this.workspace = workspace;
        workspace.children.push(this);
        this.canvas = workspace.canvas;
        this.width = 60; // 90;
        this.height = 50; // 75;
        this.x = x;
        this.y = y;
        this.text = "";
	
        this.output = new Connection(.95*this.width, this.height/2, 1, this);
        this.inputs = new Array();
        for (var i = 0 ; i < num_inputs ; i ++) {
            this.inputs.push(new Connection(5, (i+1)*(this.height/(num_inputs+1)), 0, this));
        }
    };

    this.contains = function (x, y) {
        var slop = 20;
        return ((x >= (this.x - slop)) && (y >= (this.y - slop)) && 
	       (x <= (this.x + this.width + slop)) && (y <= (this.y + this.height + slop)));
    };

    this.contains_connection = function (e, x, y) {
        if (this.output.contains(x - this.x, y - this.y)) {
            this.output.makeWire(e, x, y);
            return true;
        }
        for (var i = 0 ; i < this.inputs.length ; i ++) {
            if (this.inputs[i].connected() &&
                (this.inputs[i].contains(x - this.x, y - this.y))) {
                // disconnect wire from current connection and drag
                this.inputs[i].wires[0].disconnectAndDrag(e, x, y);
                return true;
            }
        }
        return false;
    };

    this.setXY = function (x, y) {
        // check to make sure this gate wasn't moved past a gate it was connected to.
        for (var i = 0 ; i < this.output.wires.length ; i ++) {
            var otherGate = this.output.wires[i].dest.parent;
            if (otherGate !== null) {
                if (otherGate === workspace) {
                    // connections on workspaces are absolute locations
                    otherGate = this.output.wires[i].dest;
                }
                x = Math.min(x, otherGate.x - this.width);
            }
        }
        for (var i = 0 ; i < this.inputs.length ; i ++) {
            if (this.inputs[i].connected()) {
                var otherConnection = this.inputs[i].wires[0].parent;
                var otherConnectionX = otherConnection.x;
                if (otherConnection.parent !== workspace) {
                    // connections on workspaces are absolute locations
                    otherConnectionX = otherConnection.parent.x + otherConnection.parent.width;
                }
                x = Math.max(x, otherConnectionX);
            }
        }
        this.x = x;
        this.y = y;
    }

    this.draw = function () {
        var context = this.canvas.getContext("2d");
        context.drawImage(this.image, this.x, this.y, this.width, this.height);
        this.output.draw(context, this.x, this.y);
        for (var i = 0 ; i < this.inputs.length ; i ++) {
            this.inputs[i].draw(context, this.x, this.y);
        }
    };

    this.release = function () {
        if (((this.x + this.width) < 0) || ((this.y + this.height) < 0) ||                               (this.x >= this.canvas.width) || (this.y >= this.canvas.height)) {
            var releases = document.getElementById("releases");
            releases.innerHTML = "" + (parseInt(releases.innerHTML) + 1);

            for (var i = 0 ; i < this.output.wires.length ; i ++) {
                var wire = this.output.wires[i];
                wire.disconnect();
            }
            for (var i = 0 ; i < this.inputs.length ; i ++) {
                if (this.inputs[i].connected()) {
                    var wire = this.inputs[i].wires[0];
                    wire.disconnect();
                }
            }
        }
    }

    this.exp = function () { 
        this.str = "(";
        for (var i = 0 ; i < this.inputs.length ; i ++) {
            if (this.inputs[i].connected()) {
                var sub_exp = this.inputs[i].wires[0].exp();
		if (this.str.length > 1) {
		   this.str += this.operator;
		}
		this.str += sub_exp;
            }
        }
        return this.str + ")";
    }        
}

function And(workspace, x, y) {
    this.initGate(workspace, x, y, 3);
    this.text = "AND";
    this.image = new Image();
    this.image.src = "/img/" + this.text + ".png";
    this.operator = "*"

    this.value = function () { 
        var output = "x";
        for (var i = 0 ; i < this.inputs.length ; i ++) {
            if (this.inputs[i].connected()) {
                var input = this.inputs[i].wires[0].value();
                if (input === 1) {
                   if (output === "x") { output = 1; }                
                } else if (input === 0) {
                    output = 0;
                } else {
                    return "x";
                }
            }
        }
        return output;
    }        
}

And.prototype = new Gate();

function Or(workspace, x, y) {
    this.initGate(workspace, x, y, 3);
    this.text = "OR";
    this.image = new Image();
    this.image.src = "/img/" + this.text + ".png";
    this.operator = "+"

    this.value = function () { 
        var output = "x";
        for (var i = 0 ; i < this.inputs.length ; i ++) {
            if (this.inputs[i].connected()) {
                var input = this.inputs[i].wires[0].value();
                if (input === 0) {
                   if (output === "x") { output = 0; }                
                } else if (input === 1) {
                    output = 1;
                } else {
                    return "x";
                }
            }
        }
        return output;
    }        
}

Or.prototype = new Gate();

function Not(workspace, x, y) {
    this.initGate(workspace, x, y, 1);
    this.text = "NOT";
    this.image = new Image();
    this.image.src = "/img/" + this.text + ".png";

    this.exp = function () { 
        if (!this.inputs[0].connected()) {
           return "-";
	}
        return this.inputs[0].wires[0].exp() + "'";
    }        

    this.value = function () { 
        if (this.inputs[0].connected()) {
            var input = this.inputs[0].wires[0].value();
            if (input === 0) {
                return 1;
            }
            if (input === 1) {
                return 0;
            }
        }
        return "x";
    }        
}

Not.prototype = new Gate();

function handleButtonClick(e) {
    var canvas = e.currentTarget;

    // attach the touchstart, touchmove, touchend event listeners.
//     canvas.addEventListener('touchstart',draw, false);
//     canvas.addEventListener('touchmove',draw, false);
//     canvas.addEventListener('touchend',draw, false);
// http://tenderlovingcode.com/blog/web-apps/html5-canvas-drawing-on-ipad/

    var position = canvas.relMouseCoords(e);
    workspace.click(e, position.x, position.y);
}

function circuit_init() {
    var canvas = document.getElementById("workspace");
    canvas.onmousedown = handleButtonClick;
    workspace = new Workspace(canvas);
    setTimeout(function () { workspace.draw(); }, 200);
    
}

        