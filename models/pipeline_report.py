from dataclasses import dataclass


@dataclass
class TransformationSummary:
    raw_rows: int
    valid_rows: int
    removed_rows: int


@dataclass
class LoadSummary:
    mode: str
    attempted: int
    affected: int
    skipped: int
    total_rows: int


@dataclass
class PipelineReport:
    transformation: TransformationSummary
    load: LoadSummary
