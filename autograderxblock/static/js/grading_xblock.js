function GradingXBlockStudio(runtime, element) {
    
	
	var addItemBtn = document.getElementById('add-rubric-item');
    
    addItemBtn.onclick = function() {
        // Create a new rubric item
        var newIndex = $('#rubric-editor .rubric-item').length;
        var newItemHtml = `
            <div class="rubric-item" data-index="${newIndex}">
                <input type="text" class="rubric-label" placeholder="Label" />
                <input type="text" class="rubric-description" placeholder="Description" />
                <input type="number" class="rubric-weight" placeholder="Weight" />
            </div>
        `;
        $('#rubric-editor').append(newItemHtml);
    };

    $(element).find('.save-button').bind('click', function() {
        var rubricItems = [];
        $('#rubric-editor .rubric-item').each(function(index, elem) {
            rubricItems.push({
                'label': $(elem).find('.rubric-label').val(),
                'description': $(elem).find('.rubric-description').val(),
                'weight': parseInt($(elem).find('.rubric-weight').val()) || 0
            });
		console.log(rubricItems)
        });
        
        var data = {
            'question_description': $('#question_description').val(),
            'rubric': rubricItems
        };
		console.log(data)
        
        runtime.notify('save', {state: 'start'});
        var handlerUrl = runtime.handlerUrl(element, 'save_studio_data');
        $.post(handlerUrl, JSON.stringify(data)).done(function(response) {
            runtime.notify('save', {state: 'end'});
        });
    });
}

function GradingXBlockStudent(runtime, element) {
    var submitBtn = document.getElementById('submit-answer');
    
    submitBtn.onclick = function() {
        var data = {
            'student_answer': $('#student_answer').val()
        };
        var handlerUrl = runtime.handlerUrl(element, 'grade_submission');
        $.post(handlerUrl, JSON.stringify(data)).done(function(response) {
            $('#evaluation').text(response.evaluation);
            // Update grade display here if needed
        });
    };
}
