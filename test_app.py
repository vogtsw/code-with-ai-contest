import pytest
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import get_rsrp_color

class TestDataProcessing:

    def test_rsrp_color_green(self):
        assert get_rsrp_color(-85) == [0, 255, 0]

    def test_rsrp_color_yellow(self):
        color = get_rsrp_color(-100)
        assert len(color) == 3
        assert color[0] > 0
        assert color[1] > 0
        assert color[2] == 0

    def test_rsrp_color_red(self):
        assert get_rsrp_color(-115) == [255, 0, 0]

    def test_rsrp_color_boundary_high(self):
        assert get_rsrp_color(-90) == [0, 255, 0]

    def test_rsrp_color_boundary_low(self):
        assert get_rsrp_color(-110) == [255, 0, 0]

    def test_rsrp_color_transition(self):
        color = get_rsrp_color(-105)
        assert color[0] > 0
        assert color[1] > 0
        assert color[0] + color[1] == 254


class TestDataLoading:

    def test_data_file_exists(self):
        assert os.path.exists("data/signal_samples.csv")

    def test_data_columns(self):
        df = pd.read_csv("data/signal_samples.csv")
        expected_columns = ['Latitude', 'Longitude', 'CellID', 'Band', 'RSRP_dBm', 'SINR_dB', 'TerminalType', 'Download_Mbps']
        assert list(df.columns) == expected_columns

    def test_data_not_empty(self):
        df = pd.read_csv("data/signal_samples.csv")
        assert len(df) > 0

    def test_data_types(self):
        df = pd.read_csv("data/signal_samples.csv")
        assert df['Latitude'].dtype in ['float64', 'float32']
        assert df['Longitude'].dtype in ['float64', 'float32']
        assert df['RSRP_dBm'].dtype in ['float64', 'float32']

    def test_rsrp_range(self):
        df = pd.read_csv("data/signal_samples.csv")
        assert df['RSRP_dBm'].min() < -70
        assert df['RSRP_dBm'].max() > -120

    def test_bands(self):
        df = pd.read_csv("data/signal_samples.csv")
        unique_bands = df['Band'].unique()
        assert len(unique_bands) >= 3
        assert 'n28' in unique_bands or 'n41' in unique_bands or 'n78' in unique_bands

    def test_terminal_types(self):
        df = pd.read_csv("data/signal_samples.csv")
        unique_terminals = df['TerminalType'].unique()
        assert len(unique_terminals) >= 2
        assert 'Smartphone' in unique_terminals


class TestDataFiltering:

    def test_filter_by_band(self):
        df = pd.read_csv("data/signal_samples.csv")
        filtered = df[df['Band'] == 'n78']
        assert len(filtered) > 0
        assert all(filtered['Band'] == 'n78')

    def test_filter_by_rsrp_range(self):
        df = pd.read_csv("data/signal_samples.csv")
        filtered = df[(df['RSRP_dBm'] >= -90) & (df['RSRP_dBm'] <= -80)]
        assert len(filtered) > 0
        assert all(filtered['RSRP_dBm'] >= -90)
        assert all(filtered['RSRP_dBm'] <= -80)

    def test_filter_by_terminal_type(self):
        df = pd.read_csv("data/signal_samples.csv")
        filtered = df[df['TerminalType'] == 'CPE']
        assert len(filtered) > 0
        assert all(filtered['TerminalType'] == 'CPE')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
