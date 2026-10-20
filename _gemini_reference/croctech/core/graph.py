"""
Topological Stitch Graph & Directed Acyclic Graph (DAG) for Crochet.
Represents every stitch as a discrete node with parent/child dependencies,
tracking exact yarn flow, loop connections, and spatial coordinates.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Set
from croctech.core.types import StitchType, LoopTarget


@dataclass
class StitchNode:
    """Discrete stitch node within the topological graph."""
    node_id: str                 # e.g., "R2_S3"
    stitch_type: StitchType
    round_index: int
    stitch_index_in_round: int
    parent_node_ids: List[str] = field(default_factory=list) # Base stitches consumed
    child_node_ids: List[str] = field(default_factory=list)  # Stitches built on top
    loop_target: LoopTarget = LoopTarget.BOTH
    color: str = "default"
    x_mm: float = 0.0
    y_mm: float = 0.0
    z_mm: float = 0.0
    is_join_stitch: bool = False   # True for slip stitch joins or height chains


class StitchGraph:
    """Topological graph maintaining all stitches, connections, and validation checks."""

    def __init__(self):
        self.nodes: Dict[str, StitchNode] = {}
        self.rounds: Dict[int, List[str]] = {} # round_index -> list of node_ids

    def add_stitch(self, node: StitchNode) -> None:
        """Register a stitch node in the graph."""
        self.nodes[node.node_id] = node
        if node.round_index not in self.rounds:
            self.rounds[node.round_index] = []
        self.rounds[node.round_index].append(node.node_id)

        # Wire up child references in parents
        for p_id in node.parent_node_ids:
            if p_id in self.nodes:
                self.nodes[p_id].child_node_ids.append(node.node_id)

    def get_round_nodes(self, round_index: int) -> List[StitchNode]:
        """Return all stitch nodes in a specific round."""
        node_ids = self.rounds.get(round_index, [])
        return [self.nodes[nid] for nid in node_ids]

    def get_active_body_stitches(self, round_index: int) -> List[StitchNode]:
        """Return only stitches that count towards pattern stitch count (excluding join sl_st and turn ch)."""
        return [node for node in self.get_round_nodes(round_index) if not node.is_join_stitch]

    def validate_stitch_conservation(self, round_index: int) -> Tuple[bool, str, Dict[str, int]]:
        """
        Verify that round_index consumes exactly the stitches provided by round_index - 1.
        Returns: (is_valid, diagnostic_message, counts)
        """
        if round_index <= 1:
            return True, "Foundation round", {}

        prev_nodes = self.get_active_body_stitches(round_index - 1)
        curr_nodes = self.get_active_body_stitches(round_index)

        consumed_parent_ids: Set[str] = set()
        consumed_count = 0
        produced_count = len(curr_nodes)

        for curr in curr_nodes:
            for p_id in curr.parent_node_ids:
                consumed_parent_ids.add(p_id)
                consumed_count += 1

        prev_count = len(prev_nodes)
        unique_parents_used = len(consumed_parent_ids)

        if unique_parents_used != prev_count:
            return (
                False,
                f"Round {round_index} used {unique_parents_used} distinct stitches from Round {round_index - 1}, but expected {prev_count}.",
                {"prev_count": prev_count, "unique_consumed": unique_parents_used, "produced": produced_count}
            )

        return (
            True,
            f"Round {round_index} correctly conserved all {prev_count} stitches of previous round.",
            {"prev_count": prev_count, "unique_consumed": unique_parents_used, "produced": produced_count}
        )

    def total_stitch_count(self) -> int:
        """Total number of stitches in graph."""
        return len(self.nodes)

