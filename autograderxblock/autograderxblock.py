"""TO-DO: Write a description of what this XBlock is."""

from importlib.resources import files
import pkg_resources
from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.fields import Integer, Scope, String, List
from django.template import Context, Template
class AutograderXBlock(XBlock):
        
    #question_description = String(default="Enter the question description here", scope=Scope.settings)
    question_description = String(
        help="Description of the question",
        default="",
        scope=Scope.content
    )
     # TO-DO: delete count, and define your own fields.
    count = Integer(
        default=34, scope=Scope.content,
        help="A simple counter, to show something happening",
    )

    """
    rubric = List(default=[{"label": "meets expectations", "description": "", "weight": 0},
                           {"label": "does not meet expectations", "description": "", "weight": 0}],
                 scope=Scope.settings)
    """
    rubric = List(
        default=[{'label': 'Meets Expectations', 'description': '', 'weight': 0},
                 {'label': 'Does Not Meet Expectations', 'description': '', 'weight': 0}],
        scope=Scope.content,
        help="Editable rubric with labels and weights"
    )
    def render_template(self, template_path, context={}):
        template_str = self.resource_string(template_path)
        template = Template(template_str)
        return template.render(Context(context))
    
    def resource_string(self, path):
        """Helper to load a resource from the static directory."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")
    
    def studio_view(self, context):
        print("++++++++========**********In studio view")
        print(f"Question Description: {self.question_description}")
        print(f"Rubric: {self.rubric}")
        # Render authoring (Studio) view as HTML form
        #html = self.resource_string("static/html/grading_xblock_studio.html")
        html = self.render_template("static/html/grading_xblock_studio.html",{'self':self,"question":self.question_description,'random_thing':self.count})
        
        print("Loaded html template: ",html)
        frag = Fragment()
        frag.add_content(html)
        #frag = Fragment(html.format(self=self,question=self.question_description,random_thing=34))
        frag.add_css(self.resource_string("static/css/grading_xblock.css"))
        frag.add_javascript(self.resource_string("static/js/src/grading_xblock.js"))
        frag.initialize_js('GradingXBlockStudio')
        
        return frag

    @XBlock.json_handler
    def save_studio_data(self, data, suffix=''):
        # Save Studio data
        print("========================!!!!!!!!!!!!!!!!!!+================")
        
        self.question_description = data.get("question_description", "")
        self.rubric = data.get("rubric", [])
        print(self.question_description)
        print(self.rubric)
        return {"result": "success"}

    def student_view(self, context):
        html = self.resource_string("static/html/grading_xblock_student.html")
        #frag = Fragment(html.format(self=self))
        frag = Fragment(html.format(self=self,question=self.question_description,random_thing=34))
        frag.add_css(self.resource_string("static/css/grading_xblock.css"))
        frag.add_javascript(self.resource_string("static/js/src/grading_xblock.js"))
        frag.initialize_js('GradingXBlockStudent')
        return frag

    @XBlock.json_handler
    def grade_submission(self, data, suffix=''):
        student_answer = data.get("student_answer", "")
        rubric = self.rubric  # Get the rubric that was saved
        rubric_string = self.format_rubric_for_grading(rubric)

        # Call the external evaluation function
        evaluation_string = text_text_eval(document_text=student_answer, prompt=rubric_string, model='phi', max_length=1024)

        # Call grade computation function
        grade = compute_grade(evaluation_string, [item['weight'] for item in rubric])

        # Save the student's grade
        self.runtime.publish(self, 'grade', {
            'value': grade,
            'max_value': 100,
        })

        return {
            "evaluation": evaluation_string,
            "grade": grade
        }

    def format_rubric_for_grading(self, rubric):
        # Format the rubric as needed for your external evaluation
        rubric_str = "\n".join([f"{item['label']}: {item['description']}" for item in rubric])
        return rubric_str
    # TO-DO: change this to create the scenarios you'd like to see in the
    # workbench while developing your XBlock.
    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("AutograderXBlock",
             """<autograderxblock/>
             """),
            ("Multiple AutograderXBlock",
             """<vertical_demo>
                <autograderxblock/>
                <autograderxblock/>
                <autograderxblock/>
                </vertical_demo>
             """),
        ]
