from sae.models.canvas import Canvas, Connection, NodeInstance
from sae.simulation.engine import SimulationEngine


def test_load_balancer_distributes_requests():
    canvas = Canvas(
        nodes=[
            NodeInstance(
                id="user1",
                type="user",
                label="Usuario",
                position={"x": 0, "y": 0},
                parameters={"requests_per_second": 100},
            ),
            NodeInstance(
                id="lb1",
                type="load_balancer",
                label="LB",
                position={"x": 200, "y": 0},
                parameters={"algorithm": "round_robin"},
            ),
            NodeInstance(
                id="ws1",
                type="web_server",
                label="Web 1",
                position={"x": 400, "y": -50},
                parameters={"workers": 4, "process_time_ms": 10},
            ),
            NodeInstance(
                id="ws2",
                type="web_server",
                label="Web 2",
                position={"x": 400, "y": 50},
                parameters={"workers": 4, "process_time_ms": 10},
            ),
        ],
        connections=[
            Connection(id="c1", source="user1", source_handle="requests", target="lb1", target_handle="in"),
            Connection(id="c2", source="lb1", source_handle="out", target="ws1", target_handle="in"),
            Connection(id="c3", source="lb1", source_handle="out", target="ws2", target_handle="in"),
        ],
    )

    engine = SimulationEngine(canvas)
    engine.start(duration=2.0, speed=10.0)

    while engine.is_running:
        engine.step(dt=0.5)

    lb_metrics = engine.metrics.nodes["lb1"]
    dist = lb_metrics.extra.get("distribution", {})
    assert len(dist) == 2
    assert engine.metrics.total_requests > 0
