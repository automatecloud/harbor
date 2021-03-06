# -*- coding: utf-8 -*-

import base
import swagger_client
from swagger_client.rest import ApiException

def is_member_exist_in_project(members, member_user_name, expected_member_role_id = None):
    result = False
    for member in members:
        if member.entity_name == member_user_name:
            if expected_member_role_id != None:
                if member.role_id == expected_member_role_id:
                    return True
            else:
                return True
    return result

class Project(base.Base):
    def create_project(self, name=None, metadata=None, expect_status_code = 201, expect_response_body = None, **kwargs):
        if name is None:
            name = base._random_name("project")
        if metadata is None:
            metadata = {}
        client = self._get_client(**kwargs)

        try:
            _, status_code, header = client.projects_post_with_http_info(swagger_client.ProjectReq(name, metadata))
        except ApiException as e:
            base._assert_status_code(expect_status_code, e.status)
            if expect_response_body is not None:
                base._assert_status_body(expect_response_body, e.body)
            return
        base._assert_status_code(expect_status_code, status_code)
        base._assert_status_code(201, status_code)
        return base._get_id_from_header(header), name

    def get_projects(self, params, **kwargs):
        client = self._get_client(**kwargs)
        data = []
        data, status_code, _ = client.projects_get_with_http_info(**params)
        base._assert_status_code(200, status_code)
        return data

    def projects_should_exist(self, params, expected_count = None, expected_project_id = None, **kwargs):
        project_data = self.get_projects(params, **kwargs)
        actual_count = len(project_data)
        if expected_count is not None and actual_count!= expected_count:
            raise Exception(r"Private project count should be {}.".format(expected_count))
        if expected_project_id is not None and actual_count == 1 and str(project_data[0].project_id) != str(expected_project_id):
            raise Exception(r"Project-id check failed, expect {} but got {}, please check this test case.".format(str(expected_project_id), str(project_data[0].project_id)))

    def check_project_name_exist(self, name=None, **kwargs):
        client = self._get_client(**kwargs)
        _, status_code, _ = client.projects_head_with_http_info(name)
        return {
            200: True,
            404: False,
        }.get(status_code,'error')

    def get_project(self, project_id, expect_status_code = 200, expect_response_body = None, **kwargs):
        client = self._get_client(**kwargs)
        try:
            data, status_code, _ = client.projects_project_id_get_with_http_info(project_id)
        except ApiException as e:
            base._assert_status_code(expect_status_code, e.status)
            if expect_response_body is not None:
                base._assert_status_body(expect_response_body, e.body)
            return

        base._assert_status_code(expect_status_code, status_code)
        base._assert_status_code(200, status_code)
        return data

    def update_project(self, project_id, metadata, **kwargs):
        client = self._get_client(**kwargs)
        project = swagger_client.Project(project_id, None, None, None, None, None, None, None, None, None, None, metadata)
        _, status_code, _ = client.projects_project_id_put_with_http_info(project_id, project)
        base._assert_status_code(200, status_code)

    def delete_project(self, project_id, expect_status_code = 200, **kwargs):
        client = self._get_client(**kwargs)
        _, status_code, _ = client.projects_project_id_delete_with_http_info(project_id)
        base._assert_status_code(expect_status_code, status_code)

    def get_project_metadata_by_name(self, project_id, meta_name, expect_status_code = 200, **kwargs):
        client = self._get_client(**kwargs)
        ProjectMetadata = swagger_client.ProjectMetadata()
        ProjectMetadata, status_code, _ = client.projects_project_id_metadatas_meta_name_get_with_http_info(project_id, meta_name)
        base._assert_status_code(expect_status_code, status_code)
        return {
            'public': ProjectMetadata.public,
            'enable_content_trust': ProjectMetadata.enable_content_trust,
            'prevent_vul': ProjectMetadata.prevent_vul,
            'auto_scan': ProjectMetadata.auto_scan,
            'severity': ProjectMetadata.severity,
        }.get(meta_name,'error')

    def get_project_log(self, project_id, expect_status_code = 200, **kwargs):
        client = self._get_client(**kwargs)
        body, status_code, _ = client.projects_project_id_logs_get_with_http_info(project_id)
        base._assert_status_code(expect_status_code, status_code)
        return body

    def filter_project_logs(self, project_id, operator, repository, tag, operation_type, **kwargs):
        access_logs = self.get_project_log(project_id, **kwargs)
        count = 0
        for each_access_log in list(access_logs):
            if each_access_log.username == operator and \
               each_access_log.repo_name.strip(r'/') == repository and \
               each_access_log.repo_tag == tag and \
               each_access_log.operation == operation_type:
                count = count + 1
        return count

    def get_project_members(self, project_id, **kwargs):
        client = self._get_client(**kwargs)
        return client.projects_project_id_members_get(project_id)

    def get_project_member(self, project_id, member_id, expect_status_code = 200, expect_response_body = None, **kwargs):
        client = self._get_client(**kwargs)
        data = []
        try:
            data, status_code, _ = client.projects_project_id_members_mid_get_with_http_info(project_id, member_id,)
        except ApiException as e:
            base._assert_status_code(expect_status_code, e.status)
            if expect_response_body is not None:
                base._assert_status_body(expect_response_body, e.body)
            return

        base._assert_status_code(expect_status_code, status_code)
        base._assert_status_code(200, status_code)
        return data

    def check_project_member_not_exist(self, project_id, member_user_name, **kwargs):
        members = self.get_project_members(project_id, **kwargs)
        result = is_member_exist_in_project(list(members), member_user_name)
        if result == True:
            raise Exception(r"User {} should not be a member of project with ID {}.".format(member_user_name, project_id))

    def check_project_members_exist(self, project_id, member_user_name, expected_member_role_id = None, **kwargs):
        members = self.get_project_members(project_id, **kwargs)
        result = is_member_exist_in_project(members, member_user_name, expected_member_role_id = expected_member_role_id)
        if result == False:
            raise Exception(r"User {} should be a member of project with ID {}.".format(member_user_name, project_id))

    def update_project_member_role(self, project_id, member_id, member_role_id, expect_status_code = 200, **kwargs):
        client = self._get_client(**kwargs)
        role = swagger_client.Role(role_id = member_role_id)
        data = []
        data, status_code, _ = client.projects_project_id_members_mid_put_with_http_info(project_id, member_id, role = role)
        base._assert_status_code(expect_status_code, status_code)
        base._assert_status_code(200, status_code)
        return data

    def delete_project_member(self, project_id, member_id, expect_status_code = 200, **kwargs):
        client = self._get_client(**kwargs)
        _, status_code, _ = client.projects_project_id_members_mid_delete_with_http_info(project_id, member_id)
        base._assert_status_code(expect_status_code, status_code)
        base._assert_status_code(200, status_code)

    def add_project_members(self, project_id, user_id, member_role_id = None, expect_status_code = 201, **kwargs):
        if member_role_id is None:
            member_role_id = 1
        _member_user = {"user_id": int(user_id)}
        projectMember = swagger_client.ProjectMember(member_role_id, member_user = _member_user)
        client = self._get_client(**kwargs)
        data = []
        data, status_code, header = client.projects_project_id_members_post_with_http_info(project_id, project_member = projectMember)
        base._assert_status_code(expect_status_code, status_code)
        return base._get_id_from_header(header)

    def add_project_robot_account(self, project_id, project_name, robot_name = None, robot_desc = None, has_pull_right = True,  has_push_right = True,  expect_status_code = 201, **kwargs):
        if robot_name is None:
            robot_name = base._random_name("robot")
        if robot_desc is None:
            robot_desc = base._random_name("robot_desc")
        if has_pull_right is False and has_push_right is False:
            has_pull_right = True
        access_list = []
        resource_by_project_id = "/project/"+str(project_id)+"/repository"
        resource_by_project_name = "/project/"+project_name+"/repository"
        action_pull = "pull"
        action_push = "push"
        if has_pull_right is True:
            robotAccountAccess = swagger_client.RobotAccountAccess(resource = resource_by_project_id, action = action_pull)
            access_list.append(robotAccountAccess)
            robotAccountAccess = swagger_client.RobotAccountAccess(resource = resource_by_project_name, action = action_pull)
            access_list.append(robotAccountAccess)
        if has_push_right is True:
            robotAccountAccess = swagger_client.RobotAccountAccess(resource = resource_by_project_id, action = action_push)
            access_list.append(robotAccountAccess)
            robotAccountAccess = swagger_client.RobotAccountAccess(resource = resource_by_project_name, action = action_push)
            access_list.append(robotAccountAccess)
        robotAccountCreate = swagger_client.RobotAccountCreate(robot_name, robot_desc, access_list)
        client = self._get_client(**kwargs)
        data = []
        data, status_code, header = client.projects_project_id_robots_post_with_http_info(project_id, robotAccountCreate)
        base._assert_status_code(expect_status_code, status_code)
        base._assert_status_code(201, status_code)
        return base._get_id_from_header(header), data

    def get_project_robot_account_by_id(self, project_id, robot_id, **kwargs):
        client = self._get_client(**kwargs)
        data, status_code, _ = client.projects_project_id_robots_robot_id_get_with_http_info(project_id, robot_id)
        return data

    def disable_project_robot_account(self, project_id, robot_id, disable,  expect_status_code = 200, **kwargs):
        client = self._get_client(**kwargs)
        robotAccountUpdate = swagger_client.RobotAccountUpdate(disable)
        _, status_code, _ = client.projects_project_id_robots_robot_id_put_with_http_info(project_id, robot_id, robotAccountUpdate)
        base._assert_status_code(expect_status_code, status_code)
        base._assert_status_code(200, status_code)

    def delete_project_robot_account(self, project_id, robot_id, expect_status_code = 200, **kwargs):
        client = self._get_client(**kwargs)
        _, status_code, _ = client.projects_project_id_robots_robot_id_delete_with_http_info(project_id, robot_id)
        base._assert_status_code(expect_status_code, status_code)
        base._assert_status_code(200, status_code)