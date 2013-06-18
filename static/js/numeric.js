function validate_b(elements) {
    validate_elements(elements, '01');
}

function validate_d(elements) {
    validate_elements(elements, '-0123456789');
}

function validate_h(elements) {
    validate_elements(elements, '0123456789ABCDEFabcdef');
}

function validate_decimal(elements) {
    validate_elements(elements, '.-0123456789');
}


function validate_elements(elements, allowed_characters) {
    elements.keypress(function(event) {
        return filter_input_character(event, allowed_characters);
    });

    // keyup is activated after input has been updated, so no timeout is needed
    // I can't just do
    // elements.keyup(checkSubmit);
    // because that would pass a truthy argument to checkSubmit
    // and therefore the submit button would always get enabled
    elements.keyup(function() {
        checkSubmit();
    });

    function value_changed(event) {
        filter_input_value(event, allowed_characters);
        checkSubmit();
    }

    elements.on('paste', function(event) {
        // this is to trigger the function after value is updated
        setTimeout(function() {
            value_changed(event);
        }, 0);
    });

    // this is a gotta catch 'em all thing
    // nothing should really slip through the cracks
    // but it can't hurt to be careful
    elements.change(value_changed);
}

function filter_input_character(event, allowed_characters) {  
    submitOnEnter(event);

    // jQuery standardizes which, so that's all we need to check
    // which == 0 covers delete, tab, home, end and the arrow keys
    // backspace needs to be handled explicitly
    if (event.which == 0 || event.altKey || event.ctrlKey || event.metaKey) {
        return true;
    } else {
        var character = String.fromCharCode(event.which);
        return character === '\b' ||
            allowed_characters.indexOf(character) !== -1;
    }
}

function filter_input_value(event, allowed_characters) {
    var value = event.currentTarget.value;
    var filtered_value = value.split('').filter(function(character) {
        return allowed_characters.indexOf(character) !== -1;
    }).join('');

    // this should minimize the number of sudden cursor changes,
    // although they'll still happen unfortunately
    if (value !== filtered_value) {
        event.currentTarget.value = filtered_value;
    }
}
