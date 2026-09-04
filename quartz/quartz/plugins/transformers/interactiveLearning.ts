import { QuartzTransformerPlugin } from "../types"
// @ts-ignore
import script from "../../components/scripts/interactive-learning.inline"

export const InteractiveLearning: QuartzTransformerPlugin = () => {
  return {
    name: "InteractiveLearning",
    externalResources() {
      return {
        js: [
          {
            loadTime: "afterDOMReady",
            contentType: "inline",
            script: script,
          },
        ],
      }
    },
  }
}
