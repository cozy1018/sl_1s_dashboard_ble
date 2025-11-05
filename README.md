# sl_1s_lead_classifier_dashboard

Repository for the Python-based dashboard to debug the single-lead embedded ventricular dysfunction project.

Connect the Silicon Labs board to a USB port, then execute vcom_with_dashboard.py . End execution with ctrl + C or by closing the plot window. If trying out again, make sure to reset the Silicon Labs board to empty the buffers.

To change the file that is being sent, change line 490 (array_to_send = ecg_long_data_normal ), the options currently are ecg_long_data_normal, ecg_long_data_PVC (external files), and ecg_data_normal, ecg_data_PVC (hardcoded in vcom_with_dasboard.py)