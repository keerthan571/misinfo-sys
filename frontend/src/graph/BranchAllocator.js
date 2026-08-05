import PropagationPolicy from "./PropagationPolicy";

export default class BranchAllocator {

    constructor(simulation, random) {
        this.simulation = simulation;
        this.random = random;
    }

    allocate(parent, remaining) {

        let children = 0;

        switch (parent.type) {

            case "claim":

                children = 1;

                break;

            case "influencer":

                if (parent.influence >= 70) {

                    children =
                        this.random.chance(0.70)
                            ? 4
                            : 3;

                } else if (parent.influence >= 50) {

                    children =
                        this.random.chance(0.60)
                            ? 3
                            : 2;

                } else {

                    children = 2;

                }

                break;

            case "bot":

                children =
                    this.random.chance(0.60)
                        ? 2
                        : 1;

                break;

            case "user":

                if (parent.influence >= 35) {

                    children =
                        this.random.chance(0.65)
                            ? 3
                            : 2;

                } else if (parent.influence >= 20) {

                    children =
                        this.random.chance(0.55)
                            ? 2
                            : 1;

                } else if (parent.influence >= 10) {

                    children =
                        this.random.chance(0.40)
                            ? 1
                            : 0;

                } else {

                    children = 0;

                }

                break;

            default:

                children = 0;
        }

        return Math.min(
            children,
            remaining
        );
    }

    allocateUserChildren(parent) {

        const influence =
            parent.influence;

        const probability =
            this.simulation.spreadProbability;

        const decay =
            this.simulation.cascadeDecay;

        if (influence >= 60) {
            return this.random.chance(
                0.70 * (1 - decay)
            ) ? 3 : 2;
        }

        if (influence >= 40) {
            return this.random.chance(
                0.60 * probability
            ) ? 2 : 1;
        }

        if (influence >= 20) {
            return this.random.chance(
                0.45 * probability
            ) ? 1 : 0;
        }

        return 0;
    }
}