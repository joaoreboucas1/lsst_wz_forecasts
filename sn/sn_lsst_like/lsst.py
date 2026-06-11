from .pantheonplus import PantheonPlus

class lsst(PantheonPlus):
    """
    Likelihood for the Union3 & UNITY1.5 type Ia supernovae sample.

    Reference
    ---------
    https://arxiv.org/pdf/2311.12098.pdf
    """

    def configure(self):
        # DHFS note: 
        # For a total LSST positive definite cov, 
        # MUST add per-SN stat errors on top of syst cov matrix!
        self.pre_vars = self.dmb**2 

    def _read_data_file(self, data_file):
        file_cols = ['zcmb', 'zhel', 'mb', 'dmb']
        self.cols = ['zcmb', 'zhel', 'mag', 'dmb']
        self._read_cols(data_file, file_cols)
        self.zhel = self.zcmb
