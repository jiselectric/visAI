from typing import Any, Counter, Dict, List

from utils.file_operation import save_json_data


def chunk_list(lst: List[Any], batch_size: int):
    """Split a list into batches of specified size"""
    for i in range(0, len(lst), batch_size):
        yield lst[i : i + batch_size]


def generate_dataset_summary(state: Dict[str, Any]) -> Dict[str, Any]:
    """Generate comprehensive summary of dataset attributes and return updated state"""
    dataset_info = state.get("dataset_info", {})
    dataset_rows = dataset_info.get("rows", [])
    attributes = dataset_info.get("attributes", [])

    if not isinstance(dataset_rows, list):
        raise ValueError("Rows must be a list")
    if not isinstance(attributes, list):
        raise ValueError("Attributes must be a list")

    summaries = {}
    for attribute in attributes:
        values = [row.get(attribute, None) for row in dataset_rows if attribute in row]
        values = [v for v in values if v is not None]  # Remove nulls

        all_examples = []
        counter = Counter()

        batches = chunk_list(values, batch_size=10)
        for batch in batches:
            counter.update(batch)
            all_examples.extend(batch)

        # Deduplicate and truncate to 10 representative examples
        unique_examples = []
        seen = set()
        for v in all_examples:
            if v not in seen:
                seen.add(v)
                unique_examples.append(v)
            if len(unique_examples) == 10:
                break

        # Final summary for the column
        summaries[attribute] = {
            "column_name": attribute,
            "examples": unique_examples,
            "unique_value_count": len(set(values)),
            "top_frequencies": dict(counter.most_common(5)),
        }

    # Save dataset summary
    output_dir = "./datasets"
    save_json_data(summaries, "00_dataset_summary.json", output_dir)

    # Return updated state with dataset_summary added
    updated_state = state.copy()
    updated_state["dataset_summary"] = summaries
    return updated_state
