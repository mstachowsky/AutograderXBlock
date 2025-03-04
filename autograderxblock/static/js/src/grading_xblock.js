function GradingXBlockStudio(runtime, element) {
    var $element = $(element);

    // Initialize sortable to enable drag-and-drop
    $element.find('#rubric-editor').sortable();

    var addItemBtn = $element.find('#add-rubric-item');

    // Add new rubric item
    addItemBtn.on('click', function() {
        var newIndex = $element.find('.rubric-item').length;
        var newItemHtml = `
            <div class="rubric-item" data-index="${newIndex}">
                <input type="text" class="rubric-label" placeholder="Label" />
                <input type="text" class="rubric-description" placeholder="Description" />
                <input type="number" class="rubric-weight" placeholder="Weight" />
                <button class="delete-rubric-item">Delete</button>
            </div>
        `;
        $element.find('#rubric-editor').append(newItemHtml);
    });

    // Handle rubric item deletion
    $element.on('click', '.delete-rubric-item', function() {
        $(this).closest('.rubric-item').remove();
    });

    // Handle save button click
    $element.find('.save-button').on('click', function() {
        var rubricItems = [];
        $element.find('.rubric-item').each(function(index, elem) {
            rubricItems.push({
                'label': $(elem).find('.rubric-label').val(),
                'description': $(elem).find('.rubric-description').val(),
                'weight': parseInt($(elem).find('.rubric-weight').val()) || 0
            });
        });

       /* var data = {
            'question_description': $element.find('#question_description').val(),
            'rubric': rubricItems,
			'model_name': $element.find('#model_name').val() // Add model_name to the data
        };*/
		var data = {
            'question_description': $element.find('#question_description').val(),
            'rubric': rubricItems,
            'model_name': $element.find('#model_name').val(),
            'show_label': $element.find('#show_label').is(':checked'),  // Get value of show_label checkbox
            'show_feedback': $element.find('#show_feedback').is(':checked') // Get value of show_feedback checkbox
        };

        runtime.notify('save', {state: 'start'});
        var handlerUrl = runtime.handlerUrl(element, 'save_studio_data');
        $.post(handlerUrl, JSON.stringify(data)).done(function(response) {
            runtime.notify('save', {state: 'end'});
        });
    });
}

function GradingXBlockStudent(runtime, element, data) {
    var $element = $(element);
	console.log(data)
    // Access show_label and show_feedback from data attributes
    var showLabel = data.show_label;
    var showFeedback = data.show_feedback;

    $element.find('#submit-answer').on('click', function() {
        var dataToSend = {
            'student_answer': $element.find('#student_answer').val()
        };
        var handlerUrl = runtime.handlerUrl(element, 'grade_submission');

        $.post(handlerUrl, JSON.stringify(dataToSend)).done(function(response) {
            console.log(response);

            // Extract content from tags using regex
            let evalString = response.evaluation;
            let labelMatch = evalString.match(/<label>([\s\S]*?)<\/label>/);
            let feedbackMatch = evalString.match(/<feedback>([\s\S]*?)<\/feedback>/);

            let label = labelMatch ? labelMatch[1].trim() : '';
            let feedback = feedbackMatch ? feedbackMatch[1].trim() : '';

            // Update the DOM based on show_label and show_feedback settings
            if (showLabel) {
                $element.find('#evaluation .label').html('<strong>Label:</strong> ' + label);
            } else {
                $element.find('#evaluation .label').html('');
            }

            if (showFeedback) {
                $element.find('#evaluation .feedback').html('<strong>Feedback:</strong> ' + feedback);
            } else {
                $element.find('#evaluation .feedback').html('');
            }
			
			if(!showFeedback && !showLabel){
				$element.find('#evaluation .label').html('<strong>Submission Received!</strong>');
			}
        });
    });
}

/*
function GradingXBlockStudent(runtime, element,data_bools) {
    var $element = $(element);
	 // Access show_label and show_feedback from data attributes
    var showLabel = data_bools.show_label;
    var showFeedback = data_bools.show_feedback;
	console.log(data_bools)
	console.log(showFeedback)
    $element.find('#submit-answer').on('click', function() {
        var data = {
            'student_answer': $element.find('#student_answer').val()
        };
        var handlerUrl = runtime.handlerUrl(element, 'grade_submission');
		$.post(handlerUrl, JSON.stringify(data)).done(function(response) {
			console.log(data)
			// Parse the evaluation string to extract label and feedback
			let evalString = response.evaluation;
			console.log(response)
			// Extract content from tags using regex
			let labelMatch = evalString.match(/<label>([\s\S]*?)<\/label>/);
			let feedbackMatch = evalString.match(/<feedback>([\s\S]*?)<\/feedback>/);
			
			// Get the content or empty string if not found
			let label = labelMatch ? labelMatch[1].trim() : '';
			let feedback = feedbackMatch ? feedbackMatch[1].trim() : '';
			// Update the DOM based on show_label and show_feedback settings
            if (showLabel) {
                $element.find('#evaluation .label').html('<strong>Label:</strong> ' + label);
            } else {
                $element.find('#evaluation .label').html('');
            }

            if (showFeedback) {
                $element.find('#evaluation .feedback').html('<strong>Feedback:</strong> ' + feedback);
            } else {
                $element.find('#evaluation .feedback').html('');
            }
			// Update the DOM with formatted content
			//$element.find('#evaluation .label').html('<strong>Submission received!<\strong>');
			//$element.find('#evaluation .label').html('<strong>Label:</strong> ' + label);
			//$element.find('#evaluation .feedback').html('<strong>Feedback:</strong> ' + feedback);
		});
    });
}*/
