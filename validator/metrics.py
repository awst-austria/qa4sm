import numpy as np
import pytesmo.metrics as metrics
from pytesmo.validation_framework.metric_calculators import BasicMetrics


class EssentialMetrics(BasicMetrics):
    """
    Basic Metrics plus ubrmsd and RSS, as per
    https://www.awst.at/qa4sm-jira/browse/QA4SM-58
    """

    def __init__(self, other_name='k1',
                 calc_tau=False):

        super(EssentialMetrics, self).__init__(other_name=other_name,
                                                  calc_tau=calc_tau)
        self.result_template.update({'urmsd': np.float32([np.nan]),
                                     'RSS': np.float32([np.nan]),})

        if not calc_tau:
            self.result_template.pop('tau', None)
            self.result_template.pop('p_tau', None)

    def calc_metrics(self, data, gpi_info):
        dataset = super(EssentialMetrics, self).calc_metrics(data, gpi_info)
        if len(data) < 10:
            return dataset
        x, y = data['ref'].values, data[self.other_name].values

        urmsd = metrics.ubrmsd(x,y)
        RSS = metrics.RSS(x,y)

        dataset['urmsd'][0] = urmsd
        dataset['RSS'][0] = RSS

        return dataset
