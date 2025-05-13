from sqlalchemy.orm import Session
from app.domain.models.issue import Issue

class IssueRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_issue(self, issue_data):
        issue = Issue(**issue_data)
        self.db.add(issue)
        self.db.commit()
        self.db.refresh(issue)
        return issue

    def get_issue(self, issue_id):
        return self.db.query(Issue).filter(Issue.id == issue_id).first()

    def update_issue(self, issue_id, issue_data):
        issue = self.get_issue(issue_id)
        if issue:
            for key, value in issue_data.items():
                setattr(issue, key, value)
            self.db.commit()
            self.db.refresh(issue)
        return issue

    def delete_issue(self, issue_id):
        issue = self.get_issue(issue_id)
        if issue:
            self.db.delete(issue)
            self.db.commit()
            return True
        return False

    def get_all_issues(self):
        return self.db.query(Issue).all()

    def get_issues_by_status(self, status):
        return self.db.query(Issue).filter(Issue.status == status).all()

    def get_issues_by_user(self, user_id):
        return self.db.query(Issue).filter(Issue.assigned_to_id == user_id).all()

    def assign_issue(self, issue_id, user_id):
        issue = self.get_issue(issue_id)
        if issue:
            issue.assigned_to_id = user_id
            self.db.commit()
            self.db.refresh(issue)
        return issue

    def resolve_issue(self, issue_id):
        issue = self.get_issue(issue_id)
        if issue:
            issue.status = "Resolved"
            self.db.commit()
            self.db.refresh(issue)
        return issue

    def escalate_issue(self, issue_id):
        issue = self.get_issue(issue_id)
        if issue:
            issue.status = "Escalated"
            self.db.commit()
            self.db.refresh(issue)
        return issue

    def close_issue(self, issue_id):
        issue = self.get_issue(issue_id)
        if issue:
            issue.status = "Closed"
            self.db.commit()
            self.db.refresh(issue)
        return issue

    def get_issue_history(self, issue_id):
        # Placeholder for issue history logic
        return []