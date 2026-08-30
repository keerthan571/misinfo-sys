import PropagationPolicy from "./PropagationPolicy";

export default class BranchAllocator {

    constructor(simulation, random) {
        this.simulation = simulation;
        this.random = random;
    }

    allocate(parent, remaining) {

        if (remaining <= 0) {
            return 0;
        }

        const influence =
            Number(parent.influence) || 0;

        const spreadProbability =
            Math.max(
                0,
                Math.min(
                    1,
                    Number(
                        this.simulation.spreadProbability
                    ) || 0
                )
            );

        let children = 0;

        switch (parent.type) {

            // =========================================
            // ORIGINAL CLAIM
            // =========================================

            case "claim":

                children = 1;

                break;


            // =========================================
            // INFLUENCER
            // =========================================

            case "influencer":

                if (influence >= 70) {

                    children =
                        this.random.chance(
                            0.75
                        )
                            ? 4
                            : 3;

                } else if (influence >= 50) {

                    children =
                        this.random.chance(
                            0.70
                        )
                            ? 3
                            : 2;

                } else {

                    children = 2;
                }

                /*
                 * Strong spread probability can add
                 * one additional propagation branch.
                 */
                if (
                    spreadProbability >= 0.70 &&
                    children < 4 &&
                    this.random.chance(
                        spreadProbability * 0.35
                    )
                ) {
                    children++;
                }

                break;


            // =========================================
            // BOT
            // =========================================

            case "bot":

                children =
                    this.random.chance(
                        0.65
                    )
                        ? 2
                        : 1;

                break;


            // =========================================
            // NORMAL USER
            // =========================================

            case "user":

                if (influence >= 40) {

                    children =
                        this.random.chance(
                            0.70
                        )
                            ? 3
                            : 2;

                } else if (influence >= 25) {

                    children =
                        this.random.chance(
                            0.65
                        )
                            ? 2
                            : 1;

                } else if (influence >= 12) {

                    /*
                     * Previously this level had a
                     * 60% chance of terminating.
                     *
                     * Keep at least one child for
                     * meaningful propagation.
                     */
                    children =
                        this.random.chance(
                            0.75
                        )
                            ? 2
                            : 1;

                } else {

                    /*
                     * Low influence should still be
                     * capable of one final cascade.
                     */
                    children =
                        this.random.chance(
                            0.55 +
                            spreadProbability * 0.20
                        )
                            ? 1
                            : 0;
                }

                break;


            default:

                children = 0;
        }


        /*
         * Never create more nodes than remain.
         */
        children =
            Math.min(
                children,
                remaining
            );


        return children;
    }


    /*
     * Kept as a public helper for compatibility.
     *
     * PropagationSimulator currently uses allocate(),
     * so this method is not part of the main path.
     */
    allocateUserChildren(parent) {

        const influence =
            Number(parent.influence) || 0;

        const probability =
            Math.max(
                0,
                Math.min(
                    1,
                    Number(
                        this.simulation.spreadProbability
                    ) || 0
                )
            );

        const decay =
            Math.max(
                0,
                Math.min(
                    1,
                    Number(
                        this.simulation.cascadeDecay
                    ) || 0
                )
            );

        if (influence >= 60) {

            return this.random.chance(
                0.70 * (1 - decay)
            )
                ? 3
                : 2;
        }

        if (influence >= 40) {

            return this.random.chance(
                0.60 * probability
            )
                ? 2
                : 1;
        }

        if (influence >= 20) {

            return this.random.chance(
                0.45 * probability
            )
                ? 1
                : 0;
        }

        return 0;
    }
}