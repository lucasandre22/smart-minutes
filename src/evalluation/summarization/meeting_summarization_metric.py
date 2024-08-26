import time
import asyncio
import nest_asyncio
from pydantic import BaseModel, Field
from typing import List
from enum import Enum
from dataclasses import dataclass
from .template import MeetingSummarizationTemplate
from deepeval.metrics.utils import (
    construct_verbose_logs,
    trimAndLoadJson
)

@dataclass
class LLMTestCase:
    input: str | list
    actual_output: str

class ScoreType(Enum):
    ALIGNMENT = "Alignment"
    COVERAGE = "Coverage"

class SummarizationAlignmentVerdict(BaseModel):
    # yes, no, or idk
    verdict: str
    reason: str = Field(default=None)


class SummarizationCoverageVerdict(BaseModel):
    summary_verdict: str
    original_verdict: str
    question: str = Field(default=None)


class Verdict(BaseModel):
    verdicts: List[SummarizationAlignmentVerdict]


class Questions(BaseModel):
    questions: List[str]


class Answers(BaseModel):
    answers: List[str]


class Answers(BaseModel):
    answers: List[str]

class Reason(BaseModel):
    reason: str

def get_or_create_event_loop() -> asyncio.AbstractEventLoop:
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            print(
                "Event loop is already running. Applying nest_asyncio patch to allow async execution..."
            )
            nest_asyncio.apply()

        if loop.is_closed():
            raise RuntimeError
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop


