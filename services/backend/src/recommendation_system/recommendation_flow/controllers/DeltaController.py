from src.recommendation_system.recommendation_flow.candidate_generators.DeltaGenerator import (
    UserPreferenceGenerator, CFGenerator, PopularCategoryGenerator
)

from src.recommendation_system.recommendation_flow.candidate_generators.RandomGenerator import (
    RandomGenerator
)

from src.recommendation_system.recommendation_flow.controllers.AbstractController import (
    AbstractController,
)

from src.recommendation_system.recommendation_flow.filtering.DeltaFilter import (
    QualityFilter
)

from src.recommendation_system.recommendation_flow.model_prediction.RandomModel import (
    RandomModel
)

from src.recommendation_system.recommendation_flow.model_prediction.DeltaModel import (
    RuleBasedModel,
)

from src.recommendation_system.recommendation_flow.ranking.DeltaRanker import (
    RuleBasedRanker,
)

import time

class DeltaController(AbstractController):
    def get_content_ids(self, user_id, limit, offset, seed, starting_point):
        candidates_limit = (
            limit * 10 * 10
        )
        if user_id == 0:
            candidates, scores = RandomGenerator().get_content_ids(
                user_id, candidates_limit, offset, seed, starting_point
            )
        else:
            candidates_1, scores_1 = UserPreferenceGenerator().get_content_ids(
                user_id, candidates_limit, offset, seed, starting_point
            )
            candidates_2, scores_2 = CFGenerator().get_content_ids(
                user_id, candidates_limit, offset, seed, starting_point
            )

            candidates_3, scores_3 = PopularCategoryGenerator().get_content_ids(
                user_id, candidates_limit, offset, seed, starting_point
            )
            candidates = candidates_1 + candidates_2 + candidates_3

        filtered_candidates_scores = QualityFilter().filter_ids(
            candidates, seed, starting_point, user_id
        )

        filtered_candidates = filtered_candidates_scores.keys()
        if user_id == 0:
            predictor_model = RandomModel()
        else:
            predictor_model = RuleBasedModel()

        predictions = RuleBasedModel().predict_probabilities(
            filtered_candidates,
            user_id,
            seed=seed,
            scores={
                content_id: {"score": filtered_candidates_scores[content_id]}
                for content_id in filtered_candidates_scores
            }
        )
        rank = RuleBasedRanker().rank_ids(limit, predictions, seed, starting_point)
        return rank
