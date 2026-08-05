import ParameterEngine from "./ParameterEngine";
import NodeGenerator from "./NodeGenerator";
import EdgeGenerator from "./EdgeGenerator";
import InfluenceDetector from "./InfluenceDetector";
import PropagationSimulator from "./PropagationSimulator";
import ELKLayoutEngine from "./ELKLayoutEngine";

export default class GraphGenerator {

    static async generate(aiResult) {

        try {

            // STEP 1: Generate blueprint
            const blueprint =
                new ParameterEngine(aiResult)
                    .generate();

            // STEP 2: Simulate propagation
            const events =
                new PropagationSimulator(blueprint)
                    .simulate();

            // STEP 3: Generate nodes
            let nodes =
                new NodeGenerator(
                    events,
                    blueprint
                ).generate();

            // STEP 4: Generate edges
            let edges =
                new EdgeGenerator(
                    nodes,
                    blueprint
                ).generate();

            // STEP 5: Analyze influence
            const detector =
                new InfluenceDetector(
                    nodes,
                    edges,
                    blueprint
                );

            const influencers =
                detector.detect();

            const analytics =
                detector.getAnalytics();

            nodes =
                detector.getNodes();

            edges =
                detector.getEdges();

            // STEP 6: Apply ELK layout
            nodes =
                await ELKLayoutEngine.layout(
                    nodes,
                    edges
                );

            // STEP 7: Return graph
            return {
                blueprint,
                nodes,
                edges,
                influencers,
                analytics
            };

        } catch (error) {

            console.error(
                "Graph generation failed:",
                error
            );

            throw error;
        }
    }

    static async build(aiResult) {
        return this.generate(aiResult);
    }
}