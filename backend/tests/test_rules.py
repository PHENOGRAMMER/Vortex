from backend.services.routing_rules import RoutingRules
from backend.models.task_type import TaskType

for task in TaskType:

    print(task)

    print(RoutingRules.get(task))

    print("-" * 40)