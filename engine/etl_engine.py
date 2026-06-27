from extractors.base_extractor import BaseExtractor
from loaders.base_loader import BaseLoader
from models.pipeline_report import LoadSummary, PipelineReport, TransformationSummary
from transformers.cleaner import DataCleaner
from transformers.validator import DataValidator


class ETLEngine:
    """Coordinates extract, transform, validate, and load steps."""

    def __init__(
        self,
        extractor: BaseExtractor,
        cleaner: DataCleaner,
        validator: DataValidator,
        loader: BaseLoader,
    ):
        self.extractor = extractor
        self.cleaner = cleaner
        self.validator = validator
        self.loader = loader

    def run(self) -> PipelineReport:
        raw_data = self.extractor.extract()
        cleaned_data = self.cleaner.clean_dataframe(raw_data.copy())
        valid_data = self.validator.validate(cleaned_data.copy())

        load_result = self.loader.load(valid_data)

        transformation = TransformationSummary(
            raw_rows=len(raw_data),
            valid_rows=len(valid_data),
            removed_rows=len(raw_data) - len(valid_data),
        )

        load = LoadSummary(
            mode=load_result["mode"],
            attempted=load_result["attempted"],
            affected=load_result["affected"],
            skipped=load_result["skipped"],
            total_rows=load_result["total_rows"],
        )

        return PipelineReport(transformation=transformation, load=load)
