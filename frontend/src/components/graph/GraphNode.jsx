
import { Handle, Position } from "reactflow";
import "./GraphNode.css";

const ICONS = {
    claim: "📢",
    origin: "📢",
    influencer: "⭐",
    media: "📰",
    user: "👤",
    bot: "🤖",
    source: "📢"
};

export default function GraphNode({ data = {} }) {
    const {
        label,
        displayName,
        nodeType,
        followers,
        formattedFollowers,
        influenceScore,
        networkInfluencePercent,
        verified
    } = data;

    const type = String(nodeType || "user").toLowerCase();
    const icon = ICONS[type] || ICONS.user;

    const isSource = ["claim", "origin", "source"].includes(type);

    // Resolve the displayed name without duplicating prefixes.
    const rawName = String(displayName || label || "Unknown").trim();

    const cleanName = rawName
        .replace(/^(simulated|source)\s*:\s*/i, "")
        .trim();

    const isInfluencer = [
    "influencer",
    "micro_influencer",
    "micro influencer",
    "community_leader",
    "community leader"
].includes(type.replace(/-/g, "_"));

const nodeName = isSource
    ? `Source: ${cleanName}`
    : isInfluencer
        ? `Simulated Influencer ${cleanName}`
        : `Simulated: ${cleanName}`;

    // Prefer network influence when available.
    const influence = networkInfluencePercent ?? influenceScore;
    const numericInfluence = Number(influence);

    // Preserve compact formatting such as 37.7K when provided.
    const numericFollowers =
        followers !== null &&
        followers !== undefined &&
        followers !== "" &&
        Number.isFinite(Number(followers))
            ? Number(followers)
            : null;

    const followerValue =
        formattedFollowers !== null &&
        formattedFollowers !== undefined &&
        formattedFollowers !== ""
            ? formattedFollowers
            : numericFollowers !== null
                ? numericFollowers.toLocaleString()
                : "N/A";

    return (
        <>
            <Handle
                type="target"
                position={Position.Top}
            />

            <div
                className={`graph-node ${type} ${
                    verified ? "verified-node" : ""
                }`}
            >
                <div className="graph-node-header">
                    <span
                        className="graph-node-icon"
                        aria-hidden="true"
                    >
                        {icon}
                    </span>

                    <div className="graph-node-heading">
                        <div
                            className="graph-node-title"
                            title={nodeName}
                        >
                            {nodeName}
                        </div>
                    </div>

                    {verified && (
                        <span
                            className="verified"
                            title="Verified"
                        >
                            ✔
                        </span>
                    )}
                </div>

                <div className="graph-node-body">
                    <div className="metric">
                        <span className="metric-label">
                            <span aria-hidden="true">👥</span>
                            Followers
                        </span>

                        <strong>{followerValue}</strong>
                    </div>

                    <div className="metric">
                        <span className="metric-label">
                            <span aria-hidden="true">⭐</span>
                            Influence
                        </span>

                        <strong>
                            {influence !== null &&
                            influence !== undefined &&
                            influence !== "" &&
                            Number.isFinite(numericInfluence)
                                ? `${Math.round(numericInfluence)}%`
                                : "N/A"}
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
