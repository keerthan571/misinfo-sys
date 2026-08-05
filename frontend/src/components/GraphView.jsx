import ReactFlow, {
    Background,
    Controls,
    MiniMap
} from "reactflow";

import "reactflow/dist/style.css";
import "./GraphView.css";

export default function GraphView({
    nodes,
    edges,
    nodeTypes,
    edgeTypes,
    onNodeClick
}) {

    return (

        <div className="graph-view">

            <ReactFlow
                nodes={nodes}
                edges={edges}
                nodeTypes={nodeTypes}
                edgeTypes={edgeTypes}
                onNodeClick={onNodeClick}
                fitView
                fitViewOptions={{
                    padding: 0.2
                }}
                minZoom={0.25}
                maxZoom={2}
                defaultViewport={{
                    x: 0,
                    y: 0,
                    zoom: 1
                }}
                proOptions={{
                    hideAttribution: true
                }}
            >

                <MiniMap
                    pannable
                    zoomable
                    nodeStrokeWidth={3}
                />

                <Controls
                    showInteractive={false}
                />

                <Background
                    gap={24}
                    size={1}
                />

            </ReactFlow>

        </div>

    );

}