class MeetingSummarizationMetric():
    def __init__(
        self,
        threshold: float = 0.5,
        n: int = 5,
        model = None,
        assessment_questions = None,
        include_reason: bool = True,
        async_mode=True,
        strict_mode: bool = False,
        verbose_mode: bool = False,
    ):
        self.threshold = 1 if strict_mode else threshold
        self.model = model
        self.using_native_model = True

        if assessment_questions is not None and len(assessment_questions) == 0:
            self.assessment_questions = None
        else:
            self.assessment_questions = assessment_questions

        self.include_reason = include_reason
        self.n = n
        self.async_mode = async_mode
        self.strict_mode = strict_mode
        self.verbose_mode = verbose_mode
        self.start_time = -1
        self.total_time_to_measure = -1

    def measure(self, test_case: LLMTestCase) -> float:
        self.start_time = time.time()
        if self.async_mode:
            loop = get_or_create_event_loop()
            loop.run_until_complete(
                self.a_measure(test_case, _show_indicator=False)
            )
        else:
            if isinstance(test_case.input, list):
                maximum_truths_from_original_text = 60
                maximum_claims_per_chapter = int(maximum_truths_from_original_text/len(test_case.input))
                self.truths_from_original_text: List[str] = self._generate_claims_from_chapters(
                    test_case.input, maximum_claims_per_chapter
                )
            else:
                self.truths_from_original_text: List[str] = self._generate_claims(test_case.input)
            self.claims_from_summary: List[str] = self._generate_claims(
                test_case.actual_output
            )
            self.coverage_verdicts: List[SummarizationCoverageVerdict] = (
                self._generate_coverage_verdicts(test_case)
            )
            self.alignment_verdicts: List[SummarizationAlignmentVerdict] = (
                self._generate_alignment_verdicts()
            )
            alignment_score = self._calculate_score(ScoreType.ALIGNMENT)
            coverage_score = self._calculate_score(ScoreType.COVERAGE)
            self.score_breakdown = {
                ScoreType.ALIGNMENT.value: alignment_score,
                ScoreType.COVERAGE.value: coverage_score,
            }
            self.score = min(alignment_score, coverage_score)
            self.reason = self._generate_reason()
            self.success = self.score >= self.threshold
            self.verbose_logs = construct_verbose_logs(
                self,
                steps=[
                    f"Truths:\n{self.truths_from_original_text}",
                    f"Summary claims:\n{self.claims_from_summary}",
                    f"Assessment Questions:\n{self.assessment_questions}",
                    f"Coverage Verdicts:\n{self.coverage_verdicts}",
                    f"Alignment Verdicts:\n{self.alignment_verdicts}",
                    f"Score: {self.score}\nReason: {self.reason}",
                ],
            )
            self.total_time_to_measure = time.time() - self.start_time
            return self.score

    async def a_measure(
        self,
        test_case: LLMTestCase,
        _show_indicator: bool = True,
    ) -> float:

        self.truths_from_original_text, self.claims_from_summary = await asyncio.gather(
            self._a_generate_claims(test_case.input),
            self._a_generate_claims(test_case.actual_output),
        )
        (
            self.coverage_verdicts,
            self.alignment_verdicts,
        ) = await asyncio.gather(
            self._a_generate_coverage_verdicts(test_case),
            self._a_generate_alignment_verdicts(),
        )
        alignment_score = self._calculate_score(ScoreType.ALIGNMENT)
        coverage_score = self._calculate_score(ScoreType.COVERAGE)
        self.score_breakdown = {
            ScoreType.ALIGNMENT.value: alignment_score,
            ScoreType.COVERAGE.value: coverage_score,
        }
        self.score = min(alignment_score, coverage_score)
        self.reason = await self._a_generate_reason()
        self.success = self.score >= self.threshold
        self.verbose_logs = construct_verbose_logs(
            self,
            steps=[
                f"Truths:\n{self.truths_from_original_text}",
                f"Claims:\n{self.claims_from_summary}",
                f"Assessment Questions:\n{self.assessment_questions}",
                f"Coverage Verdicts:\n{self.coverage_verdicts}",
                f"Alignment Verdicts:\n{self.alignment_verdicts}",
                f"Score: {self.score}\nReason: {self.reason}",
            ],
        )

        return self.score

    async def _a_generate_reason(self) -> str:
        if self.include_reason is False:
            return None

        contradictions = []
        redundancies = []
        for verdict in self.alignment_verdicts:
            if verdict.verdict.strip().lower() == "no":
                contradictions.append(verdict.reason)
            elif verdict.verdict.strip().lower() == "idk":
                redundancies.append(verdict.reason)

        questions = []
        if self.coverage_verdicts:
            for verdict in self.coverage_verdicts:
                if (
                    verdict.original_verdict.strip().lower() == "yes"
                    and verdict.summary_verdict.strip().lower() == "no"
                ):
                    questions.append(verdict.question)

        prompt: dict = MeetingSummarizationTemplate.generate_reason(
            contradictions=contradictions,
            redundancies=redundancies,
            questions=questions,
            score=format(self.score, ".2f"),
        )

        if len(questions) > 0:
            prompt += f"""Questions the original text can answer but not the summary:
{questions}

"""
        prompt += """JSON:
"""
        res = await self.model.a_generate(prompt)
        data = trimAndLoadJson(res, self)
        return data["reason"]

    def _generate_reason(self) -> str:
        if self.include_reason is False:
            return None

        contradictions = []
        redundancies = []
        for verdict in self.alignment_verdicts:
            if verdict.verdict.strip().lower() == "no":
                contradictions.append(verdict.reason)
            elif verdict.verdict.strip().lower() == "idk":
                redundancies.append(verdict.reason)

        questions = []
        if self.coverage_verdicts:
            for verdict in self.coverage_verdicts:
                if (
                    verdict.original_verdict.strip().lower() == "yes"
                    and verdict.summary_verdict.strip().lower() == "no"
                ):
                    questions.append(verdict.question)

        prompt: dict = MeetingSummarizationTemplate.generate_reason(
            contradictions=contradictions,
            redundancies=redundancies,
            questions=questions,
            score=format(self.score, ".2f"),
        )

        if len(questions) > 0:
            prompt += f"""Questions the original text can answer but not the summary:
{questions}

"""
        prompt += """JSON:
"""
        res = self.model.generate(prompt)
        data = trimAndLoadJson(res, self)
        return data["reason"]

    def _calculate_score(self, score_type: ScoreType) -> float:
        """Calculates the score of the given result

        Args:
            score_type (ScoreType): ScoreType.ALIGNMENT or ScoreType.COVERAGE

        Returns:
            float: the corresponding score value
        """
        if score_type == ScoreType.ALIGNMENT:
            total = len(self.alignment_verdicts)
            if total == 0:
                return 0
            faithfulness_count = 0
            for verdict in self.alignment_verdicts:
                # Different from the faithfulness score, this
                # penalizes 'idk' (full of fluff) summaries
                if verdict.verdict.strip().lower() == "yes":
                    faithfulness_count += 1

            score = faithfulness_count / total

        else:
            if self.assessment_questions is None:
                return 1
            total = 0
            coverage_count = 0
            for verdict in self.coverage_verdicts:
                if verdict.original_verdict.strip().lower() == "yes":
                    total += 1
                    if verdict.summary_verdict.strip().lower() == "yes":
                        coverage_count += 1

            if total == 0:
                return 0

            score = coverage_count / total

        return 0 if self.strict_mode and score < self.threshold else score

    async def _a_generate_answers(self, text: str) -> List[str]:
        prompt = MeetingSummarizationTemplate.generate_answers(
            questions=self.assessment_questions, text=text
        )
        res = await self.model.a_generate(prompt)
        data = trimAndLoadJson(res, self)
        return data["answers"]

    def _generate_answers(self, text: str) -> List[str]:
        prompt = MeetingSummarizationTemplate.generate_answers(
            questions=self.assessment_questions, text=text
        )
        res = self.model.generate(prompt)
        data = trimAndLoadJson(res, self)
        return data["answers"]

    async def _a_generate_assessment_questions(self, text: str):
        prompt = MeetingSummarizationTemplate.generate_questions(text=text, n=self.n)
        res = await self.model.a_generate(prompt)
        data = trimAndLoadJson(res, self)
        return data["questions"]

    def _generate_assessment_questions(self, text: str):
        prompt = MeetingSummarizationTemplate.generate_questions(text=text, n=self.n)
        res = self.model.generate(prompt)
        data = trimAndLoadJson(res, self)
        return data["questions"]

    async def _a_generate_coverage_verdicts(
        self, test_case: LLMTestCase
    ) -> List[SummarizationCoverageVerdict]:
        if self.assessment_questions is None:
            self.assessment_questions = (
                await self._a_generate_assessment_questions(test_case.input)
            )

        tasks = [
            self._a_generate_answers(test_case.input),
            self._a_generate_answers(test_case.actual_output),
        ]
        results = await asyncio.gather(*tasks)
        original_answers = results[0]
        summary_answers = results[1]

        if len(original_answers) != len(summary_answers):
            raise ValueError("Number of verdicts generated does not equal.")

        coverage_veridcts: List[SummarizationCoverageVerdict] = []
        for i in range(len(original_answers)):
            coverage_veridcts.append(
                SummarizationCoverageVerdict(
                    summary_verdict=summary_answers[i],
                    original_verdict=original_answers[i],
                    question=self.assessment_questions[i],
                )
            )
        return coverage_veridcts

    def _generate_coverage_verdicts(
        self, test_case: LLMTestCase
    ) -> List[SummarizationCoverageVerdict]:
        if self.assessment_questions is None:
            if isinstance(test_case.input, list):
                result = []
                for i in range(len(test_case.input)):
                    chapter_result: List[str] = self._generate_assessment_questions(
                        test_case.input[i]
                    )
                    result.extend(chapter_result)
                self.assessment_questions = result
                
            else:
                self.assessment_questions = self._generate_assessment_questions(
                    test_case.input
                )
            
        # Every answer is "yes"
        #original_answers = self._generate_answers(test_case.input)
        summary_answers = self._generate_answers(test_case.actual_output)
        
        total_questions = len(summary_answers)

        if (not isinstance(test_case.input, list) and self.n != total_questions) or (isinstance(test_case.input, list) and
                                              self.n*len(test_case.input) != total_questions):
            raise ValueError("Number of verdicts generated does not equal n.")

        coverage_veridcts: List[SummarizationCoverageVerdict] = []
        for i in range(total_questions):
            coverage_veridcts.append(
                SummarizationCoverageVerdict(
                    summary_verdict=summary_answers[i],
                    original_verdict="yes",
                    question=self.assessment_questions[i],
                )
            )

        return coverage_veridcts

    async def _a_generate_alignment_verdicts(
        self,
    ) -> List[SummarizationAlignmentVerdict]:
        if len(self.claims_from_summary) == 0:
            return []

        verdicts: List[SummarizationAlignmentVerdict] = []
        prompt = MeetingSummarizationTemplate.generate_alignment_verdicts(
            summary_claims=self.claims_from_summary, orignal_text="\n\n".join(self.truths_from_original_text)
        )
        res = await self.model.a_generate(prompt)
        data = trimAndLoadJson(res, self)
        verdicts = [
            SummarizationAlignmentVerdict(**item)
            for item in data["verdicts"]
        ]
        return verdicts

    def _generate_alignment_verdicts(
        self,
    ) -> List[SummarizationAlignmentVerdict]:
        if len(self.claims_from_summary) == 0:
            return []

        verdicts: List[SummarizationAlignmentVerdict] = []
        prompt = MeetingSummarizationTemplate.generate_alignment_verdicts(
            summary_claims=self.claims_from_summary, orignal_text="\n\n".join(self.truths_from_original_text)
        )
        res = self.model.generate(prompt)
        data = trimAndLoadJson(res, self)
        verdicts = [
            SummarizationAlignmentVerdict(**item)
            for item in data["verdicts"]
        ]
        return verdicts

    async def _a_generate_claims(self, text: str) -> List[str]:
        prompt = MeetingSummarizationTemplate.generate_claims(text=text)
        res = await self.model.a_generate(prompt)
        data = trimAndLoadJson(res, self)
        return data["claims"]

    def _generate_claims(self, text: str) -> List[str]:
        prompt = MeetingSummarizationTemplate.generate_claims(text=text)
        res = self.model.generate(prompt)
        data = trimAndLoadJson(res, self)
        return data["claims"]

    def _generate_claims_from_chapters(self, text: List, maximum_claims_per_chapter: int) -> List[str]:
        result = []
        for i in range(0, len(text)):
            prompt = MeetingSummarizationTemplate.generate_claims_for_chapter(
                chapter_text=text[i], maximum_claims=maximum_claims_per_chapter
            )
            res = self.model.generate(prompt)
            data = trimAndLoadJson(res, self)
            result.extend(data["claims"])
        return result

    def is_successful(self) -> bool:
        if self.error is not None:
            self.success = False
        else:
            try:
                self.success = self.score >= self.threshold
            except:
                self.success = False
        return self.success

    @property
    def __name__(self):
        return "MeetingSummarization"