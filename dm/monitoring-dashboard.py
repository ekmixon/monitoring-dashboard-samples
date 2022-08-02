# Copyright 2020 Google Inc. All rights reserved.
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
"""
    Creates a Cloud Monitoring Dashboard from a local configuration file
"""

import json
import uuid
import re


def create_dashboard_resource(context):
    """ Creates the Cloud Monitoring Dashboard resource. """
    properties = context.properties
    project_id = properties.get("project", context.env["project"])
    dash_name = f"projects/{project_id}/dashboards/{uuid.uuid4()}"
    parent = f"projects/{project_id}"
    config_file = properties.get("config_file")

    # Read the dashboard json file. Fix potential trailing comma errors
    with open(config_file, "r") as fh:
        json_file = fh.read()
        data = json.loads(re.sub(r"}\s*\,\s*}", "}}", json_file))

    props = {
        "parent": parent,
        "name": dash_name,
    }
    props |= data

    # The type provider 'monitoring-dashboardv1type' needs to be created first!
    # The discovery API: https://monitoring.googleapis.com/$discovery/rest?version=v1
    dashboard_config = [
        {
            "action": f"{project_id}/monitoring-dashboardv1type:monitoring.projects.dashboards.create",
            "metadata": {"runtimePolicy": ["CREATE"]},
            "name": f'{context.env["name"]}-create',
            "properties": props,
        },
        {
            "action": f"{project_id}/monitoring-dashboardv1type:monitoring.projects.dashboards.delete",
            "metadata": {"runtimePolicy": ["DELETE"]},
            "name": f'{context.env["name"]}-delete',
            "properties": {"name": dash_name},
        },
    ]


    return (
        dashboard_config,
        [{"name": "project_id", "value": context.properties["projectId"]}],
    )


def generate_config(context):
    """ Entry point for the deployment resources. """

    resources, outputs = create_dashboard_resource(context)

    return {"resources": resources, "outputs": outputs}
