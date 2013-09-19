function drag(elementToDrag, event) {
	console.log("drag(elementToDrag, event)");
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
		console.log("drag.moveHandler(e)");
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
		console.log("drag.upHandler(e)");
		elementToDrag.release();
		workspace.draw();

		// Unregister the capturing event handlers.
		document.removeEventListener("mouseup", upHandler, true);
		document.removeEventListener("mousemove", moveHandler, true);

		// And don't let the event propagate any further.
		e.stopPropagation();  
	}
}

var student_format = new Array();

function relMouseCoords(event){
	console.log("relMouseCoords(event)");
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

function Workspace(canvas) {
	console.log("Workspace(canvas)");
	this.canvas = canvas;
	this.x = this.y = 0;
	this.children = new Array(); // Blocks
	this.tiles = new Array();

	this.evaluate = function() {
		console.log("Workspace.evaluate()");
		// Each tile has a "data" field, which stores a string
		// representing the type of block covering it.
		// If it is not covered by any block, its "occupied"
		// field is false.
		for (var i = 0; i < this.tiles.length; i++) {
			if (this.tiles[i].occupied === true) {
				student_format[i] = this.tiles[i].data;
			} else {
				// If any bit tiles aren't occupied, we don't
				// want to evaluate the student's answer yet.
				return new Array();
			}
		}
		return student_format;
	}

	this.evaluateAll = function () {
		console.log("Workspace.evaluateAll()");
		student_format = this.evaluate();
		evaluate_instruction(student_format);
	}

	this.draw = function () {
		console.log("Workspace.draw()");
		var context = this.canvas.getContext("2d");
		context.fillStyle = "white";
		context.fillRect(0, 0, this.canvas.width, this.canvas.height);

		// A rectangle drawn around the bit tiles
		context.strokeRect(this.canvas.width/2 - 320, 10, 641, 32);

		// Draw the bit tiles
		for (var i = 0; i < 32; i++) {
			this.tiles[i].draw();
		}

		// Draw the blocks
		for (i = 0; i < this.children.length; i++) {
			this.children[i].draw();
		}
		this.evaluateAll();
	}

	this.click = function (e, x, y) {
		console.log("Workspace.click(e,x,y)");
		for (var i = 0 ; i < this.factories.length ; i ++) {
			if (this.children[i].contains(x, y)) {
				// If we haven't submitted yet, drag the block
				// (to prevent cheating by moving blocks after submit)
				if (this.children[i].enabled === true) {
					drag(this.children[i], e);
					return;
				}
			}
		}
	}

	this.drawSolution = function(format_type) {
		console.log("Workspace.draw_solution(%s)" % format_type);
		rd = this.children[0];
		rs = this.children[1];
		rt = this.children[2];
		shamt = this.children[3];
		opcode = this.children[4];
		funct = this.children[5];
		immediate = this.children[6];
		address = this.children[7];

		// Disconnect all the blocks and put them back
		// to their starting positions.
		for (var i = 0; i < this.children.length; i++) {
			this.children[i].disconnect();
			this.children[i].setXY(10, 32*i+52);
			this.children[i].draw();
		}
		// Connect the blocks to their proper
		// bit tile.
		if (String(format_type) === "R") {
			opcode.connectTo(this.tiles[0], 0);
			rs.connectTo(this.tiles[6], 6);
			rt.connectTo(this.tiles[11], 11);
			rd.connectTo(this.tiles[16], 16);
			shamt.connectTo(this.tiles[21], 21);
			funct.connectTo(this.tiles[26], 26);
		} else if (String(format_type) === "I") {
			opcode.connectTo(this.tiles[0], 0);
			rs.connectTo(this.tiles[6], 6);
			rt.connectTo(this.tiles[11], 11);
			immediate.connectTo(this.tiles[16], 16);
		} else if (String(format_type) === "J") {
			opcode.connectTo(this.tiles[0], 0);
			address.connectTo(this.tiles[6], 6);
		}
		this.draw();
	}

	this.gradeFormat = function(format_type, format) {
		console.log("Workspace.gradeFormat(format_type)");
		for (var i = 0; i < this.children.length; i++) {
			if (this.children[i].tiles.length > 0) {
				block = this.children[i];
				start_tile = 31 - block.tiles[0].bit;
				if (format[start_tile] !== block.text) {
					block.draw_incorrect();
				}
			}
		}
	}

	this.disableChildren = function() {
		for (var i = 0; i < this.children.length; i++) {
			this.children[i].disable();
		}
	}

	this.factories = [rd, rs, rt, shamt, opcode, funct, immediate, address];
	this.widths = [100, 100, 100, 100, 120, 120, 320, 520];

	for (var i = 0 ; i < this.factories.length ; i ++) {
		var block = new this.factories[i](this, 10, 32*i+56);
		block.draw();
	}

	for (i = 0; i < 32; i++) {
		this.tiles[i] = new tile(this, this.canvas.width/2 - 320 + i*20, 10, 31-i);
	}

	this.draw();

	// To randomly place blocks on the canvas (below the bit tiles)
/*	for (var i = 0; i < this.factories.length; i++) {
		x = Math.floor(Math.random()*(this.canvas.width - this.widths[i]+10)); // self.generator.randint(10,this.canvas.width - this.widths[i]);
		y = Math.floor(Math.random()*(this.canvas.height - 82)); //self.generator.randint(52, this.canvas.height - 32);
		if (x < 10) {
			x += 10;
		}
		if (x >= this.canvas.width - this.widths[i]) {
			x -= this.widths[i];
		}
		if (y < 52) {
			y += 52;
		}
		if (y >= this.canvas.height - 32) {
			y -= 32;
		}
		console.log(x);
		console.log(y);
		var gate = new this.factories[i](this, x, y);
		gate.draw();
	}*/
}

function Block() {
	console.log("Block()");
	this.initBlock = function (workspace, x, y, num_bits) {
		console.log("Block.initBlock(workspace,x,y,num_bits)");
		this.workspace = workspace;
		workspace.children.push(this);
		this.canvas = workspace.canvas;
		this.num_bits = num_bits;
		this.width = this.num_bits * 20;
		this.height = 32;
		this.x = x;
		this.y = y;
		this.text = "";
		this.tiles = new Array();
		this.enabled = true; // later disabled to prevent cheating
	};

	this.contains = function (x, y) {
		console.log("Block.contains(x,y)");
		var slop = 10;
		return ((x >= (this.x - slop)) && (y >= (this.y - slop)) && 
		   (x <= (this.x + this.width + slop)) && (y <= (this.y + this.height + slop)));
	};

	this.setXY = function (x, y) {
		console.log("Block.setXY(x,y)");
		this.x = x;
		this.y = y;
	}

	this.connect = function() {
		console.log("Block.connect()");
		// Perhaps make it so that if it is to the left of tile[0]
		// or to the right of tile[31], it automatically snaps
		// to those tiles
		best_idx = -1;
		var best_tile = null;
		var best_dist = 100;
		var tolerance = 15;
		// Find the closest sequence of unoccupied bit tiles that to this block.
		for (var i = 0; i < this.workspace.tiles.length - this.num_bits + 1; i++) {
			tile = this.workspace.tiles[i];
			current_dist = Math.abs(tile.x - this.x);
			if (current_dist < best_dist && tile.occupied === false && current_dist < tolerance) {
				tiles_open = true;
				for (var j = 0; j < this.num_bits; j++) {
					next_tile = this.workspace.tiles[i+j];
					if (next_tile.occupied === true) {
						tiles_open = false;
						break;
					}
				}
				if (tiles_open === true) {
					best_tile = tile;
					best_idx = i;
					best_dist = current_dist;
				}
			}
		}
		if (best_tile !== null) {
			this.setXY(best_tile.x, best_tile.y);
			this.tiles = [];
			for (i = best_idx; i < best_idx + this.num_bits; i++) {
				tile = this.workspace.tiles[i];
				tile.data = this.text;
				tile.occupied = true;
				this.tiles.push(tile);
			}
		}
		// If we can't find a good bit tile, release the
		// block at its current location.
		else {
			this.disconnect();
		}
	}

	// For drawing solutions
	this.connectTo = function(tile, idx) {
		console.log("Block.connectTo(tile,idx)");
		this.disconnect();
		this.setXY(tile.x, tile.y);
		this.tiles = [];
		for (var i = idx; i < idx + this.num_bits; i++) {
			temp_tile = this.workspace.tiles[i];
			temp_tile.data = this.text;
			temp_tile.occupied = true;
			this.tiles.push(temp_tile);
		}
	}

	this.disconnect = function () {
		console.log("Block.disconnect()");
		// De-occupy the bit tiles so that other blocks
		// can occupy them.
		for (var i = 0; i < this.tiles.length; i++) {
			this.tiles[i].occupied = false;
		}
		this.tiles = [];
	}

	this.draw = function () {
		console.log("Block.draw()");
		var context = this.canvas.getContext("2d");
		context.drawImage(this.image, this.x, this.y, this.width, this.height);
	};

	this.draw_incorrect = function() {
		console.log("Block.draw_incorrect()");
		var context = this.canvas.getContext("2d");
		context.drawImage(this.incorrect_image, this.x, this.y, this.width, this.height);
	}

	this.release = function () {
		console.log("Block.release()");
		this.disconnect();
		// If we drag a block outside the canvas, bring it back.
		if (((this.x + this.width/2 < 0) || ((this.y + this.height/2) < 0) ||
			(this.x + this.width/2 >= this.canvas.width) || (this.y + this.height/2 >= this.canvas.height))) {
			if (this.x + this.width/2 < 0) {
				this.setXY(10, this.y);
			}
			if (this.y + this.height/2 < 0) {
				this.setXY(this.x, 56);
			}
			if (this.x + this.width/2 >= this.canvas.width) {
				this.setXY(this.canvas.width - this.width - 10, this.y);
			}
			if (this.y + this.height/2 >= this.canvas.height) {
				this.setXY(this.x, this.canvas.height - this.height - 10);
			}
		}
		if (this.y <= 42) {
			this.connect(); // Connect to a bit tile
		}
	}

	this.disable = function() {
		this.enabled = false;
	}
}

function tile(workspace, x, y, bit) {
	console.log("tile(workspace,x,y,bit)");
	this.initTile = function (workspace, x, y) {
		console.log("tile.initTile(workspace,x,y)");
		this.workspace = workspace;
		this.canvas = workspace.canvas;
		this.width = 20;
		this.height = 32;
		this.x = x;
		this.y = y;
		this.num_bits = 1;
	};
	this.initTile(workspace, x, y);
	this.text = "tile";
	this.image = new Image();
	this.image.src = "/img/" + this.text + ".png";
	this.bit = bit;
	this.occupied = false;
	this.data = "";

	this.draw = function () {
		console.log("tile.draw()");
		var context = this.canvas.getContext("2d");
		context.drawImage(this.image, this.x, this.y, this.width, this.height);
		context.font = ".9em courier new";
		context.fillStyle = "black";
		context.textAlign = "center";
		context.fillText(String(this.bit), this.x + this.width/2, this.y+this.height/2+5);
	};
}

tile.prototype = new Block();

function opcode(workspace, x, y) {
	console.log("opcode(workspace,x,y)");
	this.initBlock(workspace, x, y, 6);
	this.text = "opcode";
	this.image = new Image();
	this.image.src = "/img/" + this.text + ".png";
	this.incorrect_image = new Image();
	this.incorrect_image.src = "/img/" + this.text + "_incorrect.png";
	this.width = 120;
	this.height = 32;

	this.connectTo = function(tile, idx) {
		this.disconnect();
		this.setXY(tile.x, tile.y);
		this.tiles = [];
		for (var i = idx; i < idx + this.num_bits; i++) {
			temp_tile = this.workspace.tiles[i];
			temp_tile.data = this.text;
			temp_tile.occupied = true;
			this.tiles.push(temp_tile);
		}
	}
}

opcode.prototype = new Block();

function rs(workspace, x, y) {
	console.log("rs(workspace,x,y)");
	this.initBlock(workspace, x, y, 5);
	this.text = "rs";
	this.image = new Image();
	this.image.src = "/img/" + this.text + ".png";
	this.incorrect_image = new Image();
	this.incorrect_image.src = "/img/" + this.text + "_incorrect.png";
	this.width = 100;
	this.height = 32;
	this.connectTo = function(tile, idx) {
		this.disconnect();
		this.setXY(tile.x, tile.y);
		this.tiles = [];
		for (var i = idx; i < idx + this.num_bits; i++) {
			temp_tile = this.workspace.tiles[i];
			temp_tile.data = this.text;
			temp_tile.occupied = true;
			this.tiles.push(temp_tile);
		}
	}
}

rs.prototype = new Block();

function rt(workspace, x, y) {
	console.log("rt(workspace,x,y)");
	this.initBlock(workspace, x, y, 5);
	this.text = "rt";
	this.image = new Image();
	this.image.src = "/img/" + this.text + ".png";
	this.incorrect_image = new Image();
	this.incorrect_image.src = "/img/" + this.text + "_incorrect.png";
	this.width = 100;
	this.height = 32;
	this.connectTo = function(tile, idx) {
		this.disconnect();
		this.setXY(tile.x, tile.y);
		this.tiles = [];
		for (var i = idx; i < idx + this.num_bits; i++) {
			temp_tile = this.workspace.tiles[i];
			temp_tile.data = this.text;
			temp_tile.occupied = true;
			this.tiles.push(temp_tile);
		}
	}
}

rt.prototype = new Block();

function rd(workspace, x, y) {
	console.log("rd(workspace,x,y)");
	this.initBlock(workspace, x, y, 5);
	this.text = "rd";
	this.image = new Image();
	this.image.src = "/img/" + this.text + ".png";
	this.incorrect_image = new Image();
	this.incorrect_image.src = "/img/" + this.text + "_incorrect.png";
	this.width = 100;
	this.height = 32;
	this.connectTo = function(tile, idx) {
		this.disconnect();
		this.setXY(tile.x, tile.y);
		this.tiles = [];
		for (var i = idx; i < idx + this.num_bits; i++) {
			temp_tile = this.workspace.tiles[i];
			temp_tile.data = this.text;
			temp_tile.occupied = true;
			this.tiles.push(temp_tile);
		}
	}
}

rd.prototype = new Block();

function shamt(workspace, x, y) {
	console.log("shamt(workspace,x,y)");
	this.initBlock(workspace, x, y, 5);
	this.text = "shamt";
	this.image = new Image();
	this.image.src = "/img/" + this.text + ".png";
	this.incorrect_image = new Image();
	this.incorrect_image.src = "/img/" + this.text + "_incorrect.png";
	this.width = 100;
	this.height = 32;
	this.connectTo = function(tile, idx) {
		this.disconnect();
		this.setXY(tile.x, tile.y);
		this.tiles = [];
		for (var i = idx; i < idx + this.num_bits; i++) {
			temp_tile = this.workspace.tiles[i];
			temp_tile.data = this.text;
			temp_tile.occupied = true;
			this.tiles.push(temp_tile);
		}
	}
}

shamt.prototype = new Block();

function funct(workspace, x, y) {
	console.log("funct(workspace,x,y)");
	this.initBlock(workspace, x, y, 6);
	this.text = "funct";
	this.image = new Image();
	this.image.src = "/img/" + this.text + ".png";
	this.incorrect_image = new Image();
	this.incorrect_image.src = "/img/" + this.text + "_incorrect.png";
	this.width = 120;
	this.height = 32;
	this.connectTo = function(tile, idx) {
		this.disconnect();
		this.setXY(tile.x, tile.y);
		this.tiles = [];
		for (var i = idx; i < idx + this.num_bits; i++) {
			temp_tile = this.workspace.tiles[i];
			temp_tile.data = this.text;
			temp_tile.occupied = true;
			this.tiles.push(temp_tile);
		}
	}
}

funct.prototype = new Block();

function immediate(workspace, x, y) {
	console.log("immediate(workspace,x,y)");
	this.initBlock(workspace, x, y, 16);
	this.text = "immediate";
	this.image = new Image();
	this.image.src = "/img/" + this.text + ".png";
	this.incorrect_image = new Image();
	this.incorrect_image.src = "/img/" + this.text + "_incorrect.png";
	this.width = 320;
	this.height = 32;
	this.connectTo = function(tile, idx) {
		this.disconnect();
		this.setXY(tile.x, tile.y);
		this.tiles = [];
		for (var i = idx; i < idx + this.num_bits; i++) {
			temp_tile = this.workspace.tiles[i];
			temp_tile.data = this.text;
			temp_tile.occupied = true;
			this.tiles.push(temp_tile);
		}
	}
}

immediate.prototype = new Block();

function address(workspace, x, y) {
	console.log("address(workspace,x,y)");
	this.initBlock(workspace, x, y, 26);
	this.text = "address";
	this.image = new Image();
	this.image.src = "/img/" + this.text + ".png";
	this.incorrect_image = new Image();
	this.incorrect_image.src = "/img/" + this.text + "_incorrect.png";
	this.width = 520;
	this.height = 32;
	this.connectTo = function(tile, idx) {
		this.disconnect();
		this.setXY(tile.x, tile.y);
		this.tiles = [];
		for (var i = idx; i < idx + this.num_bits; i++) {
			temp_tile = this.workspace.tiles[i];
			temp_tile.data = this.text;
			temp_tile.occupied = true;
			this.tiles.push(temp_tile);
		}
	}
}

address.prototype = new Block();

function handleButtonClick(e) {
	console.log("handleButtonClick(e)");
	var canvas = e.currentTarget;
	var position = canvas.relMouseCoords(e);
	workspace.click(e, position.x, position.y);
}

function instruction_format_init(id) {
	console.log("circuit_init(id)");
	var canvas = document.getElementById(String(id));
	canvas.onmousedown = handleButtonClick;
	workspace = new Workspace(canvas);
	setTimeout(function () { workspace.draw(); }, 200);
}

		
