import os
import requests
import json
import utils
import logging
from clients.github_client import GitHubClient
from repositories.git_repository import GitRepositoryInterface


class GitHubGitRepository(GitRepositoryInterface):
    
    MAX_DESCR_LENGTH = 140

    def __init__(self):
        self.gitops_repo_name = utils.getenv("GITHUB_GITOPS_REPO_NAME") #gitops-manifests
        self.github_client = GitHubClient()
        self.headers = self.github_client.get_rest_api_headers()
        self.rest_api_url = self.github_client.get_rest_api_url()

    def post_commit_status(self, commit_status):
        url = f'{self.rest_api_url}/{self.gitops_repo_name}/statuses/{commit_status.commit_id}'

        github_state = self._map_to_github_state(commit_status.state)
        message = commit_status.message
        if len(message) > self.MAX_DESCR_LENGTH:
            message = message[:self.MAX_DESCR_LENGTH]
        # data = {'state': github_state, 'description': commit_status.status_name + ": " + commit_status.message, 'context': commit_status.genre }
        data = {
            'state': github_state,
            'description': message,
            'context': commit_status.status_name
            }
        logging.info(f'Url {url}: Headers {self.headers}: Data {data}')
        response = requests.post(url=url, headers=self.headers, json=data)
        # Throw appropriate exception if request failed
        response.raise_for_status()

    def _map_to_github_state(self, reason): 
        state_map = {
            "Suspended": "error",
            "ReconciliationSucceeded": "success",
            "ReconciliationFailed": "failure",
            "Progressing": "pending",
            "DependencyNotReady": "error",
            "PruneFailed": "failure",
            "ArtifactFailed": "failure",
            "BuildFailed": "failure",
            "HealthCheckFailed": "failure",
            "ValidationFailed": "failure",
            "NotApplicable": "success",
            "info": "pending",
            "error": "failure",

            "Succeeded": "success",
            "Failed": "failure",
            "Error": "error",
            "Inconclusive": "pending",
            "Running": "pending",
            "OutOfSync": "pending",
            "Synced": "success",
            "Unknown": "success",
            "Progressing": "pending",
            "Degraded": "error",
            "Healthy": "success",
            "Missing": "failure"

        }
        return state_map[reason]        
    
    
    def get_pr_num(self, commit_id) -> str:
        pass
    
    def get_pr_metadata(self, commit_id):
        pass
    
    def get_pull_request(self, pr_num):
        pass

    def get_prs(self, pr_status):
        pass

    # def get_pr_metadata(self, pr_num):
    #     # https://docs.microsoft.com/en-us/rest/api/azure/devops/git/pull%20request%20properties/list?view=azure-devops-rest-6.0
    #     url = f'{self.pr_repository_api}/pullRequests/{pr_num}/properties?api-version=6.0-preview'

    #     response = requests.get(url=url, headers=self.headers)
    #     # Throw appropriate exception if request failed
    #     response.raise_for_status()

    #     # Navigate the properties response structure
    #     result = response.json()
    #     if (result['count'] > 0):
    #         properties = result['value']
    #         entry = properties.get(PR_METADATA_KEY)
    #         if entry:
    #             # At this point, we have the original JSON string we stored.
    #             return json.loads(entry['$value'])
    #     return None

    # def get_pull_request(self, pr_num):
    #     url = f'{self.pr_repository_api}/pullRequests/{pr_num}?api-version=6.1-preview.1'
    #     response = requests.get(url=url, headers=self.headers)
    #     # Throw appropriate exception if request failed
    #     response.raise_for_status()
    #     pr = json.loads(response.content)
    #     return pr

    # # Returns an array of PR dictionaries with an optional status filter
    # # pr_status values: https://docs.microsoft.com/en-us/rest/api/azure/devops/git/pull%20requests/get%20pull%20requests?view=azure-devops-rest-6.0#pullrequeststatus
    # def get_prs(self, pr_status):
    #     pr_status_param = ''
    #     if pr_status:
    #         pr_status_param = f'searchCriteria.status={pr_status}&'
    #     url = f'{self.pr_repository_api}/pullRequests?{pr_status_param}api-version=6.0'
    #     response = requests.get(url=url, headers=self.headers)
    #     # Throw appropriate exception if request failed
    #     response.raise_for_status()

    #     pr_response = json.loads(response.content)
    #     if pr_response['count'] == 0:
    #         return None

    #     return pr_response['value']

    # def _map_to_azdo_status(self, status):
    #     status_map = {
    #         "Succeeded": "succeeded",
    #         "Failed": "failed",
    #         "Error": "error",
    #         "Inconclusive": "pending",
    #         "Running": "pending",
    #         "OutOfSync": "pending",
    #         "Synced": "succeeded",
    #         "Unknown": "notApplicable",
    #         "Progressing": "pending",
    #         "Degraded": "error",
    #         "Healthy": "succeeded",
    #         "Missing": "failed",

    #         "Suspended": "error",
    #         "ReconciliationSucceeded": "succeeded",
    #         "ReconciliationFailed": "failed",
    #         "DependencyNotReady": "error",
    #         "PruneFailed": "failed",
    #         "ArtifactFailed": "failed",
    #         "BuildFailed": "failed",
    #         "HealthCheckFailed": "failed",
    #         "ValidationFailed": "failed",
    #         "NotApplicable": "notApplicable",
    #         "info": "pending",
    #         "error": "failed"
    #     }
    #     return status_map[status]

    # def get_pr_num(self, commit_id) -> str:
    #     url = f'{self.repository_api}/commits/{commit_id}?api-version=6.0'

    #     response = requests.get(url=url, headers=self.headers)
    #     # Throw appropriate exception if request failed
    #     response.raise_for_status()

    #     commit = response.json()
    #     comment = commit['comment']
    #     MERGED_PR = "Merged PR "
    #     pr_num = None
    #     if MERGED_PR in comment:
    #         merged_pr_index = comment.index(MERGED_PR)
    #         pr_num = comment[merged_pr_index + len(MERGED_PR): comment.index(":", merged_pr_index)]
    #     return pr_num
