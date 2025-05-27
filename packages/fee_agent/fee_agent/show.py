from llama_index.utils.workflow import draw_all_possible_flows

from fee_agent.main import DDoSDetectionWorkflow

if __name__ == "__main__":
    draw_all_possible_flows(DDoSDetectionWorkflow(), "show.html")
    print("Workflow diagram saved to show.html")
