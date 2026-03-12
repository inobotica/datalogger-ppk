# get today's date in YYYY-MM-DD format #
NOW="$(date +"%Y-%m-%d_%H%M%S")"
 
# Append date to error log file 
log_file="/home/pi/datalogger-ppk/logs_runtime/${NOW}_run.log"
error_file="/home/pi/datalogger-ppk/logs_runtime/${NOW}_err.log"
# Now run command1 and send errors to the $log_file
#python /home/pi/datalogger-ppk/main.py > "$log_file" 2>&1
python /home/pi/datalogger-ppk/main.py > "$log_file" 2> "$error_file"