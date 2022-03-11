from theblockchainapi.resource import APIResource
from typing import List, Optional
import requests
import platform
import time
from enum import Enum


class Type(Enum):

    BOOL = 'boolean'
    ARRAY = 'array'
    NUMBER = 'number'
    STRING = 'string'


class Specification:

    def __init__(
        self,
        type_: Type,
        name: str,
        description: str,
        required: bool
    ):
        self.type_ = type_
        self.name = name
        self.description = description
        self.required = required

    def get_dict(self):
        return {
            'type': self.type_.value,
            'name': self.name,
            'description': self.description,
            'required': self.required
        }


class Group:

    def __init__(
        self,
        section_name: str,
        group_name: str,
        group_description: str
    ):
        self.section_name = section_name
        self.group_name = group_name
        self.group_description = group_description

    def get_dict(self):
        return {
            'section_name': self.section_name,
            'group_name': self.group_name,
            'group_description': self.group_description
        }


class DeveloperProgramResource(APIResource):

    ACCEPTED_PLATFORMS = ['Darwin', 'Windows', 'Linux']
    ACCEPTED_ARCHITECTURES = ['64bit']

    def __modify_project(
        self,
        project_id: Optional[str],
        project_name: str,
        project_description: str,
        contact_email: str,
        groups: Optional[List[Group]]
    ):
        payload = {
            'project_name': project_name,
            'project_description': project_description,
            'contact_email': contact_email,
            'groups': []
        }
        for group in groups:
            payload['groups'].append(group.get_dict())
        if project_id is not None:
            payload['project_id'] = project_id
        response = self._request(
            payload=payload,
            endpoint="project" if project_id is None else f"project/{project_id}",
            request_method=self._RequestMethod.POST
        )
        if 'error_message' in response:
            raise Exception(response['error_message'])
        return response

    def create_project(
        self,
        project_name: str,
        project_description: str,
        contact_email: str,
        groups: Optional[List[Group]]
    ):
        """
        More info available here: https://docs.blockchainapi.com/#operation/createProject

        :param project_name:
        :param project_description:
        :param contact_email:
        :param groups:
        :return:
        """
        return self.__modify_project(None, project_name, project_description, contact_email, groups)

    def update_project(
        self,
        project_id: str,
        project_name: str,
        project_description: str,
        contact_email: str,
        groups: Optional[List[Group]]
    ):
        """
        More info available here: https://docs.blockchainapi.com/#operation/updateProject

        :param project_id:
        :param project_name:
        :param project_description:
        :param contact_email:
        :param groups:
        :return:
        """
        return self.__modify_project(project_id, project_name, project_description, contact_email, groups)

    def get_project(self, project_id: str):
        """
        More info available here: https://docs.blockchainapi.com/#operation/getProject

        :param project_id:
        :return:
        """
        response = self._request(
            payload=dict(), endpoint=f"project/{project_id}", request_method=self._RequestMethod.GET
        )
        if 'error_message' in response:
            raise Exception(response['error_message'])
        return response

    def delete_project(self, project_id: str):
        """
        More info available here: https://docs.blockchainapi.com/#operation/deleteProject
        :param project_id:
        :return:
        """
        response = self._request(
            payload=dict(), endpoint=f"project/{project_id}", request_method=self._RequestMethod.DELETE
        )
        if 'error_message' in response:
            raise Exception(response['error_message'])
        return response

    def create_project_version(self, project_id: str, version: str):
        """
        More info available here: https://docs.blockchainapi.com/#operation/createProjectVersion

        :param project_id:
        :param version:
        :return:
        """
        response = self._request(
            payload=dict(), endpoint=f"project/{project_id}/{version}", request_method=self._RequestMethod.POST
        )
        if 'error_message' in response:
            raise Exception(response['error_message'])
        return response

    def delete_project_version(self, project_id: str, version: str):
        """
        More info available here: https://docs.blockchainapi.com/#operation/deleteProjectVersion

        :param project_id:
        :param version:
        :return:
        """
        response = self._request(
            payload=dict(), endpoint=f"project/{project_id}/{version}", request_method=self._RequestMethod.DELETE
        )
        if 'error_message' in response:
            raise Exception(response['error_message'])
        return response

    def deploy_project(self, project_id: str, binary_file_path: str):
        """
        More info available here: https://docs.blockchainapi.com/#operation/deployProject

        :param project_id:
        :param binary_file_path:
        :return:
        """
        if platform.system() not in DeveloperProgramResource.ACCEPTED_PLATFORMS:
            raise Exception(
                f"Your current system is not supported. We currently only support the following platforms: "
                f"{','.join(DeveloperProgramResource.ACCEPTED_PLATFORMS)}. We detected that you're using the platform "
                f"{platform.system()}. If you want support for this platform, please contact us."
            )
        arch = platform.architecture()[0]
        if arch not in DeveloperProgramResource.ACCEPTED_ARCHITECTURES:
            raise Exception(
                f"Your current architecture is not supported. We currently only support the following architectures: "
                f"{','.join(DeveloperProgramResource.ACCEPTED_ARCHITECTURES)}. "
                f"We detected that you're using the architecture "
                f"{arch}. If you want support for this platform, please contact us."
            )

        response = self._request(
            payload={
                'platform': platform.system()
            },
            endpoint=f"project/{project_id}/deploy/url",
            request_method=self._RequestMethod.POST
        )

        def upload(result_: dict):

            fields = result_['fields']
            url = result_['url']

            # Upload
            files = {
                'file': open(binary_file_path, 'rb')
            }
            print("Uploading...")
            r = requests.post(
                url,
                data=fields,
                files=files
            )
            if r.status_code == 204:
                print("Upload successful. Now monitoring for successful deployment...")
            else:
                raise Exception("Upload failed... Please report this issue to our team so we can help.\n\n", r.text)

            # Check status
            while True:
                status_ = self.get_project_deployment_status(project_id)
                print(status_['status'])
                if status_['status_code'] == 1:
                    break
                else:
                    print(f"Checking... ")
                    time.sleep(5)
            return status_

        if 'error_message' in response:
            raise Exception(response['error_message'])

        status = upload(response)

        return status

    def get_project_deployment_status(self, project_id: str):
        """
        More info available here: https://docs.blockchainapi.com/#operation/deployProject

        :param project_id:
        :return:
        """

        response = self._request(
            payload=dict(),
            endpoint=f"project/{project_id}/deploy/status",
            request_method=self._RequestMethod.POST
        )
        if 'error_message' in response:
            raise Exception(response['error_message'])
        return response

    def get_project_stats(self, project_id: str):
        """
        More info available here: https://docs.blockchainapi.com/#operation/getProjectStats

        :param project_id:
        :return:
        """
        response = self._request(
            payload=dict(), endpoint=f"project/{project_id}/stats", request_method=self._RequestMethod.GET
        )
        if 'error_message' in response:
            raise Exception(response['error_message'])
        return response

    def list_projects(self):
        """
        More info available here: https://docs.blockchainapi.com/#operation/listProjects

        :return:
        """
        response = self._request(
            payload=dict(), endpoint=f"project/list", request_method=self._RequestMethod.GET)
        if 'error_message' in response:
            raise Exception(response['error_message'])
        return response

    def update_project_documentation(self, project_id: str, version: str):
        """
        More info available here: https://docs.blockchainapi.com/#operation/updateProjectDocumentation

        :param project_id:
        :param version:
        :return:
        """
        response = self._request(
            payload=dict(),
            endpoint=f"project/{project_id}/{version}/documentation",
            request_method=self._RequestMethod.POST
        )
        if 'error_message' in response:
            raise Exception(response['error_message'])
        return response

    def set_endpoint(
        self,
        project_id: str,
        version: str,
        path: str,
        readable_name: str,
        operation_id: str,
        summary: Optional[str],
        description: Optional[str],
        credits_: int,
        group_name: Optional[str],
        input_specification: List[Specification],
        input_examples: List[dict],
        output_specification: List[Specification],
        output_examples: List[dict]
    ):
        """
        More info available here: https://docs.blockchainapi.com/#operation/setEndpoint

        :param project_id:
        :param version:
        :param path:
        :param readable_name:
        :param operation_id:
        :param summary:
        :param description:
        :param credits_:
        :param group_name:
        :param input_specification:
        :param input_examples:
        :param output_specification:
        :param output_examples:
        :return:
        """
        payload = {
            'project_id': project_id,
            'version': version,
            'path': path,
            'readable_name': readable_name,
            'operation_id': operation_id,
            'description': description,
            'credits': credits_,
            'group_name': group_name,
            'input_specification': [],
            'input_examples': input_examples,
            'output_specification': [],
            'output_examples': output_examples
        }
        if summary is not None:
            payload['summary'] = summary
        if description is not None:
            payload['description'] = description
        if group_name is not None:
            payload['group_name'] = group_name
        for spec in input_specification:
            payload['input_specification'].append(spec.get_dict())
        for spec in output_specification:
            payload['output_specification'].append(spec.get_dict())
        response = self._request(
            payload=payload,
            endpoint=f"endpoint",
            request_method=self._RequestMethod.POST
        )
        if 'error_message' in response:
            raise Exception(response['error_message'])
        return response

    def get_endpoint(
        self,
        project_id: str,
        version: str,
        path: str
    ):
        """
        More info available here: https://docs.blockchainapi.com/#operation/getEndpoint

        :param project_id:
        :param version:
        :param path:
        :return:
        """
        payload = {
            'project_id': project_id,
            'version': version,
            'path': path
        }
        response = self._request(
            payload=payload,
            endpoint=f"endpoint/metadata",
            request_method=self._RequestMethod.POST
        )
        if 'error_message' in response:
            raise Exception(response['error_message'])
        return response

    def delete_endpoint(
        self,
        project_id: str,
        version: str,
        path: str
    ):
        """
        More info available here: https://docs.blockchainapi.com/#operation/deleteEndpoint

        :param project_id:
        :param version:
        :param path:
        :return:
        """
        payload = {
            'project_id': project_id,
            'version': version,
            'path': path
        }
        response = self._request(
            payload=payload,
            endpoint=f"endpoint/delete",
            request_method=self._RequestMethod.POST
        )
        if 'error_message' in response:
            raise Exception(response['error_message'])
        return response

    def list_endpoints(self):
        """
        More info available here: https://docs.blockchainapi.com/#operation/listEndpoints

        :return:
        """
        response = self._request(
            payload=dict(),
            endpoint=f"endpoint/list",
            request_method=self._RequestMethod.GET
        )
        if 'error_message' in response:
            raise Exception(response['error_message'])
        return response
