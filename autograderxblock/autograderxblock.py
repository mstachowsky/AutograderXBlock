"""TO-DO: Write a description of what this XBlock is."""

#from importlib.resources import files
import pkg_resources
from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.scorable import ScorableXBlockMixin, Score
from xblock.fields import Integer, Scope, String, List, Float, Boolean
from xblockutils.settings import XBlockWithSettingsMixin #needed to enable settings
from xblockutils.studio_editable import StudioEditableXBlockMixin #needed to show the settings modal
from django.template import Context, Template
from requests.exceptions import Timeout
from submissions import api as submissions_api
import os
import requests
import json
import traceback
import re

#from openai import OpenAI

from lms.djangoapps.courseware.courses import get_course_by_id

# high_level_api.py - use this only! No more URLs or silly things

BASE_URL = "http://ece-nebula07.eng.uwaterloo.ca:8976"  # This is the stable endpoint

def generate(prompt: str, reasoning: bool = False) -> str:
    response = requests.post(f"{BASE_URL}/generate", data={"prompt": prompt, "reasoning": reasoning})
    return response.json().get("result", "No result returned")

def generate_vision(prompt: str, image_path: str, fast: bool = False) -> str:
    with open(image_path, "rb") as img:
        files = {"file": img}
        data = {"prompt": prompt, "fast": str(fast).lower()}
        response = requests.post(f"{BASE_URL}/generate_vision", data=data, files=files)
    return response.json().get("result", "No result returned")


