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