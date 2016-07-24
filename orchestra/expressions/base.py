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

import abc
import logging
import six


LOG = logging.getLogger(__name__)


@six.add_metaclass(abc.ABCMeta)
class Evaluator(object):

    @classmethod
    @abc.abstractmethod
    def strip_delimiter(cls, expr):
        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    def validate(cls, expr):
        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    def evaluate(cls, text, data=None):
        raise NotImplementedError()