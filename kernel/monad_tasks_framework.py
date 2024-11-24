# Step 1: Update the CalculationState Model to Store JSON Data

# models.py
from django.db import models
import jsonfield  # Using jsonfield package for JSON support in Django models

class CalculationState(models.Model):
    step = models.IntegerField(default=0)
    value = jsonfield.JSONField()  # Use JSONField to store the state in JSON format
    description = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Step {self.step}: {self.value} ({self.description})"

# New Model to Represent Manual Task
class ManualTask(models.Model):
    step = models.IntegerField(default=0)
    input_params = jsonfield.JSONField()  # Store input parameters, e.g., URLs of historical form contents
    form_result = jsonfield.JSONField(null=True, blank=True)  # Store the output as a JSON form
    is_completed = models.BooleanField(default=False)
    assigned_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        status = "Completed" if self.is_completed else "Pending"
        return f"Task {self.step}: {status}"

# Step 2: Update StateMonad Class to Support Manual Task Creation and Linking

# state_monad.py
from calc_app.models import CalculationState, ManualTask
from datetime import datetime

class StateMonad:
    def __init__(self, value):
        self.value = value
    
    # `bind` used to link calculations
    def bind(self, func):
        result = func(self.value)
        return StateMonad(result)
    
    # Persist current state in CalculationState
    def persist(self, description=""):
        # Get the current max step
        last_state = CalculationState.objects.order_by('-step').first()
        current_step = last_state.step + 1 if last_state else 1

        # Save new state
        state = CalculationState.objects.create(
            step=current_step,
            value=self.value,
            description=description
        )
        return state
    
    # Create manual task for human intervention
    def create_manual_task(self, input_params, description="Manual Task"):
        # Get the current max step
        last_task = ManualTask.objects.order_by('-step').first()
        current_step = last_task.step + 1 if last_task else 1

        # Save new task
        task = ManualTask.objects.create(
            step=current_step,
            input_params=input_params,
            is_completed=False
        )
        return task

# Example Function to Add Manual Task for Human Input
def add_manual_task(monad_value):
    # Assuming monad_value has relevant data to create a manual task
    input_urls = ["http://example.com/form1", "http://example.com/form2"]  # Example links
    task = monad_value.create_manual_task(input_params=input_urls, description="Review Historical Form Data")
    return task

# Step 3: Create a View to Demonstrate Manual Task Management and State Update

# views.py
from django.http import JsonResponse
from calc_app.state_monad import StateMonad, add_manual_task
from calc_app.models import ManualTask
from datetime import datetime

def calculate(request):
    # Initialize Monad with a starting value
    initial_state = StateMonad({"initial_value": 5})

    # Create a manual task for review
    task = add_manual_task(initial_state)

    # Mock completion of manual task (for illustration purposes)
    if not task.is_completed:
        # Simulate task being completed by a user
        ManualTask.objects.filter(pk=task.pk).update(
            form_result={"form_field_1": "value1", "form_field_2": "value2"},
            is_completed=True,
            completed_at=datetime.now()
        )

    # Use the result of the manual task as the new state value
    if task.is_completed:
        new_state = StateMonad(task.form_result)
        new_state.persist(description="Manual task completed and result persisted")

    # Return all states and tasks
    all_states = CalculationState.objects.all()
    all_tasks = ManualTask.objects.all()
    state_result = [{"step": s.step, "value": s.value, "description": s.description} for s in all_states]
    task_result = [{"step": t.step, "input": t.input_params, "result": t.form_result, "status": "Completed" if t.is_completed else "Pending"} for t in all_tasks]
    
    return JsonResponse({"states": state_result, "tasks": task_result}, safe=False)
