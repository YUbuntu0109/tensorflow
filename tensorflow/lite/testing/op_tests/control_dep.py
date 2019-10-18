# Copyright 2019 The TensorFlow Authors. All Rights Reserved.
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
# ==============================================================================
"""Test configs for control_dep."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf
from tensorflow.lite.testing.zip_test_utils import create_tensor_data
from tensorflow.lite.testing.zip_test_utils import ExtraTocoOptions
from tensorflow.lite.testing.zip_test_utils import make_zip_of_tests
from tensorflow.lite.testing.zip_test_utils import register_make_test_function

TEST_INPUT_DEPTH = 3


@register_make_test_function()
def make_control_dep_tests(options):
  """Make a set of tests that use control dependencies."""

  test_parameters = [{
      "input_shape": [[], [1, 1, 1, 1], [1, 15, 14, 1], [3, 15, 14, 3]],
  }]

  def build_graph(parameters):
    input_tensor = tf.placeholder(
        dtype=tf.float32, name="input", shape=parameters["input_shape"])
    filter_value = tf.zeros((3, 3, TEST_INPUT_DEPTH, 8), tf.float32)
    assert_op = tf.assert_greater_equal(input_tensor, input_tensor - 1)
    with tf.control_dependencies([assert_op]):
      out = tf.nn.conv2d(
          input_tensor, filter_value, strides=(1, 1, 1, 1), padding="SAME")
      return [input_tensor], [out]

  def build_inputs(parameters, sess, inputs, outputs):
    input_values = create_tensor_data(tf.float32, parameters["input_shape"])
    return [input_values], sess.run(
        outputs, feed_dict=dict(zip(inputs, [input_values])))

  extra_toco_options = ExtraTocoOptions()
  extra_toco_options.drop_control_dependency = True
  make_zip_of_tests(
      options,
      test_parameters,
      build_graph,
      build_inputs,
      extra_toco_options,
      expected_tf_failures=3)
