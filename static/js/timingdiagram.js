// draw a dashed line
// taken from http://vetruvet.blogspot.com/2010/10/drawing-dashed-lines-on-html5-canvas.html
CanvasRenderingContext2D.prototype.dashedLine = function(x1, y1, x2, y2, dashLen) {
    if (dashLen == undefined) dashLen = 2;
    
    this.beginPath();
    this.moveTo(x1, y1);
    
    var dX = x2 - x1;
    var dY = y2 - y1;
    var dashes = Math.floor(Math.sqrt(dX * dX + dY * dY) / dashLen);
    var dashX = dX / dashes;
    var dashY = dY / dashes;
    
    var q = 0;
    while (q++ < dashes) {
     x1 += dashX;
     y1 += dashY;
     this[q % 2 == 0 ? 'moveTo' : 'lineTo'](x1, y1);
    }
    this[q % 2 == 0 ? 'moveTo' : 'lineTo'](x2, y2);
    
    this.stroke();
    this.closePath();
};


/**
 * Timing diagram class
 *
 * Arguments:
 * canvas is the canvas object to draw on
 * signals is an array of signal objects
 *     each signal object has the following fields:
 *     name: name associated with that signal
 *     binary: true if only possible values are 0s and 1s
 *     values: array of timing values; each timing value is an object
 *             with time and value fields. For a binary signal, value can
 *             only be 0 or 1, otherwise it can be an arbitrary string.
 *  labeledMarkers is an array of times at which to place dashed vertical lines
 *      each marker gets labeled as t0, t1, etc.
 *  unlabeledMarkers is like labeledMarkers except with a different color and no labeling
 *      it it the caller's responsibility to ensure no overlap between the two marker arrays
 *      because the behavior on an overlap is undefined
 */
function TimingDiagram(canvas, signals, labeledMarkers, unlabeledMarkers) {
    this.ctx = canvas.getContext('2d');
    this.signals = signals;
    this.labeledMarkers = labeledMarkers;
    this.unlabeledMarkers = unlabeledMarkers;

    // y coordinate of y axis
    this.yAxisY = TimingDiagram.getSignalBaseY(signals.length - 1) + TimingDiagram.topYMargin;

    canvas.width = TimingDiagram.getTimeX(TimingDiagram.maxTime);
    canvas.height = this.yAxisY + 20;

    this.ctx.lineWidth = 1;
    this.ctx.font = '12px monospace';
}


// static variables of TimingDiagram
TimingDiagram.xAxisX = 100; // x coordinate of x axis
TimingDiagram.timeWidth = 6; // width of one time unit
TimingDiagram.maxTime = 80;

TimingDiagram.topYMargin = 10; // also for bottom
TimingDiagram.signalSep = 10; // gap between signals
TimingDiagram.signalHeight = 20; // gap between top and bottom of signal

TimingDiagram.axesColor = 'black';
TimingDiagram.textColor = 'black';
TimingDiagram.signalColor = '#0f0';
TimingDiagram.labeledMarkerColor = 'red';
TimingDiagram.unlabeledMarkerColor = '#66f';


// draws the timing diagram
TimingDiagram.prototype.draw = function() {
    this.drawAxes();
    this.drawUnlabeledMarkers();
    this.drawLabeledMarkers();
    this.drawSignals();
};


// draws the x and y axes
TimingDiagram.prototype.drawAxes = function() {
    this.ctx.strokeStyle = TimingDiagram.axesColor;
    this.ctx.beginPath();
    this.ctx.moveTo(TimingDiagram.xAxisX, 0);
    this.ctx.lineTo(TimingDiagram.xAxisX, this.yAxisY);
    this.ctx.lineTo(TimingDiagram.getTimeX(TimingDiagram.maxTime), this.yAxisY);
    this.ctx.stroke();
};


// draws all signals
TimingDiagram.prototype.drawSignals = function() {
    for (var i = 0; i < this.signals.length; ++i) {
        this.drawSignalLabel(i);
        if (this.signals[i].binary) {
            this.drawBinarySignal(i);
        } else {
            this.drawGeneralSignal(i);
        }
    }
};


// draws the y-axis label for a signal
TimingDiagram.prototype.drawSignalLabel = function(signalNum) {
    this.ctx.textAlign = 'right';
    this.ctx.textBaseline = 'middle';
    var x = TimingDiagram.xAxisX - 5;
    var y = TimingDiagram.getSignalMiddleY(signalNum);
    this.ctx.fillStyle = TimingDiagram.textColor;
    this.ctx.fillText(this.signals[signalNum].name, x, y);
};


