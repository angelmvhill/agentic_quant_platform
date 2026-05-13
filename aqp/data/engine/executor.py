"""Local data-engine executor."""
from __future__ import annotations

from datetime import datetime

from aqp.data.engine.manifest import PipelineManifest
from aqp.data.engine.nodes import NodeContext, SinkNode, SourceNode, TransformNode
from aqp.data.engine.pipeline import Pipeline, PipelineRunResult
from aqp.data.engine.registry import build_node


class LocalExecutor:
    def execute(self, pipeline: Pipeline) -> PipelineRunResult:
        manifest = pipeline.manifest
        context = NodeContext(namespace=manifest.namespace, name=manifest.name)
        result = PipelineRunResult()
        try:
            source = build_node(manifest.source.name, manifest.source.kwargs)
            rows = source.read(context) if isinstance(source, SourceNode) else []
            for spec in manifest.transforms:
                node = build_node(spec.name, spec.kwargs)
                if isinstance(node, TransformNode):
                    rows = node.apply(rows, context)
            sink = build_node(manifest.sink.name, manifest.sink.kwargs)
            sink_result = sink.write(rows, context) if isinstance(sink, SinkNode) else {}
            result.sink_result = dict(sink_result or {})
            result.total_rows_written = int(result.sink_result.get("rows_written") or len(rows))
            result.tables = list(result.sink_result.get("tables") or [])
        except Exception as exc:  # noqa: BLE001
            result.errors.append(str(exc))
        finally:
            result.finished_at = datetime.utcnow()
        return result


def build_executor(_spec: PipelineManifest) -> LocalExecutor:
    return LocalExecutor()
