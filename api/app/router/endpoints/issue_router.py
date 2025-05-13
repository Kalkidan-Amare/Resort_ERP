from fastapi import APIRouter, Depends, HTTPException, status
from app.usecase.issue_service import IssueService, get_issue_service
from app.domain.schemas.issue import IssueInput
from typing import List

issueRouter = APIRouter()

@issueRouter.post("/issues", status_code=status.HTTP_201_CREATED)
def create_issue(issue: IssueInput, issue_service: IssueService = Depends(get_issue_service)):
    issue_data = issue.dict()
    if issue.photo:
        # Assuming photo is an image URL
        issue_data['photo'] = issue.photo
    created_issue = issue_service.create_issue(issue_data)
    return created_issue

@issueRouter.get("/issues/{issue_id}")
def get_issue(issue_id: int, issue_service: IssueService = Depends(get_issue_service)):
    issue = issue_service.get_issue(issue_id)
    if not issue:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found")
    return issue

@issueRouter.put("/issues/{issue_id}")
def update_issue(issue_id: int, issue: IssueInput, issue_service: IssueService = Depends(get_issue_service)):
    issue_data = issue.dict()
    updated_issue = issue_service.update_issue(issue_id, issue_data)
    if not updated_issue:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found")
    return updated_issue

@issueRouter.delete("/issues/{issue_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_issue(issue_id: int, issue_service: IssueService = Depends(get_issue_service)):
    deleted = issue_service.delete_issue(issue_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found")

@issueRouter.get("/issues", response_model=List[IssueInput])
def get_all_issues(issue_service: IssueService = Depends(get_issue_service)):
    return issue_service.get_all_issues()
