from sqlmodel import Session, select, or_
from fastapi import Depends, FastAPI, HTTPException, APIRouter, Form
from traceback import print_exc
from ..db import get_session
from ..schemas import Branch

branch_router = APIRouter(prefix="/branches")

@branch_router.post(path="/register-branch")
def register_branch(
    name: str = Form(...), address: str = Form(...),
    session: Session = Depends(get_session)
):
    try:
        branch = Branch(name=name, address=address)
        session.add(branch)
        session.commit()
        return {"status_code": 200, "detail": f"Branch registered successfully with ID {branch.id}"}
    except:
        raise HTTPException(status_code=500, detail="Internal Server Error")
        print_exc()
    

@branch_router.get(path="/get-branch-by-id")
def get_branch_by_id(
    id: int,
    session: Session = Depends(get_session)
) -> Branch | None:
    try:
        statement = select(Branch).where(Branch.id == id)
        result = session.exec(statement).one_or_none()
        return result
    except:
        raise HTTPException(status_code=500, detail="Internal Server Error")
        print_exc()
        

@branch_router.get(path="/list-branches")
def list_branches(
    session: Session = Depends(get_session)
):
    try:
        statement = select(Branch)
        results = session.exec(statement).all()
        return list(results)
    except:
        print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")

@branch_router.get(path="/find-branches")
def find_branches(
    name: str = "", address: str = "",
    session: Session = Depends(get_session)
):
    
    try:
        statement = select(Branch).where(
            Branch.name.like(f"%{name}%"),
            Branch.address.like(f"%{address}%")
        )
        results = session.exec(statement)
        return list(results)
    except:
        print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@branch_router.patch("/update-branch")
def update_branch(
    id: int,
    name: str | None = None,
    address: str | None = None,
    session: Session = Depends(get_session),
):
    try:
        statement = select(Branch).where(Branch.id == id)
        branch = session.exec(statement).one_or_none()

        if branch is None:
            raise HTTPException(status_code=404, detail="Branch not found")

        if name is not None:
            branch.name = name
        if address is not None:
            branch.address = address

        session.add(branch)
        session.commit()
        session.refresh(branch)

        return {
            "status_code": 200,
            "detail": "Branch updated successfully",
            "branch": branch,
        }
    except:
        print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")

@branch_router.delete(path="/unregister-branch")
def unregister_branch(
    id: int, 
    session: Session = Depends(get_session)
):
    try:
        statement = select(Branch).where(Branch.id == id)
        result = session.exec(statement).one_or_none()
        if result is None:
            raise HTTPException(status_code = 404, detail = "Brand ID not found")
        session.delete(result)
        session.commit()
        return {"status_code": 200, "detail": f"Brand with ID {id} unregistered"}
    except:
        print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")