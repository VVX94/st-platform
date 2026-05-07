from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from st_platform.tasks import TaskType
from st_platform.workflows import create_platform_service


service = create_platform_service(project_root=str(ROOT))
result = service.run(
    task_type=TaskType.DOMAIN_DETECTION,
    algorithm_id="mock-domain",
    data=service.build_demo_dataset(),
    parameters={"resolution": 1.0},
)

print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))

