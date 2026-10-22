
import React from "react";
import { BaseEdge } from "reactflow";

/**
 * Orthogonal propagation edge.
 *
 * Each edge receives a lane offset from GraphViewer.jsx.
 * Edges can share the initial segment leaving the same node,
 * then separate into individual lanes before reaching children.
 */
export default function PropagationEdge({
    id,
    sourceX,
    sourceY,
    targetX,
    targetY,
    markerEnd,
    style,
    data,
}) {
    const requestedOffset = Number(data?.laneOffset ?? 0);

    // Keep the routing lane inside the space between node columns.
    const horizontalGap = targetX - sourceX;
    const maxOffset = Math.max(0, horizontalGap / 2 - 10);

    const laneOffset = Math.max(
        -maxOffset,
        Math.min(maxOffset, requestedOffset)
    );

    const middleX =
        sourceX + horizontalGap / 2 + laneOffset;

    // Horizontal -> vertical -> horizontal: no diagonal segments.
    const edgePath = [
        `M ${sourceX} ${sourceY}`,
        `H ${middleX}`,
        `V ${targetY}`,
        `H ${targetX}`,
    ].join(" ");

    return (
        <BaseEdge
            id={id}
            path={edgePath}
            markerEnd={markerEnd}
            style={{
                ...style,
                strokeLinecap: "round",
                strokeLinejoin: "round",
            }}
        />
    );
}
