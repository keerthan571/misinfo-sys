export default class PropagationPolicy {

    static maxChildren(parent) {
        switch (parent.type) {

            case "claim":
                return 1;

            case "influencer":
                return 3;

            case "user":
                return 2;

            case "bot":
                return 1;

            default:
                return 1;
        }
    }

    // Promotion Rules
    static influencerPromotionChance() {
        return 0.20;
    }

    // Bot Rules
    static botInjectionChance(baseProbability) {
        return baseProbability;
    }

    static botSpreadChance() {
        return 0.50;
    }

    // Influencer Spread Rules
    static highInfluencerSpreadChance() {
        return 0.70;
    }

    static normalInfluencerSpreadChance() {
        return 0.60;
    }

    // User Spread Rules
    static activeUserSpreadChance() {
        return 0.60;
    }

    static normalUserSpreadChance() {
        return 0.45;
    }
}