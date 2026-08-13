from typing import List, Optional
from pydantic import BaseModel, Field

class CanvasNode(BaseModel):
    id: str = Field(description="Unique node identifier, e.g., 'node-prob', 'node-sol', 'node-member-1'")
    type: str = Field(description="Type of node: 'problem', 'solution', 'tech_stack', 'roadmap', or 'member_task'")
    label: str = Field(description="Title/summary displayed on the node card")
    description: str = Field(description="Detailed explanation of this node's task or function")
    x: int = Field(description="X position coordinate on the visual canvas")
    y: int = Field(description="Y position coordinate on the visual canvas")
    icon: str = Field(description="Emoji or icon representing the node (e.g., '🎯', '💡', '🤖', '⚡')")
    assigned_role: Optional[str] = Field(
        default="Unassigned",
        description="Assigned member or role (e.g., 'Member 1 (ML)', 'Member 5 (DevOps)', 'Solo Developer')"
    )

class CanvasEdge(BaseModel):
    id: str = Field(description="Unique edge ID, e.g., 'edge-prob-sol'")
    source: str = Field(description="Source node ID")
    target: str = Field(description="Target node ID")
    label: Optional[str] = Field(default="", description="Optional label for the edge connection")

class ExtractedStudentProfile(BaseModel):
    is_team: bool = Field(default=False, description="True if team size is 2 or more")
    team_size: int = Field(default=1, description="Exact number of members in the team (1 for solo, N for teams)")
    academic_field: Optional[str] = Field(default=None, description="Student major or domain")
    interests: Optional[str] = Field(default=None, description="Target problem domains or technical interests")
    tech_level: Optional[str] = Field(default=None, description="Technical experience level")
    team_members: Optional[List[str]] = Field(
        default=[],
        description="List describing roles/skills for each member (length equal to team_size)"
    )

class NexusCanvasProjectSpec(BaseModel):
    project_title: str = Field(description="Catchy, high-impact hackathon project name")
    tagline: str = Field(description="One-line pitch of the solution")
    target_problem: str = Field(description="Core problem statement being solved")
    suggested_tech_stack: List[str] = Field(description="List of key frameworks, APIs, and libraries")
    nodes: List[CanvasNode] = Field(description="List of visual canvas nodes scaled to team_size")
    edges: List[CanvasEdge] = Field(description="List of directional connecting edges")