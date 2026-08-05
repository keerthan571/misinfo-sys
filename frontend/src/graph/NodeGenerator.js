import {
    NODE_TYPES,
    NODE_COLORS,
    DEFAULT_NODE_DATA,
    PLATFORMS
} from "./constants";

import {
    createSeededRandom,
    generatePosition
} from "./GraphUtils";

export default class NodeGenerator {
    constructor(events, blueprint) {
        this.events = events;
        this.blueprint = blueprint;
        this.nodes = [];

        this.random = createSeededRandom(
            blueprint.metadata.seed
        );
    }
    usernames = [
        "news_today",
        "viral_feed",
        "world_report",
        "daily_update",
        "fact_watch",
        "city_alert",
        "breaking_news",
        "citizen_voice",
        "global_media",
        "trend_now",
        "headline_live",
        "media_watch",
        "public_voice",
        "buzz_daily",
        "truth_check",
        "social_news",
        "flash_report",
        "local_updates",
        "world_update",
        "news_network"
    ];
    communityNames = [
        "News Media",
        "Public Discussion",
        "Regional Community",
        "Politics",
        "Technology",
        "Healthcare",
        "Entertainment",
        "Education"
    ];
    generate() {
        this.nodes = this.events.map(event =>
            this.createNode(event)
        );
        return this.nodes;
    }

    createNode(event) {
        return {
            id: event.id,
            type: event.type,
            position: this.calculatePosition(event),
            data: {
                    ...DEFAULT_NODE_DATA,

                    id: event.id,

                    label: this.generateLabel(event),

                    displayName:
                        this.generateUsername(event.id),

                    nodeType: event.type,

                    color:
                        this.resolveColor(event.type),

                    followers:
                        event.followers,

                    formattedFollowers:
                        this.formatFollowers(event.followers),

                    influenceScore:
                        event.influence,

                    influencePercent:
                        event.influence,

                    shareProbability:
                        this.calculateShareProbability(event),

                    verified:
                        this.isVerified(event),

                    viral:
                        event.type === NODE_TYPES.CLAIM,

                    publisher:
                        event.type === NODE_TYPES.CLAIM,

                    community:
                        this.communityNames[
                            event.community %
                            this.communityNames.length
                        ],

                    reach: 0,

                    networkInfluence: 0,

                    networkInfluencePercent: 0,

                    pageRank: 0,

                    pageRankScore: 0,

                    inDegree: 0,

                    outDegree: 0,

                    degree: 0,

                    weightedReach: 0,

                    platform:
                        this.blueprint.metadata.platform ||
                        PLATFORMS.UNKNOWN,

                    parentId:
                        event.parentId,

                    level:
                        event.level,

                    createdAt:
                        this.generateTimestamp(event.level),

                    isBot:
                        event.isBot
            }
        };
    }

    calculateTrust(event) {

        if (event.isBot)
            return 20;

        if (event.type === NODE_TYPES.CLAIM)
            return 70;

        if (event.type === NODE_TYPES.INFLUENCER)
            return 90;

        return Math.min(
            85,
            40 +
            Math.round(
                event.influence / 2
            )
        );
    }

    calculatePosition(event) {
        return generatePosition(
            this.random,
            event.level,
            event.community,
            this.blueprint.layout
        );
    }

    generateLabel(event) {

        switch (event.type) {

            case NODE_TYPES.CLAIM:
                return "Original Publisher";

            case NODE_TYPES.INFLUENCER:
                return "Verified Influencer";

            case NODE_TYPES.BOT:
                return "Bot Account";

            default:
                return "Social User";
        }
    }

    calculateShareProbability(event) {

        let probability =
            this.blueprint.propagation
                .spreadProbability;

        probability +=
            event.influence / 500;

        probability +=
            Math.min(
                event.followers,
                100000
            ) / 500000;

        if (event.isBot)
            probability += 0.08;

        return Number(
            Math.min(
                1,
                probability
            ).toFixed(2)
        );
    }

    resolveColor(type) {
        switch (type) {
            case NODE_TYPES.CLAIM:
                return NODE_COLORS.claim;
            case NODE_TYPES.INFLUENCER:
                return NODE_COLORS.influencer;
            case NODE_TYPES.BOT:
                return NODE_COLORS.bot;
            default:
                return NODE_COLORS.user;
        }
    }

    isVerified(event) {
        return (
            event.type === NODE_TYPES.INFLUENCER &&
            event.followers >= 100000 &&
            event.influence >= 70
        );
    }

    generateTimestamp(level) {
        return new Date(
            Date.now() + level * 60000
        ).toISOString();
    }

    generateUsername(id) {

        const base =
            this.usernames[
                Number(
                    id.split("-")[1]
                ) % this.usernames.length
            ];

        const suffixes = [
            "",
            "_official",
            "_news",
            "_live",
            "_tv",
            "_media",
            "_network",
            "_24",
            "_global",
            "_india"
        ];

        const suffix =
            suffixes[
                Number(
                    id.split("-")[1]
                ) % suffixes.length
            ];

        return `@${base}${suffix}`;
    }

    formatFollowers(value) {

        if (value >= 1000000)
            return (
                value / 1000000
            ).toFixed(1) + "M";

        if (value >= 1000)
            return (
                value / 1000
            ).toFixed(1) + "K";

        return value.toString();
    }

    getNodes() {
        return this.nodes;
    }
}