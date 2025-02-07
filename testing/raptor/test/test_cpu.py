# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from __future__ import absolute_import, unicode_literals

import mozunit
import os
import mock

from raptor import cpu
from raptor.raptor import RaptorAndroid


def test_no_device():
    raptor = RaptorAndroid('geckoview', 'org.mozilla.org.mozilla.geckoview_example',
                           cpu_test=True, no_conditioned_profile=False)
    raptor.device = None
    resp = cpu.start_android_cpu_profiler(raptor)
    assert resp is None


def test_usage_with_invalid_data_returns_zero():
    with mock.patch('mozdevice.adb.ADBDevice') as device:
        with mock.patch('raptor.raptor.RaptorControlServer') as control_server:
            # Create a device that returns invalid data
            device.shell_output.side_effect = ['8.0.0', 'geckoview']
            device._verbose = True

            # Create a control server
            control_server.cpu_test = True
            control_server.device = device
            raptor = RaptorAndroid('geckoview', 'org.mozilla.geckoview_example')
            raptor.config['cpu_test'] = True
            raptor.control_server = control_server
            raptor.device = device

            cpu_profiler = cpu.AndroidCPUProfiler(raptor)
            cpu_profiler.get_app_cpu_usage()

            # Verify the call to submit data was made
            avg_cpuinfo_data = {
                u'type': u'cpu',
                u'test': u'usage_with_invalid_data_returns_zero-avg',
                u'unit': u'%',
                u'values': {
                    u'avg': 0
                }
            }
            min_cpuinfo_data = {
                u'type': u'cpu',
                u'test': u'usage_with_invalid_data_returns_zero-min',
                u'unit': u'%',
                u'values': {
                    u'min': 0
                }
            }
            max_cpuinfo_data = {
                u'type': u'cpu',
                u'test': u'usage_with_invalid_data_returns_zero-max',
                u'unit': u'%',
                u'values': {
                    u'max': 0
                }
            }

            cpu_profiler.generate_android_cpu_profile("usage_with_invalid_data_returns_zero")
            control_server.submit_supporting_data.assert_has_calls([
                mock.call(avg_cpuinfo_data),
                mock.call(min_cpuinfo_data),
                mock.call(max_cpuinfo_data)
            ])


def test_usage_with_output():
    with mock.patch('mozdevice.adb.ADBDevice') as device:
        with mock.patch('raptor.raptor.RaptorControlServer') as control_server:
            # Override the shell output with sample CPU usage details
            filepath = os.path.abspath(os.path.dirname(__file__)) + '/files/'
            with open(filepath + 'top-info.txt', 'r') as f:
                test_data = f.read()
            device.shell_output.side_effect = ['8.0.0', test_data]
            device._verbose = True

            # Create a control server
            control_server.cpu_test = True
            control_server.test_name = 'cpuunittest'
            control_server.device = device
            control_server.app_name = 'org.mozilla.geckoview_example'
            raptor = RaptorAndroid('geckoview', 'org.mozilla.geckoview_example')
            raptor.device = device
            raptor.config['cpu_test'] = True
            raptor.control_server = control_server

            cpu_profiler = cpu.AndroidCPUProfiler(raptor)
            cpu_profiler.polls.append(cpu_profiler.get_app_cpu_usage())
            cpu_profiler.polls.append(0)

            # Verify the response contains our expected CPU % of 93.7
            avg_cpuinfo_data = {
                u'type': u'cpu',
                u'test': u'usage_with_integer_cpu_info_output-avg',
                u'unit': u'%',
                u'values': {
                    u'avg': 93.7/2
                }
            }
            min_cpuinfo_data = {
                u'type': u'cpu',
                u'test': u'usage_with_integer_cpu_info_output-min',
                u'unit': u'%',
                u'values': {
                    u'min': 0
                }
            }
            max_cpuinfo_data = {
                u'type': u'cpu',
                u'test': u'usage_with_integer_cpu_info_output-max',
                u'unit': u'%',
                u'values': {
                    u'max': 93.7
                }
            }

            cpu_profiler.generate_android_cpu_profile("usage_with_integer_cpu_info_output")
            control_server.submit_supporting_data.assert_has_calls([
                mock.call(avg_cpuinfo_data),
                mock.call(min_cpuinfo_data),
                mock.call(max_cpuinfo_data)
            ])


def test_usage_with_fallback():
    with mock.patch('mozdevice.adb.ADBDevice') as device:
        with mock.patch('raptor.raptor.RaptorControlServer') as control_server:
            device._verbose = True

            # Return what our shell call to dumpsys would give us
            shell_output = ' 31093 u0_a196  10 -10   8% S    ' + \
                '66 1392100K 137012K  fg org.mozilla.geckoview_example'

            # We set the version to be less than Android 8
            device.shell_output.side_effect = ['7.0.0', shell_output]

            # Create a control server
            control_server.cpu_test = True
            control_server.test_name = 'cpuunittest'
            control_server.device = device
            control_server.app_name = 'org.mozilla.geckoview_example'
            raptor = RaptorAndroid('geckoview', 'org.mozilla.geckoview_example')
            raptor.device = device
            raptor.config['cpu_test'] = True
            raptor.control_server = control_server

            cpu_profiler = cpu.AndroidCPUProfiler(raptor)
            cpu_profiler.polls.append(cpu_profiler.get_app_cpu_usage())
            cpu_profiler.polls.append(0)

            # Verify the response contains our expected CPU % of 8
            avg_cpuinfo_data = {
                u'type': u'cpu',
                u'test': u'usage_with_fallback-avg',
                u'unit': u'%',
                u'values': {
                    u'avg': 8/2
                }
            }
            min_cpuinfo_data = {
                u'type': u'cpu',
                u'test': u'usage_with_fallback-min',
                u'unit': u'%',
                u'values': {
                    u'min': 0
                }
            }
            max_cpuinfo_data = {
                u'type': u'cpu',
                u'test': u'usage_with_fallback-max',
                u'unit': u'%',
                u'values': {
                    u'max': 8
                }
            }

            cpu_profiler.generate_android_cpu_profile("usage_with_fallback")
            control_server.submit_supporting_data.assert_has_calls([
                mock.call(avg_cpuinfo_data),
                mock.call(min_cpuinfo_data),
                mock.call(max_cpuinfo_data)
            ])


if __name__ == '__main__':
    mozunit.main()
