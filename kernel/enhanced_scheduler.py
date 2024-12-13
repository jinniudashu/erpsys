"""
Enhanced Django Service Scheduler with improved state management, error handling, and logging.
This is an alternative implementation that can be tested alongside the original scheduler.py.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib import messages
from django.contrib.auth.signals import user_logged_in
from django.forms.models import model_to_dict
from django.utils import timezone
from django.conf import settings
from django.db import transaction
from django.core.exceptions import ValidationError

from datetime import timedelta
from typing import Dict, Any, Optional, List
import logging
import traceback

from kernel.signals import process_terminated_signal, ux_input_signal
from kernel.models import Process, Service, ServiceRule, Operator
from kernel.process_state import ProcessState, ProcessContext
from kernel.sys_lib import sys_call

logger = logging.getLogger(__name__)

class RuleEvaluator:
    """Handles service rule evaluation and execution"""
    
    def evaluate_rules(self, process: Process, context: Optional[ProcessContext] = None):
        """
        Evaluate and execute service rules for a process
        This is the core scheduling logic similar to the original scheduler
        """
        try:
            # Build execution context
            exec_context = self._build_execution_context(process, context)
            
            # Get and execute service rules
            rules = ServiceRule.objects.filter(service=process.service)
            for rule in rules:
                logger.info(f"Checking service rule: {rule}")
                logger.info(f"Rule expression: {rule.event.expression}")
                logger.debug(f"Context: {exec_context}")
                
                if self._evaluate_rule_condition(rule, exec_context):
                    logger.info(f"Rule matched - Service: {rule.service}, Event: {rule.event}")
                    self._execute_rule_action(rule, exec_context)
                    
        except Exception as e:
            logger.error(f"Error evaluating rules for process {process.id}: {str(e)}")
            logger.error(traceback.format_exc())
            if context:
                context.transition_to(ProcessState.ERROR, str(e))
            raise
            
    def _build_execution_context(self, process: Process, context: Optional[ProcessContext] = None) -> dict:
        """Build the execution context for rule evaluation"""
        # Start with process data
        exec_context = model_to_dict(process)
        
        # Add content object data if exists
        if process.form_content_object:
            exec_context.update(model_to_dict(process.form_content_object))
            
        # Add various contexts
        if process.control_context:
            exec_context.update(process.control_context)
        if process.schedule_context:
            exec_context.update(process.schedule_context)
            
        # Add required context variables
        exec_context.update({
            "process": process,
            "instance": process,
            "customer": process.entity_content_object,
            "created": False,
            "timezone_now": timezone.now()
        })
        
        # Add context state if available
        if context:
            exec_context.update({
                "state": context.state,
                "local_vars": context.local_vars
            })
            
        return exec_context
        
    def _evaluate_rule_condition(self, rule: ServiceRule, context: dict) -> bool:
        """Evaluate a rule's condition"""
        try:
            return eval(rule.event.expression, {}, context)
        except Exception as e:
            logger.error(f"Error evaluating rule {rule.id} condition: {str(e)}")
            return False
            
    def _execute_rule_action(self, rule: ServiceRule, context: dict):
        """Execute a rule's action"""
        try:
            if rule.system_instruction:
                context['sys_call_operand'] = rule.operand_service
                sys_call(rule.system_instruction.sys_call, **context)
        except Exception as e:
            logger.error(f"Error executing rule {rule.id} action: {str(e)}")
            raise