class AutograderXBlock(XBlock,ScorableXBlockMixin,XBlockWithSettingsMixin,StudioEditableXBlockMixin): #inherit from Scorable...

    #Adding in a random string setting that does nothing at the moment
    random_string_setting = String(
    help="Model used for grading",
    default="qwen",
    scope=Scope.settings  # Change this from Scope.content to Scope.settings
    )
    
    editable_fields = ['random_string_setting']
    
    #question_description = String(default="Enter the question description here", scope=Scope.settings)
    question_description = String(
        help="Description of the question",
        default="",
        scope=Scope.content
    )
    model_name = String(
        help="Description of the question",
        default="qwen",
        scope=Scope.content
    )
    
    show_feedback = Boolean(
        help="Toggle to show or hide feedback",
        default=True,  # Set the default value (adjust as needed)
        scope=Scope.content
    )
    show_label = Boolean(
        help="Toggle to show or hide the rubric label",
        default=True,  # Set the default value (adjust as needed)
        scope=Scope.content
    )
    submitted_answer = String(default="",scope=Scope.user_state)
    answer_evaluation = String(default="",scope=Scope.user_state)
    # TO-DO: delete count, and define your own fields.
    
    raw_earned = Float(
        default=0, scope=Scope.user_state,
        help="The student score, currently an integer",
    )
    student_score = Float(
        default=0, scope=Scope.user_state,
        help="The student score, currently an integer",
    )
    
    raw_possible = Float(
        default=1, scope=Scope.content,
        help="The student max score, currently an integer",
    )
    student_attempts = Integer(
        default = 0, scope = Scope.user_state,
        help="The number of attempts the student has made at this question",
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
    
    @property
    def has_score(self):
        return True
    @staticmethod
    def needs_configuration():
        """Indicates that this XBlock has settings that should be configured in Studio."""
        return True

    def max_score(self):
        """Return the maximum score based on the highest weight in the rubric."""
        if self.rubric:
            return max(item['weight'] for item in self.rubric)
        return 0  # Default to 0 if no rubric is defined
    
    def has_submitted_answer(self):
        return self.student_attempts > 0
    
    def set_score(self, score):
        self.student_score = self.raw_earned
    
    def calculate_score(self):
        return Score(raw_earned=self.raw_earned, raw_possible=self.raw_possible)
    
    def publish_grade(self, score=None, only_if_higher=None):
        """
        Publish a grade to the runtime.
        """
        if not score:
            score = self.get_score()
 
        grade_dict = {
            "value": score.raw_earned,
            "user": self.runtime.user_id,
            "max_value": score.raw_possible,
            "only_if_higher": only_if_higher,
        }
        self.runtime.publish(self, "grade", grade_dict)
    
    def get_score(self):
        return Score(raw_earned=self.student_score, raw_possible=self.raw_possible)
    
    def render_template(self, template_path, context={}):
        template_str = self.resource_string(template_path)
        template = Template(template_str)
        return template.render(Context(context))
    
    def resource_string(self, path):
        """Helper to load a resource from the static directory."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")
    
    def studio_view(self, context):
        print("********++++++++++**********++++++++++*******")
        course = get_course_by_id(self.course_id)  # pylint: disable=no-member            
        api_key = course.other_course_settings.get("openaiApiKey")
        if api_key is not None:
            model_names = ['qwen','nemo','gpt-4o','gpt-4o-mini']
        else:
            model_names = ['qwen','nemo']
        print(course.other_course_settings.get("openaiApiKey"))
        
        html = self.render_template("static/html/grading_xblock_studio.html",{'self':self,"question":self.question_description,'model_names':model_names,'show_label':self.show_label,'show_feedback':self.show_feedback})
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
        self.model_name = data.get("model_name", "qwen")  # Default to "qwen" if not provided
        self.raw_possible = self.max_score() #update this here
        self.show_label = data.get("show_label",True)
        self.show_feedback = data.get("show_feedback",True)
        return {"result": "success"}

    def student_view(self, context):
        html = self.render_template("static/html/grading_xblock_student.html",{'self':self,'show_label':self.show_label,'show_feedback':self.show_feedback})
        frag = Fragment()
        frag.add_content(html)
        #frag = Fragment(html.format(self=self,question=self.question_description,random_thing=34))
        frag.add_css(self.resource_string("static/css/grading_xblock.css"))
        frag.add_javascript(self.resource_string("static/js/src/grading_xblock.js"))
        frag.initialize_js('GradingXBlockStudent', {
        'show_label': self.show_label,
        'show_feedback': self.show_feedback
        })
        
        return frag
        #html = self.resource_string("static/html/grading_xblock_student.html")
        #frag = Fragment(html.format(self=self))
        #frag = Fragment(html.format(self=self,question=self.question_description,random_thing=34))
        #frag.add_css(self.resource_string("static/css/grading_xblock.css"))
        #frag.add_javascript(self.resource_string("static/js/src/grading_xblock.js"))
        #frag.initialize_js('GradingXBlockStudent')
        #return frag

    @XBlock.json_handler
    def grade_submission(self, data, suffix=''):
        student_answer = data.get("student_answer", "")
        rubric = self.rubric  # Get the rubric that was saved
        rubric_string = self.format_rubric_for_grading(rubric)
        
        prompt = f"""You are helping to evaluate student work. The question you are evaluating is: {self.question_description}
        
        The rubric you are evaluating the work against is: {rubric_string}. Your job is to evaluate the student work against the rubric. You will provide a label and some feedback. It is imperative that your feedback does not contain the answer! Rather than explicitly telling the student exactly what they need to do, you should generate a small set of questions that the student can consider. Be careful to make sure that your questions don't give away the answer either - it is not OK to just rephrase the answer as a question! Remember, if they meet all of the expectations, you don't need to ask for anything else. They've done everything they had to do.
        
        You must produce two things: a label and a feedback string. The label must be exactly one of the labels supplied by the rubric. You must provide your label within <label> and </label> XML tags. The feedback must be based on the student answer and the label you chose. You must provide your feedback within <feedback> and </feedback> XML tags. 
        
        You must not produce any other output. The student work is:
        
        
        """

        # Call the external evaluation function
        evaluation_string = generate(prompt + "\n" + student_answer)
        print("============================="+evaluation_string)
        #extract the label
        label_match = re.search(r"<label>(.*?)</label>", evaluation_string)
        if label_match:
            label = label_match.group(1).strip().lower()  # Extract and convert to lower case
        else:
            # If no label is found, set a default grade or handle the error as needed
            # I strongly doubt this can happen unless the LLM goes off the rails?
            grade = 0
            return {
                "evaluation": "Hm, something went wrong. Here's what the evaluator says: " + evaluation_string
            }
            
        # Match the extracted label with the rubric
        grade = 0
        for rubric_item in rubric:
            if rubric_item['label'].lower() == label:
                grade = rubric_item['weight']
                break
        
        # Save the student's grade
        #self.runtime.publish(self, 'grade', {
        #    'value': grade,
        #    'max_value': 100,
        #})
        #print(self.state)    
        
        #Using data.get did not work twice, but I can just store the strings directly
        self.submitted_answer = student_answer#data.get("student_answer","")
        self.answer_evaluation = evaluation_string
        
        return {
            "evaluation": "GOAT!" + evaluation_string
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
