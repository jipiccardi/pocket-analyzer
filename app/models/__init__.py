__version__ = "1.0.0"
__all__ = ['conn', 'data_correct_points','connect_window','data_processing','models','workers']  # Controla qué se exporta

from .conn import SerialClient,get_available_ports,ETX,STX
from .data_correct_points import extrapole_phase,apply_extrapole,phase_correction, apply_phase_correction
from .data_processing import calculate_dut_coefficients,calculate_error_coefficients
from .models import Settings,MeasuredValue,save_measured_values_to_csv,DUT
from .workers import CalibThread