class EnhancedProcessScheduler:
    """Enhanced process scheduler with improved state management"""
    
    def __init__(self):
        self.active_processes: Dict[int, ProcessContext] = {}
        self.rule_evaluator = RuleEvaluator()
        
    def schedule_process(self, process: Process, priority: Optional[int] = None) -> ProcessContext:
        """Schedule a process for execution with optional priority override"""
        try:
            # Create or get process context
            context = self._get_or_create_context(process, priority)
            
            # Validate process can be scheduled
            if not self._can_schedule(context):
                logger.warning(f"Process {process.id} cannot be scheduled in state {context.state}")
                return context
                
            # Transition to READY state
            if context.transition_to(ProcessState.READY):
                self._handle_ready_process(context)
            
            return context
            
        except Exception as e:
            logger.error(f"Error scheduling process {process.id}: {str(e)}")
            logger.error(traceback.format_exc())
            raise
            
    def _get_or_create_context(self, process: Process, priority: Optional[int] = None) -> ProcessContext:
        """Get existing context or create new one"""
        if process.id in self.active_processes:
            context = self.active_processes[process.id]
            if priority is not None:
                context.priority = priority
            return context
            
        context = ProcessContext(
            process_id=process.id,
            state=ProcessState.NEW,
            priority=priority if priority is not None else process.priority
        )
        self.active_processes[process.id] = context
        return context
        
    def _can_schedule(self, context: ProcessContext) -> bool:
        """Check if process can be scheduled"""
        return (
            context.state in {ProcessState.NEW, ProcessState.READY, ProcessState.WAITING} and
            not context.has_timed_out()
        )
        
    def _handle_ready_process(self, context: ProcessContext):
        """Handle process that is ready for execution"""
        try:
            # Transition to RUNNING
            if not context.transition_to(ProcessState.RUNNING):
                return
                
            # Execute process
            self._execute_process(context)
            
        except Exception as e:
            logger.error(f"Error executing process {context.process_id}: {str(e)}")
            context.transition_to(ProcessState.ERROR, str(e))
            
    def _execute_process(self, context: ProcessContext):
        """Execute the process based on its service rules"""
        try:
            process = Process.objects.get(id=context.process_id)
            
            # Evaluate and execute rules
            self.rule_evaluator.evaluate_rules(process, context)
            
            # Mark as terminated if successful
            if context.state == ProcessState.RUNNING:
                context.transition_to(ProcessState.TERMINATED)
                
        except Process.DoesNotExist:
            logger.error(f"Process {context.process_id} not found")
            context.transition_to(ProcessState.ERROR, "Process not found")
            
        except Exception as e:
            logger.error(f"Error in process execution: {str(e)}")
            context.transition_to(ProcessState.ERROR, str(e))

# Alternative signal handlers with enhanced functionality
def enhanced_user_login(sender, user, request, **kwargs):
    """Enhanced handler for user login"""
    if request.path == f'/{settings.CUSTOMER_SITE_NAME}/login/':
        try:
            with transaction.atomic():
                operator = Operator.objects.get(user=user)
                process = Process.objects.create(
                    service=Service.objects.get(name='user_login'),
                    entity_content_object=operator,
                    operator=operator,
                    state=ProcessState.NEW.name,
                    priority=0
                )
                
                # Schedule the login process
                scheduler = EnhancedProcessScheduler()
                scheduler.schedule_process(process)
                
        except Exception as e:
            logger.error(f"Error handling user login: {str(e)}")
            logger.error(traceback.format_exc())

def enhanced_process_save(sender, instance: Process, created: bool, **kwargs):
    """Enhanced handler for process save"""
    try:
        if created or instance.state == ProcessState.READY.name:
            scheduler = EnhancedProcessScheduler()
            scheduler.schedule_process(instance)
    except Exception as e:
        logger.error(f"Error handling process save: {str(e)}")
        logger.error(traceback.format_exc())

def enhanced_user_input(sender, process: Process, input_data: Dict[str, Any], **kwargs):
    """Enhanced handler for user input"""
    try:
        scheduler = EnhancedProcessScheduler()
        context = scheduler._get_or_create_context(process)
        
        # Update local variables with input data
        context.local_vars.update(input_data)
        
        # Transition from WAITING to READY
        if context.state == ProcessState.WAITING:
            scheduler.schedule_process(process)
            
    except Exception as e:
        logger.error(f"Error handling user input: {str(e)}")
        logger.error(traceback.format_exc())

def enhanced_timer_schedule(**kwargs):
    """Enhanced handler for timer-based scheduling"""
    try:
        scheduler = EnhancedProcessScheduler()
        rules = ServiceRule.objects.filter(event__is_timer=True)
        
        for rule in rules:
            # Create timer process if needed
            process = Process.objects.create(
                service=rule.service,
                state=ProcessState.NEW.name,
                priority=0,
                schedule_context={'timer_rule': rule.id}
            )
            
            # Schedule with low priority
            scheduler.schedule_process(process, priority=-1)
            
    except Exception as e:
        logger.error(f"Error in timer scheduling: {str(e)}")
        logger.error(traceback.format_exc())

# Example usage:
"""
To use the enhanced scheduler instead of the original one:

1. Import the enhanced scheduler:
from kernel.enhanced_scheduler import EnhancedProcessScheduler, enhanced_user_login

2. Replace the original signal handlers:
@receiver(user_logged_in)
def on_user_login(sender, user, request, **kwargs):
    return enhanced_user_login(sender, user, request, **kwargs)

3. Or use it directly in your code:
scheduler = EnhancedProcessScheduler()
scheduler.schedule_process(process)
"""
