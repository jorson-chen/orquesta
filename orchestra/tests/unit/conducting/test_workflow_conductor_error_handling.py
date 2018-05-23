# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from orchestra import conducting
from orchestra.specs import native as specs
from orchestra import states
from orchestra.tests.unit import base


class WorkflowConductorErrorHandlingTest(base.WorkflowConductorTest):

    def test_task_transition_criteria_error(self):
        wf_def = """
        version: 1.0

        description: A basic branching workflow.

        vars:
          foobar: fubar

        tasks:
          task1:
            action: core.noop
            next:
              - when: <% $.foobar.fubar %>
                publish:
                  var1: 'xyz'
                do: task2
              - when: <% succeeded() %>
                do: task3
          task2:
            action: core.noop
            next:
              - when: <% succeeded() %>
                publish:
                  var2: 123
                do: task3
          task3:
            join: all
            action: core.noop
        """

        expected_errors = [
            {
                'message': 'Unknown function "#property#fubar"',
                'task_id': 'task1',
                'task_transition_id': 'task2__0'
            }
        ]

        spec = specs.WorkflowSpec(wf_def)
        conductor = conducting.WorkflowConductor(spec)
        conductor.set_workflow_state(states.RUNNING)

        # The workflow should fail on completion of task1 while evaluating task transition.
        task_name = 'task1'
        conductor.update_task_flow(task_name, states.RUNNING)
        conductor.update_task_flow(task_name, states.SUCCEEDED)

        # The workflow should fail with the expected errors.
        self.assertEqual(conductor.get_workflow_state(), states.FAILED)
        actual_errors = sorted(conductor.errors, key=lambda x: x.get('task_id', None))
        self.assertListEqual(actual_errors, expected_errors)

        # There are two transitions in task1. The transition to task3 should be processed.
        self.assertIn('task3', conductor.flow.staged)

        # Since the workflow failed, there should be no next tasks returned.
        self.assertListEqual(conductor.get_next_tasks(), [])

    def test_multiple_task_transition_criteria_errors(self):
        wf_def = """
        version: 1.0

        description: A basic branching workflow.

        vars:
          foobar: fubar
          fubar: foobar

        tasks:
          task1:
            action: core.noop
            next:
              - when: <% $.foobar.fubar %>
                publish:
                  var1: 'xyz'
                do: task3
          task2:
            action: core.noop
            next:
              - when: <% $.fubar.foobar %>
                publish:
                  var2: 123
                do: task3
          task3:
            join: all
            action: core.noop
        """

        expected_errors = [
            {
                'message': 'Unknown function "#property#fubar"',
                'task_id': 'task1',
                'task_transition_id': 'task3__0'
            },
            {
                'message': 'Unknown function "#property#foobar"',
                'task_id': 'task2',
                'task_transition_id': 'task3__0'
            }
        ]

        spec = specs.WorkflowSpec(wf_def)
        conductor = conducting.WorkflowConductor(spec)
        conductor.set_workflow_state(states.RUNNING)

        # Manually complete task1 and task2. Although the workflow failed when
        # processing task1, task flow can still be updated for task2.
        conductor.update_task_flow('task1', states.RUNNING)
        conductor.update_task_flow('task1', states.SUCCEEDED)
        conductor.update_task_flow('task2', states.RUNNING)
        conductor.update_task_flow('task2', states.SUCCEEDED)

        # The workflow should fail with the expected errors.
        self.assertEqual(conductor.get_workflow_state(), states.FAILED)
        actual_errors = sorted(conductor.errors, key=lambda x: x.get('task_id', None))
        self.assertListEqual(actual_errors, expected_errors)

        # Since both tasks fail evaluating task transition, task3 should not be staged.
        self.assertNotIn('task3', conductor.flow.staged)

        # Since the workflow failed, there should be no next tasks returned.
        self.assertListEqual(conductor.get_next_tasks(), [])

    def test_task_transition_publish_error(self):
        wf_def = """
        version: 1.0

        description: A basic branching workflow.

        vars:
          foobar: fubar

        tasks:
          task1:
            action: core.noop
            next:
              - when: <% succeeded() %>
                publish:
                  var1: <% $.foobar.fubar %>
                do: task2
          task2:
            action: core.noop
            next:
              - when: <% succeeded() %>
                publish:
                  var2: 123
        """

        expected_errors = [
            {
                'message': 'Unknown function "#property#fubar"',
                'task_id': 'task1',
                'task_transition_id': 'task2__0'
            }
        ]

        spec = specs.WorkflowSpec(wf_def)
        conductor = conducting.WorkflowConductor(spec)
        conductor.set_workflow_state(states.RUNNING)

        # The workflow should fail on completion of task1 while evaluating task transition.
        task_name = 'task1'
        conductor.update_task_flow(task_name, states.RUNNING)
        conductor.update_task_flow(task_name, states.SUCCEEDED)

        # The workflow should fail with the expected errors.
        self.assertEqual(conductor.get_workflow_state(), states.FAILED)
        actual_errors = sorted(conductor.errors, key=lambda x: x.get('task_id', None))
        self.assertListEqual(actual_errors, expected_errors)
        self.assertNotIn('task2', conductor.flow.staged)
        self.assertListEqual(conductor.get_next_tasks(), [])

    def test_get_start_tasks_with_task_action_error(self):
        wf_def = """
        version: 1.0

        description: A basic branching workflow.

        vars:
          foobar: fubar

        tasks:
          task1:
            action: <% $.foobar.fubar %>
            next:
              - when: <% succeeded() %>
                do: task2
          task2:
            action: core.noop
        """

        expected_errors = [
            {
                'message': 'Unknown function "#property#fubar"',
                'task_id': 'task1'
            }
        ]

        spec = specs.WorkflowSpec(wf_def)
        conductor = conducting.WorkflowConductor(spec)
        conductor.set_workflow_state(states.RUNNING)

        # The get_start_tasks method should not return any tasks.
        self.assertListEqual(conductor.get_start_tasks(), [])

        # The workflow should fail with the expected errors.
        self.assertEqual(conductor.get_workflow_state(), states.FAILED)
        actual_errors = sorted(conductor.errors, key=lambda x: x.get('task_id', None))
        self.assertListEqual(actual_errors, expected_errors)

    def test_get_start_tasks_via_get_next_tasks_with_task_action_error(self):
        wf_def = """
        version: 1.0

        description: A basic branching workflow.

        vars:
          foobar: fubar

        tasks:
          task1:
            action: <% $.foobar.fubar %>
            next:
              - when: <% succeeded() %>
                do: task2
          task2:
            action: core.noop
        """

        expected_errors = [
            {
                'message': 'Unknown function "#property#fubar"',
                'task_id': 'task1'
            }
        ]

        spec = specs.WorkflowSpec(wf_def)
        conductor = conducting.WorkflowConductor(spec)
        conductor.set_workflow_state(states.RUNNING)

        # The get_next_tasks method should not return any tasks.
        self.assertListEqual(conductor.get_next_tasks(), [])

        # The workflow should fail with the expected errors.
        self.assertEqual(conductor.get_workflow_state(), states.FAILED)
        actual_errors = sorted(conductor.errors, key=lambda x: x.get('task_id', None))
        self.assertListEqual(actual_errors, expected_errors)

    def test_get_next_tasks_with_task_action_error(self):
        wf_def = """
        version: 1.0

        description: A basic branching workflow.

        vars:
          foobar: fubar

        tasks:
          task1:
            action: core.noop
            next:
              - when: <% succeeded() %>
                do: task2
          task2:
            action: <% $.foobar.fubar %>
        """

        expected_errors = [
            {
                'message': 'Unknown function "#property#fubar"',
                'task_id': 'task2'
            }
        ]

        spec = specs.WorkflowSpec(wf_def)
        conductor = conducting.WorkflowConductor(spec)
        conductor.set_workflow_state(states.RUNNING)

        # Manually complete task1.
        task_name = 'task1'
        conductor.update_task_flow(task_name, states.RUNNING)
        conductor.update_task_flow(task_name, states.SUCCEEDED)

        # The get_next_tasks method should not return any tasks.
        self.assertListEqual(conductor.get_next_tasks(), [])

        # The workflow should fail with the expected errors.
        self.assertEqual(conductor.get_workflow_state(), states.FAILED)
        actual_errors = sorted(conductor.errors, key=lambda x: x.get('task_id', None))
        self.assertListEqual(actual_errors, expected_errors)

    def test_get_start_tasks_with_task_input_error(self):
        wf_def = """
        version: 1.0

        description: A basic branching workflow.

        vars:
          foobar: fubar

        tasks:
          task1:
            action: core.noop
            input:
              var_x: <% $.foobar.fubar %>
            next:
              - when: <% succeeded() %>
                do: task2
          task2:
            action: core.noop
        """

        expected_errors = [
            {
                'message': 'Unknown function "#property#fubar"',
                'task_id': 'task1'
            }
        ]

        spec = specs.WorkflowSpec(wf_def)
        conductor = conducting.WorkflowConductor(spec)
        conductor.set_workflow_state(states.RUNNING)

        # The get_start_tasks method should not return any tasks.
        self.assertListEqual(conductor.get_start_tasks(), [])

        # The workflow should fail with the expected errors.
        self.assertEqual(conductor.get_workflow_state(), states.FAILED)
        actual_errors = sorted(conductor.errors, key=lambda x: x.get('task_id', None))
        self.assertListEqual(actual_errors, expected_errors)

    def test_get_start_tasks_via_get_next_tasks_with_task_input_error(self):
        wf_def = """
        version: 1.0

        description: A basic branching workflow.

        vars:
          foobar: fubar

        tasks:
          task1:
            action: core.noop
            input:
              var_x: <% $.foobar.fubar %>
            next:
              - when: <% succeeded() %>
                do: task2
          task2:
            action: core.noop
        """

        expected_errors = [
            {
                'message': 'Unknown function "#property#fubar"',
                'task_id': 'task1'
            }
        ]

        spec = specs.WorkflowSpec(wf_def)
        conductor = conducting.WorkflowConductor(spec)
        conductor.set_workflow_state(states.RUNNING)

        # The get_next_tasks method should not return any tasks.
        self.assertListEqual(conductor.get_next_tasks(), [])

        # The workflow should fail with the expected errors.
        self.assertEqual(conductor.get_workflow_state(), states.FAILED)
        actual_errors = sorted(conductor.errors, key=lambda x: x.get('task_id', None))
        self.assertListEqual(actual_errors, expected_errors)

    def test_get_next_tasks_with_task_input_error(self):
        wf_def = """
        version: 1.0

        description: A basic branching workflow.

        vars:
          foobar: fubar

        tasks:
          task1:
            action: core.noop
            next:
              - when: <% succeeded() %>
                do: task2
          task2:
            action: core.noop
            input:
              var_x: <% $.foobar.fubar %>
        """

        expected_errors = [
            {
                'message': 'Unknown function "#property#fubar"',
                'task_id': 'task2'
            }
        ]

        spec = specs.WorkflowSpec(wf_def)
        conductor = conducting.WorkflowConductor(spec)
        conductor.set_workflow_state(states.RUNNING)

        # Manually complete task1.
        task_name = 'task1'
        conductor.update_task_flow(task_name, states.RUNNING)
        conductor.update_task_flow(task_name, states.SUCCEEDED)

        # The get_next_tasks method should not return any tasks.
        self.assertListEqual(conductor.get_next_tasks(), [])

        # The workflow should fail with the expected errors.
        self.assertEqual(conductor.get_workflow_state(), states.FAILED)
        actual_errors = sorted(conductor.errors, key=lambda x: x.get('task_id', None))
        self.assertListEqual(actual_errors, expected_errors)

    def test_get_start_tasks_with_multiple_task_action_and_input_errors(self):
        wf_def = """
        version: 1.0

        description: A basic branching workflow.

        vars:
          foobar: fubar
          fubar: foobar

        tasks:
          task1:
            action: <% $.foobar.fubar %>
            next:
              - when: <% succeeded() %>
                do: task3
          task2:
            action: core.noop var_x=<% $.fubar.foobar %>
            next:
              - when: <% succeeded() %>
                do: task3
          task3:
            join: all
            action: core.noop
        """

        expected_errors = [
            {
                'message': 'Unknown function "#property#fubar"',
                'task_id': 'task1'
            },
            {
                'message': 'Unknown function "#property#foobar"',
                'task_id': 'task2'
            }
        ]

        spec = specs.WorkflowSpec(wf_def)
        conductor = conducting.WorkflowConductor(spec)
        conductor.set_workflow_state(states.RUNNING)

        # The get_start_tasks method should not return any tasks.
        self.assertListEqual(conductor.get_start_tasks(), [])

        # The workflow should fail with the expected errors.
        self.assertEqual(conductor.get_workflow_state(), states.FAILED)
        actual_errors = sorted(conductor.errors, key=lambda x: x.get('task_id', None))
        self.assertListEqual(actual_errors, expected_errors)

    def test_get_start_tasks_via_get_next_tasks_with_multiple_task_action_and_input_errors(self):
        wf_def = """
        version: 1.0

        description: A basic branching workflow.

        vars:
          foobar: fubar
          fubar: foobar

        tasks:
          task1:
            action: <% $.foobar.fubar %>
            next:
              - when: <% succeeded() %>
                do: task3
          task2:
            action: core.noop var_x=<% $.fubar.foobar %>
            next:
              - when: <% succeeded() %>
                do: task3
          task3:
            join: all
            action: core.noop
        """

        expected_errors = [
            {
                'message': 'Unknown function "#property#fubar"',
                'task_id': 'task1'
            },
            {
                'message': 'Unknown function "#property#foobar"',
                'task_id': 'task2'
            }
        ]

        spec = specs.WorkflowSpec(wf_def)
        conductor = conducting.WorkflowConductor(spec)
        conductor.set_workflow_state(states.RUNNING)

        # The get_next_tasks method should not return any tasks.
        self.assertListEqual(conductor.get_next_tasks(), [])

        # The workflow should fail with the expected errors.
        self.assertEqual(conductor.get_workflow_state(), states.FAILED)
        actual_errors = sorted(conductor.errors, key=lambda x: x.get('task_id', None))
        self.assertListEqual(actual_errors, expected_errors)

    def test_get_next_tasks_with_multiple_task_action_and_input_errors(self):
        wf_def = """
        version: 1.0

        description: A basic branching workflow.

        vars:
          foobar: fubar
          fubar: foobar

        tasks:
          task1:
            action: core.noop
            next:
              - when: <% succeeded() %>
                do: task2, task3
          task2:
            action: <% $.foobar.fubar %>
          task3:
            action: core.noop var_x=<% $.fubar.foobar %>
        """

        expected_errors = [
            {
                'message': 'Unknown function "#property#fubar"',
                'task_id': 'task2'
            },
            {
                'message': 'Unknown function "#property#foobar"',
                'task_id': 'task3'
            }
        ]

        spec = specs.WorkflowSpec(wf_def)
        conductor = conducting.WorkflowConductor(spec)
        conductor.set_workflow_state(states.RUNNING)

        # Manually complete task1.
        task_name = 'task1'
        conductor.update_task_flow(task_name, states.RUNNING)
        conductor.update_task_flow(task_name, states.SUCCEEDED)

        # The get_next_tasks method should not return any tasks.
        self.assertListEqual(conductor.get_next_tasks(), [])

        # The workflow should fail with the expected errors.
        self.assertEqual(conductor.get_workflow_state(), states.FAILED)
        actual_errors = sorted(conductor.errors, key=lambda x: x.get('task_id', None))
        self.assertListEqual(actual_errors, expected_errors)