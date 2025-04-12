

class IssueService:
    def __init__(self, issue_repository):
        self.issue_repository = issue_repository

    def create_issue(self, issue_data):
        # Validate and process the issue data
        return self.issue_repository.create_issue(issue_data)

    def get_issue(self, issue_id):
        return self.issue_repository.get_issue(issue_id)

    def update_issue(self, issue_id, issue_data):
        return self.issue_repository.update_issue(issue_id, issue_data)

    def delete_issue(self, issue_id):
        return self.issue_repository.delete_issue(issue_id)
    def get_all_issues(self):
        return self.issue_repository.get_all_issues()
    def get_issues_by_status(self, status):
        return self.issue_repository.get_issues_by_status(status)
    def get_issues_by_user(self, user_id):
        return self.issue_repository.get_issues_by_user(user_id)
    def assign_issue(self, issue_id, user_id):
        return self.issue_repository.assign_issue(issue_id, user_id)
    def resolve_issue(self, issue_id):
        return self.issue_repository.resolve_issue(issue_id)
    def escalate_issue(self, issue_id):
        return self.issue_repository.escalate_issue(issue_id)
    def close_issue(self, issue_id):
        return self.issue_repository.close_issue(issue_id)
    def get_issue_history(self, issue_id):
        return self.issue_repository.get_issue_history(issue_id)

def get_issue_service(issue_repository):
    return IssueService(issue_repository)