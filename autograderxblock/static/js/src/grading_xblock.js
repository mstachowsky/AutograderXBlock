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

        var data = {
            'question_description': $element.find('#question_description').val(),
            'rubric': rubricItems
        };

        runtime.notify('save', {state: 'start'});
        var handlerUrl = runtime.handlerUrl(element, 'save_studio_data');
        $.post(handlerUrl, JSON.stringify(data)).done(function(response) {
            runtime.notify('save', {state: 'end'});
        });
    });
}


function GradingXBlockStudent(runtime, element) {
    var $element = $(element);

    $element.find('#submit-answer').on('click', function() {
        var data = {
            'student_answer': $element.find('#student_answer').val()
        };
        var handlerUrl = runtime.handlerUrl(element, 'grade_submission');
        $.post(handlerUrl, JSON.stringify(data)).done(function(response) {
            $element.find('#evaluation').text(response.evaluation);
            // Update grade display here if needed
        });
    });
}
