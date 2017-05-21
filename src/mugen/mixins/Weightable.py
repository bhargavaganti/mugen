from fractions import Fraction
from typing import Optional as Opt, Union, List, Any

from mugen import utility as util


class Weightable:
    """
    Mixin for weighting objects, useful for weighted sampling
    """
    weight: float = 1

    def __init__(self, *args, weight: Opt[float] = None, **kwargs):
        if weight is not None:
            self.weight = weight


class WeightableList(list):
    """
    A list of Weightables with some extra helpful properties
    """

    def __init__(self, weightables: Opt[List[Union[Weightable, List[Any]]]] = None, weights: Opt[List[float]] = None):
        """
        Parameters
        ----------
        weightables
            An arbitrarily nested irregular list of Weightables and lists of Weightables.
            e.g. [W1, W2, [W3, W4]]
             
        weights
            Weights to distribute across the weightables
        """
        super().__init__()

        if weightables is not None:
            if weights is None:
                weights = [1] * len(weightables)

            # Distribute the weights for each weightable
            for weightable, weight in zip(weightables, weights):
                if type(weightable) is list:
                    WeightableList._distribute_weight(weightable, weight)
                else:
                    weightable.weight = weight

            # Flatten weightables
            flattened_weightables = util.flatten(weightables)
            self.extend(flattened_weightables)

    @property
    def weights(self) -> List[float]:
        return [weightable.weight for weightable in self]

    @property
    def normalized_weights(self) -> List[float]:
        """
        Returns
        -------
        Weights in normalized form, in the range 0-1
        """
        weight_sum = sum(self.weights)

        return [weight / weight_sum for weight in self.weights]

    @property
    def weight_percentages(self) -> List[float]:
        """
        Returns
        -------
        Weights in percentage form, in the range 0-100
        """
        return [weight * 100 for weight in self.normalized_weights]

    @property
    def weight_fractions(self) -> List[Fraction]:
        """
        Returns
        -------
        Weights in simplest fraction form
        """
        return [util.float_to_fraction(weight) for weight in self.normalized_weights]

    @staticmethod
    def _distribute_weight(weightables: List[Union[Weightable, List[Any]]], weight: float):
        """
        Evenly distributes weight across an arbitrarily nested irregular list of weightables
        """
        split_weight = weight / len(weightables)

        for weightable in weightables:
            if type(weightable) is list:
                WeightableList._distribute_weight(weightable, split_weight)
            else:
                weightable.weight = split_weight