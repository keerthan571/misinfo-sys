import { Handle, Position } from "reactflow";
import "./GraphNode.css";

const ICONS = {
    claim: "📢",
    origin: "📢",
    influencer: "⭐",
    media: "📰",
    user: "👤",
    bot: "🤖"
};

export default function GraphNode({ data }) {

    const {
        label,
        displayName,
        nodeType,
        followers,
        formattedFollowers,
        influenceScore,
        networkInfluencePercent,
        verified,
        community,
        reach,
        isBot
    } = data;

    const icon =
        ICONS[nodeType] ||
        ICONS.user;

    return (
        <>
            <Handle
                type="target"
                position={Position.Top}
            />

            <div
                className={`graph-node ${nodeType} ${
                    verified ? "verified-node" : ""
                } ${
                    isBot ? "bot-node" : ""
                }`}
            >
                <div className="graph-node-header">

                    <span className="graph-node-icon">
                        {icon}
                    </span>

                    <div className="graph-node-heading">

                        <div className="graph-node-title">
                            {label}
                        </div>

                        <div className="graph-node-subtitle">
                            {displayName}
                        </div>

                    </div>

                    {verified && (
                        <span className="verified">
                            ✔
                        </span>
                    )}

                </div>

                <div className="graph-node-body">

                    <div className="metric">
                        <span>👥 Followers</span>
                        <strong>
                            {formattedFollowers || followers}
                        </strong>
                    </div>

                    <div className="metric">
                        <span>⭐ Influence</span>
                        <strong>
                            {Math.round(
                                networkInfluencePercent ??
                                influenceScore
                            )}
                            %
                        </strong>
                    </div>

                    <div className="metric">
                        <span>🌐 Reach</span>
                        <strong>
                            {reach ?? 0}
                        </strong>
                    </div>

                    <div className="metric">
                        <span>🏷 Community</span>
                        <strong>
                            {community}
                        </strong>
                    </div>

                </div>
            </div>

            <Handle
                type="source"
                position={Position.Bottom}
            />
        </>
    );
}