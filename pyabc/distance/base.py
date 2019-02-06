from abc import ABC, abstractmethod
from typing import List, Callable
import json

from ..sampler import Sampler


class Distance(ABC):
    """
    Abstract base class for distance objects.

    Any object that computes the similarity between observed and simulated data
    should inherit from this class.
    """

    def __init__(self):
        """
        Default constructor.
        """
        pass

    def initialize(
            self,
            t: int,
            get_sum_stats: Callable[[], List[dict]],
            x_0: dict):
        """
        This method is called by the ABCSMC framework before the first
        use of the distance (at the beginning of ABCSMC.run()),
        and can be used to calibrate it to the statistics of the samples.

        The default is to do nothing.
        
        Parameters
        ----------

        t: int
            Time point for which to initialize the distance.

        get_sum_stats: Callable[[], List[dict]]
            Returns on command the initial summary statistics.

        x_0: dict
            The observed summary statistics.
        """

    def configure_sampler(
            self,
            sampler: Sampler):
        """
        This is called by the ABCSMC class and gives the distance
        the opportunity to configure the sampler.
        For example, the distance might request the sampler to
        also return rejected particles in order to adapt the
        distance to the statistics of the sample.
        The method is called by the ABCSMC framework before the first
        used of the distance (at the beginning of ABCSMC.run()), after
        initialize().
        
        The default is to do nothing.

        Parameters
        ----------

        sampler: Sampler
            The sampler used in ABCSMC.
        """

    def update(
            self,
            t: int,
            sum_stats: List[dict]) -> bool:
        """
        Update the distance for the upcoming generation t.

        The default is to do nothing.

        Parameters
        ----------

        t: int
            Time point for which to update the distance.

        sum_stats: List[dict]
            List of all summary statistics from the finished generation
            that should be used to update the distance.

        Returns
        -------

        is_updated: bool
            Whether the distance has changed compared to beforehand.
            Depending on the result, the population needs to be updated
            in ABCSMC before preparing the next generation.
            Defaults to False.
        """
        return False

    @abstractmethod
    def __call__(
            self,
            x: dict,
            x_0: dict,
            t: int = None,
            par: dict = None) -> float:
        """
        Evaluate at time point t the distance of the summary statistics of
        the data simulated for the tentatively sampled particle to those of
        the observed data.

        Abstract method. This method has to be overwritten by
        all concrete implementations.

        Parameters
        ----------

        x: dict
            Summary statistics of the data simulated for the tentatively
            sampled parameter.

        x_0: dict
            Summary statistics of the observed data.

        t: int
            Time point at which to evaluate the distance.

        par: dict
            The parameters used to create the summary statistics x. These
            can be required by some distance functions.

        Returns
        -------

        distance: float
            Quantifies the distance between the summary statistics of the
            data simulated for the tentatively sampled particle and of the
            observed data.
        """

    def get_config(self) -> dict:
        """
        Return configuration of the distance.

        Returns
        -------

        config: dict
            Dictionary describing the distance.
        """
        return {"name": self.__class__.__name__}

    def to_json(self) -> str:
        """
        Return JSON encoded configuration of the distance.

        Returns
        -------

        json_str: str:
            JSON encoded string describing the distance.
            The default implementation is to try to convert the dictionary
            returned by ``get_config``.
        """
        return json.dumps(self.get_config())


class NoDistance(Distance):
	"""
	Implements a kind of null object as distance function.
	
	This can be used as a dummy distance function if e.g. integrated modeling
	is used.

	.. note::
        THis distance function cannot be evaluated, so currently it is in
        particular not possible to use an epsilon threshold which requires
        initialization, because during initialization the distance function is
        invoked directly and not via the acceptor as usual. Conceptually, this
        would be possible and can be implemented on request.
    """
    
    def __init__(self):
		super().__init__()
	
	def __call__(
			self,
			x: dict,
			x_0: dict,
			t: int = None,
			par: dict = None) -> float:
		raise Exception(
			f"{self.__class__.__name__} is not intended to be called.")


class SimpleFunctionDistance(Distance):
    """
    This is a wrapper around a simple function which calculates the distance.
    If a function is passed to the ABCSMC class, then it is converted to
    an instance of the SimpleFunctionDistance class.

    Parameters
    ----------

    function: Callable[[dict, dict], float]
        A Callable accepting two parameters, namely summary statistics x and
        x_0, and returning the distance between both.
    """

    def __init__(self,
                 function):
        super().__init__()
        self.function = function

    def __call__(self,
                 x: dict,
                 x_0: dict,
                 t: int = None,
                 par: dict = None) -> float:
        return self.function(x, x_0)

    def get_config(self):
        conf = super().get_config()
        # try to get the function name
        try:
            conf["name"] = self.function.__name__
        except AttributeError:
            try:
                conf["name"] = self.function.__class__.__name__
            except AttributeError:
                pass
        return conf


def to_distance(maybe_distance):
    """

    Parameters
    ----------
    maybe_distance: either a Callable, which takes two arguments, or
    a Distance instance.

    Returns
    -------
    
    a Distance instance.
    """

    if maybe_distance is None:
        return NoDistance()

    if isinstance(maybe_distance_function, Comparator):
        return maybe_distance_function

    return SimpleFunctionDistance(maybe_distance_function)
	