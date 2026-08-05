import BranchAllocator from "./BranchAllocator";
import PropagationPolicy from "./PropagationPolicy";


class SeededRandom {
    constructor(seed = "default") {
        this.seed = this.hash(seed);
    }

    hash(seed) {
        let hash = 0;

        for (let i = 0; i < seed.length; i++) {
            hash = ((hash << 5) - hash) + seed.charCodeAt(i);
            hash |= 0;
        }

        return Math.abs(hash);
    }

    next() {
        this.seed =
            (this.seed * 1664525 + 1013904223) % 4294967296;

        return this.seed / 4294967296;
    }

    integer(min, max) {
        return Math.floor(
            this.next() * (max - min + 1)
        ) + min;
    }

    chance(probability) {
        return this.next() <= probability;
    }
}

export default class PropagationSimulator {
    constructor(parameters) {
        this.parameters = parameters;
        this.graph = parameters.graph;
        this.composition = parameters.composition;
        this.simulation = parameters.simulation;
        this.followers = parameters.followers;
        this.initialInfluence = parameters.initialInfluence;
        this.metadata = parameters.metadata;

        this.random = new SeededRandom(this.metadata.seed);

        this.events = [];
        this.nodeCounter = 0;
        this.communityCounter = 0;
        this.branchAllocator =
            new BranchAllocator(
                this.simulation,
                this.random
            );
    }

    createEvent({
        parentId = null,
        level = 0,
        type = "user",
        community = 0,
        isBot = false,
        followers = 0,
        influence = 0
    }) {
        const id = `${type}-${this.nodeCounter++}`;

        return {
            id,
            parentId,
            level,
            type,
            community,
            isBot,
            followers,
            influence,
            children: []
        };
    }

    createClaim() {
        const event = this.createEvent({
            type: "claim",
            level: 0,
            followers: this.randomFollowers("influencer"),
            influence: this.initialInfluence.maximum
        });

        this.events.push(event);

        return event;
    }

    randomFollowers(type) {
        const range = this.followers[type];

        return this.random.integer(
            range.min,
            range.max
        );
    }

    randomInfluence(base = 50) {
        const variation = this.random.integer(-10, 10);

        return Math.max(
            1,
            Math.min(100, base + variation)
        );
    }

    addChild(parent, child) {
        parent.children.push(child.id);
        this.events.push(child);
    }
    createInfluencers(claim) {
        const influencers = [];

        for (let i = 0; i < this.composition.influencers; i++) {
            const event = this.createEvent({
                parentId: claim.id,
                level: 1,
                type: "influencer",
                community:
                    this.random.integer(
                        0,
                        this.composition.communities - 1
                    ),
                followers: this.randomFollowers("influencer"),
                influence: this.randomInfluence(this.initialInfluence.average)
            });

            this.addChild(claim, event);
            influencers.push(event);
        }

        return influencers;
    }

    createUsers(parent, count) {
        const users = [];

        for (let i = 0; i < count; i++) {

            const decay =
                0.78 +
                this.random.next() * 0.15;

            const event =
                this.createEvent({

                    parentId: parent.id,

                    level: parent.level + 1,

                    type: "user",

                    community: parent.community,

                    followers:
                        this.randomFollowers("user"),

                    influence:
                        Math.max(
                            5,
                            Math.round(
                                parent.influence * decay
                            )
                        )

                });

            this.addChild(parent, event);

            users.push(event);
        }

        return users;
    }

    promoteInfluencer(user) {
        user.type = "influencer";
        user.followers = this.randomFollowers("influencer");
        user.influence = Math.max(
            user.influence,
            this.random.integer(55,85)
        );
    }

    injectBots(parent, count) {
        const bots = [];

        for (let i = 0; i < count; i++) {
            const event = this.createEvent({
                parentId: parent.id,
                level: parent.level + 1,
                type: "bot",
                community: parent.community,
                isBot: true,
                followers: this.randomFollowers("bot"),
                influence: this.randomInfluence(30)
            });

            this.addChild(parent, event);
            bots.push(event);
        }

        return bots;
    }

    assignCommunity(parent) {

        if (
            this.random.chance(
                this.simulation.communitySpread
            )
        ) {
            return parent.community;
        }

        this.communityCounter++;

        return this.random.integer(
            0,
            this.composition.communities - 1
        );
    }

    propagate(queue) {
        while (
            queue.length &&
            this.events.length < this.graph.totalNodes
        ) {
            const parent =
                queue.shift();

            if (!parent)
                continue;

            if (parent.level >= this.graph.depth) {
                continue;
            }

            const remaining =
                this.graph.totalNodes -
                this.events.length;

            let children =
                this.branchAllocator.allocate(
                    parent,
                    remaining
                );

            children = Math.min(
                children,
                remaining
            );

            if (children === 0) {
                continue;
            }

            const users =
                this.createUsers(
                    parent,
                    children
                );

            for (const user of users) {

                user.community =
                    this.assignCommunity(parent);

                if (
                    parent.type === "user" &&
                    user.influence >= 25 &&
                    this.random.chance(
                        PropagationPolicy.influencerPromotionChance()
                    )
                ) {
                    this.promoteInfluencer(user);
                }

                queue.push(user);
            }

            if (
                parent.level < this.graph.depth - 2 &&
                this.random.chance(
                    PropagationPolicy.botInjectionChance(
                        this.simulation.botProbability
                    )
                ) &&
                this.events.length < this.graph.totalNodes
            ) {
                const bots =
                    this.injectBots(
                        parent,
                        1
                    );

                for (const bot of bots) {
                    queue.push(bot);
                }
            }
        }
        if (import.meta.env.DEV) {
            console.log(
                "Queue Finished:",
                queue.length
            );
        }
    } 
    

    simulateInfluencers(claim) {
        const influencers =
            this.createInfluencers(claim);

        const queue = [...influencers];

        this.propagate(queue);
    }
    validate() {
        if (
            import.meta.env.DEV
        ) {
            console.log(
                "generated events:",
                this.events.length
            );
        }
        if (!this.events.length) {
            throw new Error("Propagation simulation produced no events.");
        }

        if (this.events.length > this.graph.totalNodes) {
            this.events = this.events.slice(0, this.graph.totalNodes);
        }
        return this.events;
    }

    simulate() {

        const claim =
            this.createClaim();

        this.simulateInfluencers(
            claim
        );

        return this.validate();
    }
}