// draws a binary signal
// assumes signal's first value is at time 0
TimingDiagram.prototype.drawBinarySignal = function(signalNum) {
    var values = this.signals[signalNum].values;
    var yVals = [TimingDiagram.getSignalBaseY(signalNum), TimingDiagram.getSignalTopY(signalNum)];

    this.ctx.strokeStyle = TimingDiagram.signalColor;
    this.ctx.beginPath();
    // no explicit moveTo because first lineTo will do the job

    // value doesn't matter, just to complete diagram
    values.push({ time: TimingDiagram.maxTime });
    for (var i = 0; i < values.length - 1; ++i) {
        var x = TimingDiagram.getTimeX(values[i].time);
        var nextX = TimingDiagram.getTimeX(values[i + 1].time);
        var y = yVals[values[i].value];
        this.ctx.lineTo(x, y); // vertical value change line
        this.ctx.lineTo(nextX, y); // horizontal value line
    }
    values.pop(); // restore back to original
    this.ctx.stroke();
};


// draws a general (arbitrary-valued) signal
// assumes signal's first value is at time 0
TimingDiagram.prototype.drawGeneralSignal = function(signalNum) {
    var changeX = 4; // controls slant on value change

    var values = this.signals[signalNum].values;
    var yVals = [TimingDiagram.getSignalBaseY(signalNum), TimingDiagram.getSignalTopY(signalNum)];
    this.ctx.strokeStyle = TimingDiagram.signalColor;

    for (var line = 0; line < 2; ++line) {
        var topLine = line;
        this.ctx.beginPath();
        this.ctx.moveTo(TimingDiagram.xAxisX, yVals[topLine]);
        for (var i = 1; i < values.length; ++i) {
            var x = TimingDiagram.getTimeX(values[i].time);
            this.ctx.lineTo(x - changeX, yVals[topLine]);
            topLine ^= 1;
            this.ctx.lineTo(x + changeX, yVals[topLine]);
        }
        this.ctx.lineTo(TimingDiagram.getTimeX(TimingDiagram.maxTime), yVals[topLine]);
        this.ctx.stroke();
    }

    this.ctx.textAlign = 'left';
    this.ctx.textBaseline = 'middle';
    var textY = TimingDiagram.getSignalMiddleY(signalNum);
    for (var i = 0; i < values.length; ++i) {
        var x = TimingDiagram.getTimeX(values[i].time) + changeX + 2;
        var textWidth = this.ctx.measureText(values[i].value).width;
        this.ctx.fillStyle = 'white';
        this.ctx.fillRect(x, yVals[1] + 1, textWidth, 12);
        this.ctx.fillStyle = TimingDiagram.textColor;
        this.ctx.fillText(values[i].value, x, textY);
    }
};


// draws all unlabeledMarkers
TimingDiagram.prototype.drawUnlabeledMarkers = function() {
    this.ctx.textAlign = 'center';
    this.ctx.textBaseline = 'top';
    var textY = this.yAxisY + 2;

    for (var i = 0; i < this.unlabeledMarkers.length; ++i) {
        var x = TimingDiagram.getTimeX(this.unlabeledMarkers[i]);
        this.ctx.strokeStyle = TimingDiagram.unlabeledMarkerColor;
        this.ctx.dashedLine(x, this.yAxisY, x, 0, 5);
    }
}


// draws all labeledMarkers
TimingDiagram.prototype.drawLabeledMarkers = function() {
    this.ctx.textAlign = 'center';
    this.ctx.textBaseline = 'top';
    var textY = this.yAxisY + 2;

    for (var i = 0; i < this.labeledMarkers.length; ++i) {
        var x = TimingDiagram.getTimeX(this.labeledMarkers[i]);
        this.ctx.fillStyle = TimingDiagram.textColor;
        this.ctx.fillText('t' + i, x, textY);
        this.ctx.strokeStyle = TimingDiagram.labeledMarkerColor;
        this.ctx.dashedLine(x, this.yAxisY, x, 0, 5);
    }
}


// gets the base (bottom) y position for a particular signal number
TimingDiagram.getSignalBaseY = function(signalNum) {
    return TimingDiagram.topYMargin + TimingDiagram.signalHeight +
        (TimingDiagram.signalHeight + TimingDiagram.signalSep) * signalNum;
};


// gets the middle y position for a particular signal number
TimingDiagram.getSignalMiddleY = function(signalNum) {
    return TimingDiagram.topYMargin + TimingDiagram.signalHeight / 2 +
        (TimingDiagram.signalHeight + TimingDiagram.signalSep) * signalNum;
};


// gets the top y position for a particular signal number
TimingDiagram.getSignalTopY = function(signalNum) {
    return TimingDiagram.topYMargin +
        (TimingDiagram.signalHeight + TimingDiagram.signalSep) * signalNum;
};


// gets the x coordinate for a particular time
TimingDiagram.getTimeX = function(time) {
    return TimingDiagram.xAxisX + time * TimingDiagram.timeWidth;
};
