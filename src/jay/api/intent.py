from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from jay.db import get_session
from jay.intent.schemas import (
    IntentEdgeCreate,
    IntentEdgeRead,
    IntentNodeCreate,
    IntentNodeRead,
)
from jay.intent.service import IntentService

router = APIRouter(prefix="/intent", tags=["Intent"])


@router.post("/nodes", response_model=IntentNodeRead)
def create_node(node: IntentNodeCreate, session: Session = Depends(get_session)):
    return IntentService(session).create_node(node)


@router.get("/nodes", response_model=list[IntentNodeRead])
def list_nodes(session: Session = Depends(get_session)):
    return IntentService(session).list_nodes()


@router.post("/edges", response_model=IntentEdgeRead)
def create_edge(edge: IntentEdgeCreate, session: Session = Depends(get_session)):
    return IntentService(session).create_edge(edge)


@router.get("/edges", response_model=list[IntentEdgeRead])
def list_edges(session: Session = Depends(get_session)):
    return IntentService(session).list_edges()
