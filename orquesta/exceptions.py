# Copyright 2019 Extreme Networks, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging


LOG = logging.getLogger(__name__)


class PluginFactoryError(Exception):
    pass


class ExpressionGrammarException(Exception):
    pass


class ExpressionEvaluationException(Exception):
    pass


class VariableUndefinedError(Exception):

    def __init__(self, var):
        message = 'The variable "%s" is undefined.' % var
        super(VariableUndefinedError, self).__init__(message)


class VariableInaccessibleError(Exception):

    def __init__(self, var):
        message = 'The variable "%s" is for internal use and inaccessible.' % var
        super(VariableInaccessibleError, self).__init__(message)


class SchemaDefinitionError(Exception):
    pass


class SchemaIncompatibleError(Exception):
    pass


class InvalidTask(Exception):

    def __init__(self, task_id):
        message = 'Task "%s" does not exist.' % task_id
        super(InvalidTask, self).__init__(message)


class InvalidTaskTransition(Exception):

    def __init__(self, src, dest):
        message = 'Task transition from "%s" to "%s" does not exist.' % (src, dest)
        super(InvalidTaskTransition, self).__init__(message)


class AmbiguousTaskTransition(Exception):

    def __init__(self, src, dest):
        message = 'More than one task transitions found from "%s" to "%s".' % (src, dest)
        Exception.__init__(self, message)


class InvalidEventType(Exception):

    def __init__(self, type_name, event_name):
        message = 'Event type "%s" with event "%s" is not valid.' % (type_name, event_name)
        Exception.__init__(self, message)


class InvalidEvent(Exception):

    def __init__(self, value):
        message = 'Event "%s" is not valid.' % value
        super(InvalidEvent, self).__init__(message)


class InvalidStatus(Exception):

    def __init__(self, value):
        message = 'Status "%s" is not valid.' % value
        super(InvalidStatus, self).__init__(message)


class InvalidStatusTransition(Exception):

    def __init__(self, old, new):
        message = 'Status transition from "%s" to "%s" is invalid.' % (old, new)
        super(InvalidStatusTransition, self).__init__(message)


class InvalidTaskStatusTransition(Exception):

    def __init__(self, status, event):
        message = 'Unable to process event "%s" for task in "%s" status.' % (event, status)
        super(InvalidTaskStatusTransition, self).__init__(message)


class InvalidWorkflowStatusTransition(Exception):

    def __init__(self, status, event):
        message = 'Unable to process event "%s" for workflow in "%s" status.' % (event, status)
        super(InvalidWorkflowStatusTransition, self).__init__(message)


class InvalidTaskStateEntry(Exception):

    def __init__(self, task_id):
        message = 'Task "%s" is not staged or has not started yet.' % task_id
        super(InvalidTaskStateEntry, self).__init__(message)


class WorkflowInspectionError(Exception):

    def __init__(self, errors):
        message = 'Workflow definition failed inspection.'
        super(WorkflowInspectionError, self).__init__(message, errors)


class WorkflowContextError(Exception):
    pass


class WorkflowLogEntryError(Exception):
    pass


class WorkflowIsActiveAndNotRerunableError(Exception):

    def __init__(self):
        message = 'Unable to rerun workflow because it is not in a completed state.'
        super(WorkflowIsActiveAndNotRerunableError, self).__init__(message)


class InvalidTaskRerunRequest(Exception):

    def __init__(self, tasks):
        tasks_str = ''

        for task in tasks:
            tasks_str += ', ' if tasks_str else ''
            tasks_str += '%s|%s' % (task.task_id, task.route)

        message = "Unable to rerun task|route(s) because it doesn't exist or isn't rerunnable: %s"
        super(InvalidTaskRerunRequest, self).__init__(message % tasks_str)
