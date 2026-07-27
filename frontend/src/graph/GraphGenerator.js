import ParameterEngine from "./ParameterEngine";
import NodeGenerator from "./NodeGenerator";
import EdgeGenerator from "./EdgeGenerator";
import InfluenceDetector from "./InfluenceDetector";

export default class GraphGenerator {
  /**
   * Public API
   * Generates the complete graph from backend response.
   */
  static generate(apiResponse) {
    // STEP 1: Extract graph parameters
    const parameters = ParameterEngine.buildParameters(apiResponse);

    // STEP 2: Generate nodes
    const nodeGenerator = new NodeGenerator(parameters);
    const nodes = nodeGenerator.generate();

    // STEP 3: Generate edges
    const edgeGenerator = new EdgeGenerator(nodes, parameters);
    const edges = edgeGenerator.generate();

    // STEP 4: Detect influencers
    const detector = new InfluenceDetector(nodes, edges);
    const influencers = detector.detect();

    // STEP 5: Build analytics
    const analytics = detector.getAnalytics();

    return {
      nodes,
      edges,
      influencers,
      analytics,
      parameters,
    };
  }

  /**
   * Convenience wrapper for React pages.
   */
  static build(apiResponse) {
    return this.generate(apiResponse);
  }
}